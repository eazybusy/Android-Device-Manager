"""
diagnostic.py — Android Device Manager  ·  სრული დიაგნოსტიკა
გაუშვი:  python diagnostic.py
"""

import sys
import os
import subprocess
import shutil
import threading
import time
import tkinter as tk
import customtkinter as ctk

#  make sure project imports work regardless of cwd 
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from config.theme import *

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# 
#  Low-level ADB helpers (verbose versions — return full detail)
# 

def _find_adb() -> str:
    found = shutil.which("adb")
    if found:
        return found
    candidates = (
        [
            os.path.join(os.environ.get("LOCALAPPDATA", ""),
                         "Android", "Sdk", "platform-tools", "adb.exe"),
            r"C:\platform-tools\adb.exe",
            r"C:\Android\platform-tools\adb.exe",
        ] if sys.platform == "win32" else [
            "/usr/local/bin/adb",
            "/opt/homebrew/bin/adb",
            os.path.expanduser("~/Library/Android/sdk/platform-tools/adb"),
            os.path.expanduser("~/Android/Sdk/platform-tools/adb"),
            "/usr/bin/adb",
        ]
    )
    for p in candidates:
        if os.path.isfile(p):
            return p
    return "adb"


def _run_raw(cmd: list[str]) -> tuple[str, str, int]:
    """Run adb command, return (stdout, stderr, returncode)."""
    adb = _find_adb()
    full = [adb] + cmd
    kw = {"creationflags": subprocess.CREATE_NO_WINDOW} if sys.platform == "win32" else {}
    try:
        r = subprocess.run(full, capture_output=True, text=True, timeout=15, **kw)
        return r.stdout.strip(), r.stderr.strip(), r.returncode
    except FileNotFoundError:
        return "", f"ADB ვერ მოიძებნა: '{adb}'", -1
    except subprocess.TimeoutExpired:
        return "", "Timeout (15 s) — ტელეფონი არ პასუხობს", -1
    except Exception as e:
        return "", str(e), -1


# 
#  Test definitions
# 

DUMMY_APK     = os.path.join(ROOT, "test_dummy.apk")
DUMMY_PKG     = "com.example.testapp"
DUMMY_ACTION  = "com.example.DIAG_TEST"

def _make_dummy_apk():
    """Touch a fake APK so the install path is testable."""
    if not os.path.exists(DUMMY_APK):
        with open(DUMMY_APK, "wb") as f:
            f.write(b"PK\x03\x04")   # minimal ZIP header


def _tests() -> list[dict]:
    """
    Returns ordered list of test specs.
    Each spec: {id, label, group, fn}
    fn() → (status, command_shown, stdout, stderr, explanation)
    status: 'ok' | 'fail' | 'warn'
    """

    #  helper to build a broadcast command string 
    def bc_cmd(action, extras):
        parts = ["adb", "shell", "am", "broadcast", "-a", action]
        for k, v in extras.items():
            parts += ["--es", k, str(v)]
        return " ".join(parts)

    #  1. ADB BINARY 
    def t_adb_binary():
        adb = _find_adb()
        exists = os.path.isfile(adb) or shutil.which("adb") is not None
        out, err, rc = _run_raw(["version"])
        if "Android Debug Bridge" in out:
            return ("ok", f"which adb  →  {adb}", out.splitlines()[0], "", "")
        return ("fail",
                f"which adb  →  {adb}",
                out, err,
                "ADB არ არის დაინსტალირებული ან PATH-ში არ არის.\n"
                "გადმოწერე: https://developer.android.com/tools/releases/platform-tools")

    #  2. DEVICE CONNECTED 
    def t_device():
        out, err, rc = _run_raw(["devices"])
        lines = [l for l in out.splitlines()[1:] if l.strip()]
        authorized  = [l for l in lines if "device" in l and "unauthorized" not in l]
        unauthorized = [l for l in lines if "unauthorized" in l]
        offline      = [l for l in lines if "offline" in l]

        if authorized:
            return ("ok", "adb devices", out, "", "")
        if unauthorized:
            return ("warn", "adb devices", out, "",
                    "ტელეფონი ჩართულია, მაგრამ ავტორიზაცია არ არის.\n"
                    "ტელეფონზე გაჩნდა dialog — \"Allow USB Debugging\" — დაადასტურე.")
        if offline:
            return ("fail", "adb devices", out, "",
                    "ტელეფონი offline-შია.  სცადე:\n"
                    "  adb kill-server\n  adb start-server\nან USB კაბელი ხელახლა ჩართე.")
        return ("fail", "adb devices", out, err,
                "მოწყობილობა ვერ მოიძებნა.\n"
                "• USB Debugging ჩართულია ტელეფონზე?\n"
                "• USB კაბელი მხოლოდ დატენვის რეჟიმში ხომ არ არის?")

    #  3. ADB SHELL 
    def t_shell():
        out, err, rc = _run_raw(["shell", "echo", "DIAG_OK"])
        if "DIAG_OK" in out:
            return ("ok", "adb shell echo DIAG_OK", out, "", "")
        return ("fail", "adb shell echo DIAG_OK", out, err,
                "Shell ბრძანება ვერ შესრულდა — ADB კავშირი სრულად არ მუშაობს.")

    #  4. APK INSTALL 
    def t_install_apk():
        _make_dummy_apk()
        cmd_str = f"adb install -r {DUMMY_APK}"
        out, err, rc = _run_raw(["install", "-r", DUMMY_APK])
        if "Success" in out:
            return ("ok", cmd_str, out, "", "")
        if "INSTALL_FAILED_INVALID_APK" in out + err:
            return ("warn", cmd_str, out, err,
                    "სატესტო APK არასწორია (ეს ნორმალურია) — ADB install ბრძანება კი მუშაობს!\n"
                    "რეალური APK-ს ინსტალაცია იმუშავებს.")
        if "INSTALL_FAILED_USER_RESTRICTED" in out + err:
            return ("fail", cmd_str, out, err,
                    "ტელეფონი ბლოკავს გარე წყაროებიდან ინსტალაციას.\n"
                    "Settings → Security → Install Unknown Apps → ჩართე.")
        if "no devices" in err.lower() or "device not found" in err.lower():
            return ("fail", cmd_str, out, err,
                    "ტელეფონი არ არის შეერთებული — #2 ტესტი ჯერ გაიარე.")
        return ("fail", cmd_str, out, err,
                "APK ინსტალაცია ვერ მოხდა — ზემოთ მოცემული შეცდომა იხილე.")

    #  5. BROADCAST — APN 
    def t_broadcast_apn():
        extras = {"apn_name": "DIAG_TEST", "apn": "test.apn",
                  "mcc": "999", "mnc": "99", "proxy": "", "port": ""}
        cmd = bc_cmd("com.example.SET_APN", extras)
        out, err, rc = _run_raw([
            "shell", "am", "broadcast", "-a", "com.example.SET_APN",
            "--es", "apn_name", "DIAG_TEST",
            "--es", "apn", "test.apn",
            "--es", "mcc", "999",
            "--es", "mnc", "99",
        ])
        if "Broadcast completed" in out or "result=0" in out:
            return ("ok", cmd, out, "", "")
        if "result=-1" in out:
            return ("warn", cmd, out, err,
                    "Broadcast გაიგზავნა, მაგრამ მიმღები App არ პასუხობს (result=-1).\n"
                    "ეს ნიშნავს: com.example.SET_APN BroadcastReceiver დაარეგისტრირე APK-ში.")
        if "no devices" in err.lower():
            return ("fail", cmd, out, err, "ტელეფონი არ არის შეერთებული.")
        return ("fail", cmd, out, err,
                "Broadcast ვერ გაიგზავნა.\nშეამოწმე ADB კავშირი (#2, #3 ტესტი).")

    #  6. BROADCAST — API 
    def t_broadcast_api():
        cmd = bc_cmd("com.example.SET_API",
                     {"ip": "192.168.1.1", "port": "8080", "key": "TEST_KEY"})
        out, err, rc = _run_raw([
            "shell", "am", "broadcast", "-a", "com.example.SET_API",
            "--es", "ip", "192.168.1.1", "--es", "port", "8080", "--es", "key", "TEST_KEY",
        ])
        if "Broadcast completed" in out or "result=0" in out:
            return ("ok", cmd, out, "", "")
        if "result=-1" in out:
            return ("warn", cmd, out, err,
                    "Broadcast გაიგზავნა — მიმღები App-ის Receiver-ი უნდა მოაწყო.")
        return ("fail", cmd, out, err, "Broadcast ვერ გაიგზავნა.")

    #  7. BROADCAST — CAMERA 
    def t_broadcast_camera():
        cmd = bc_cmd("com.example.SET_CAMERA",
                     {"resolution": "1920x1080", "fps": "30", "flash": "Auto"})
        out, err, rc = _run_raw([
            "shell", "am", "broadcast", "-a", "com.example.SET_CAMERA",
            "--es", "resolution", "1920x1080", "--es", "fps", "30", "--es", "flash", "Auto",
        ])
        if "Broadcast completed" in out or "result=0" in out:
            return ("ok", cmd, out, "", "")
        if "result=-1" in out:
            return ("warn", cmd, out, err,
                    "Broadcast გაიგზავნა — App-ის Receiver-ი SET_CAMERA-ზე უნდა მოუსმინოს.")
        return ("fail", cmd, out, err, "Broadcast ვერ გაიგზავნა.")

    #  8. BROADCAST — WEBVIEW 
    def t_broadcast_webview():
        cmd = bc_cmd("com.example.SET_WEBVIEW",
                     {"url": "https://test.local", "js": "True",
                      "cookies": "True", "cache": "LOAD_DEFAULT"})
        out, err, rc = _run_raw([
            "shell", "am", "broadcast", "-a", "com.example.SET_WEBVIEW",
            "--es", "url", "https://test.local",
            "--es", "js", "True", "--es", "cookies", "True",
            "--es", "cache", "LOAD_DEFAULT",
        ])
        if "Broadcast completed" in out or "result=0" in out:
            return ("ok", cmd, out, "", "")
        if "result=-1" in out:
            return ("warn", cmd, out, err,
                    "Broadcast გაიგზავნა — App-ს SET_WEBVIEW Receiver-ი სჭირდება.")
        return ("fail", cmd, out, err, "Broadcast ვერ გაიგზავნა.")

    #  9. BROADCAST — APP SETTINGS 
    def t_broadcast_app_settings():
        cmd = bc_cmd("com.example.SET_PREF",
                     {"package": DUMMY_PKG, "prefKey": "diag_key", "prefValue": "diag_val"})
        out, err, rc = _run_raw([
            "shell", "am", "broadcast", "-a", "com.example.SET_PREF",
            "--es", "package", DUMMY_PKG,
            "--es", "prefKey", "diag_key",
            "--es", "prefValue", "diag_val",
        ])
        if "Broadcast completed" in out or "result=0" in out:
            return ("ok", cmd, out, "", "")
        if "result=-1" in out:
            return ("warn", cmd, out, err,
                    "Broadcast გაიგზავნა — App-ს SET_PREF Receiver-ი სჭირდება.")
        return ("fail", cmd, out, err, "Broadcast ვერ გაიგზავნა.")

    #  10. SETTINGS PUT — SLEEP 
    def t_settings_sleep():
        cmd = "adb shell settings put system screen_off_timeout 30000"
        out, err, rc = _run_raw(["shell", "settings", "put",
                                  "system", "screen_off_timeout", "30000"])
        if rc == 0 and not err:
            verify, _, _ = _run_raw(["shell", "settings", "get",
                                      "system", "screen_off_timeout"])
            return ("ok", cmd, f"set OK  →  verify: {verify}", "", "")
        if "permission" in (out + err).lower():
            return ("fail", cmd, out, err,
                    "ნებართვა არ არის — 'settings put' საჭიროებს WRITE_SETTINGS.\n"
                    "ეს ნორმალურია სტანდარტული ADB-სთვის Android 8+.\n"
                    "გამოსავალი: App-ი WRITE_SETTINGS ნებართვით.")
        return ("fail", cmd, out, err, "Sleep timeout ვერ დაყენდა.")

    #  11. SETTINGS PUT — DEVICE NAME 
    def t_settings_device_name():
        cmd = "adb shell settings put global device_name DIAG_TEST"
        out, err, rc = _run_raw(["shell", "settings", "put",
                                  "global", "device_name", "DIAG_TEST"])
        if rc == 0 and not err:
            verify, _, _ = _run_raw(["shell", "settings", "get",
                                      "global", "device_name"])
            return ("ok", cmd, f"set OK  →  verify: {verify}", "", "")
        return ("fail", cmd, out, err,
                "Device name ვერ დაყენდა.\nსაჭიროა WRITE_SECURE_SETTINGS ნებართვა.")

    #  12. PACKAGE LIST — verify target app installed 
    def t_package_exists():
        cmd = f"adb shell pm list packages {DUMMY_PKG}"
        out, err, rc = _run_raw(["shell", "pm", "list", "packages", DUMMY_PKG])
        if DUMMY_PKG in out:
            return ("ok", cmd, out, "", f"{DUMMY_PKG} ტელეფონზე დაინსტალირებულია")
        return ("warn", cmd, out, err,
                f"{DUMMY_PKG} ტელეფონზე ვერ მოიძებნა.\n"
                "Broadcast-ები გაიგზავნება, მაგრამ App ვერ მიიღებს —\n"
                "ჯერ APK დააინსტალირე (App გვერდი → Install APK).")

    return [
        {"id":  1, "group": "ADB",        "label": "ADB binary / ვერსია",          "fn": t_adb_binary},
        {"id":  2, "group": "ADB",        "label": "მოწყობილობა შეერთებულია",       "fn": t_device},
        {"id":  3, "group": "ADB",        "label": "Shell კავშირი",                  "fn": t_shell},
        {"id":  4, "group": "App",        "label": "APK ინსტალაცია",                "fn": t_install_apk},
        {"id":  5, "group": "Network",    "label": "Broadcast → SET_APN",           "fn": t_broadcast_apn},
        {"id":  6, "group": "Network",    "label": "Broadcast → SET_API",           "fn": t_broadcast_api},
        {"id":  7, "group": "Camera",     "label": "Broadcast → SET_CAMERA",        "fn": t_broadcast_camera},
        {"id":  8, "group": "WebView",    "label": "Broadcast → SET_WEBVIEW",       "fn": t_broadcast_webview},
        {"id":  9, "group": "Settings",   "label": "Broadcast → SET_PREF",          "fn": t_broadcast_app_settings},
        {"id": 10, "group": "Settings",   "label": "settings put → Sleep Timeout",  "fn": t_settings_sleep},
        {"id": 11, "group": "Settings",   "label": "settings put → Device Name",    "fn": t_settings_device_name},
        {"id": 12, "group": "App",        "label": "APK დაინსტალირებულია თუ არა",  "fn": t_package_exists},
    ]


# 
#  GUI
# 

STATUS_COLOR = {"ok": GREEN, "fail": RED, "warn": YELLOW, "pending": TEXT_MUTED}
STATUS_ICON  = {"ok": "[OK]", "fail": "[FAIL]", "warn": "[WARN]",  "pending": ""}
GROUP_ICONS  = {
    "ADB": "", "App": "", "Network": "",
    "Camera": "", "WebView": "", "Settings": "",
}


class DiagWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Diagnostic — Android Device Manager")
        self.geometry("980x720")
        self.minsize(860, 600)
        self.configure(fg_color=BG_DARK)

        self._tests   = _tests()
        self._rows    = {}   # id → {status_lbl, detail_frame, ...}
        self._running = False

        self._build()

    #  Layout 

    def _build(self):
        # Top bar
        top = ctk.CTkFrame(self, fg_color=BG_PANEL, height=56, corner_radius=0)
        top.pack(fill="x")
        top.pack_propagate(False)

        ctk.CTkLabel(
            top, text="Diagnostic Tool",
            font=ctk.CTkFont(size=18, weight="bold"), text_color=TEXT,
        ).pack(side="left", padx=20)

        self._run_btn = ctk.CTkButton(
            top, text="  Run All Tests", width=160, height=36,
            corner_radius=R_BTN, fg_color=ACCENT, hover_color=ACCENT_DARK,
            font=ctk.CTkFont(size=FONT_BODY, weight="bold"),
            command=self._start_tests,
        )
        self._run_btn.pack(side="right", padx=20)

        self._export_btn = ctk.CTkButton(
            top, text="Export Log", width=130, height=36,
            corner_radius=R_BTN, fg_color="transparent",
            border_width=1, border_color=BORDER,
            hover_color=BG_HOVER, text_color=TEXT_LABEL,
            font=ctk.CTkFont(size=FONT_BODY),
            command=self._export,
        )
        self._export_btn.pack(side="right", padx=(0, 8))

        self._summary_lbl = ctk.CTkLabel(
            top, text="", font=ctk.CTkFont(size=FONT_SMALL), text_color=TEXT_MUTED,
        )
        self._summary_lbl.pack(side="right", padx=16)

        # Body — left: test list | right: detail panel
        body = ctk.CTkFrame(self, fg_color=BG_DARK)
        body.pack(fill="both", expand=True)

        # Left list
        left = ctk.CTkScrollableFrame(
            body, width=340, fg_color=BG_PANEL, corner_radius=0,
            scrollbar_button_color=BORDER, scrollbar_button_hover_color=ACCENT,
        )
        left.pack(side="left", fill="y")

        ctk.CTkLabel(
            left, text="TESTS",
            font=ctk.CTkFont(size=FONT_MICRO, weight="bold"), text_color=TEXT_MUTED,
        ).pack(anchor="w", padx=16, pady=(20, 6))

        prev_group = None
        for t in self._tests:
            if t["group"] != prev_group:
                prev_group = t["group"]
                ctk.CTkLabel(
                    left,
                    text=f"  {t['group'].upper()}",
                    font=ctk.CTkFont(size=FONT_MICRO, weight="bold"),
                    text_color=TEXT_MUTED,
                ).pack(anchor="w", padx=16, pady=(14, 2))

            row_frame = ctk.CTkFrame(left, fg_color="transparent", cursor="hand2")
            row_frame.pack(fill="x", padx=10, pady=1)

            icon_lbl = ctk.CTkLabel(
                row_frame, text=STATUS_ICON["pending"], width=22,
                font=ctk.CTkFont(size=14), text_color=STATUS_COLOR["pending"],
            )
            icon_lbl.pack(side="left", padx=(8, 6))

            name_lbl = ctk.CTkLabel(
                row_frame, text=t["label"], anchor="w",
                font=ctk.CTkFont(size=FONT_BODY), text_color=TEXT_LABEL,
            )
            name_lbl.pack(side="left", fill="x", expand=True)

            self._rows[t["id"]] = {
                "icon": icon_lbl,
                "name": name_lbl,
                "result": None,
            }

            tid = t["id"]
            for w in (row_frame, icon_lbl, name_lbl):
                w.bind("<Button-1>", lambda e, i=tid: self._show_detail(i))

        # Right detail panel
        self._right = ctk.CTkFrame(body, fg_color=BG_DARK)
        self._right.pack(side="left", fill="both", expand=True, padx=16, pady=16)

        self._detail_placeholder()

    def _detail_placeholder(self):
        for w in self._right.winfo_children():
            w.destroy()
        ctk.CTkLabel(
            self._right,
            text="← ტესტს შეეხე დეტალებისთვის\nან \"Run All Tests\" დააჭირე",
            font=ctk.CTkFont(size=FONT_HEAD), text_color=TEXT_MUTED,
            justify="center",
        ).place(relx=0.5, rely=0.45, anchor="center")

    #  Test runner (thread) 

    def _start_tests(self):
        if self._running:
            return
        self._running = True
        self._run_btn.configure(state="disabled", text="Running...")
        self._summary_lbl.configure(text="")
        for row in self._rows.values():
            row["icon"].configure(text="", text_color=TEXT_MUTED)
            row["name"].configure(text_color=TEXT_LABEL)
            row["result"] = None
        self._detail_placeholder()
        threading.Thread(target=self._run_all, daemon=True).start()

    def _run_all(self):
        counts = {"ok": 0, "fail": 0, "warn": 0}
        for t in self._tests:
            self.after(0, lambda tid=t["id"]:
                       self._rows[tid]["icon"].configure(text="...", text_color=YELLOW))
            try:
                status, cmd, stdout, stderr, note = t["fn"]()
            except Exception as ex:
                status, cmd, stdout, stderr, note = "fail", "", "", str(ex), "Test exception"

            counts[status] = counts.get(status, 0) + 1
            result = {"status": status, "cmd": cmd, "stdout": stdout,
                      "stderr": stderr, "note": note, "label": t["label"]}
            self._rows[t["id"]]["result"] = result
            self.after(0, lambda tid=t["id"], r=result: self._update_row(tid, r))
            time.sleep(0.1)   # tiny pause so UI updates are visible

        self.after(0, lambda: self._finish(counts))

    def _finish(self, counts):
        self._running = False
        self._run_btn.configure(state="normal", text="  Run All Tests")
        total = sum(counts.values())
        self._summary_lbl.configure(
            text=f"OK: {counts.get('ok',0)}  WARN: {counts.get('warn',0)}  FAIL: {counts.get('fail',0)}  / {total}",
            text_color=RED if counts.get("fail", 0) else (YELLOW if counts.get("warn", 0) else GREEN),
        )

    def _update_row(self, tid, result):
        s = result["status"]
        row = self._rows[tid]
        row["icon"].configure(text=STATUS_ICON[s], text_color=STATUS_COLOR[s])
        row["name"].configure(text_color=STATUS_COLOR[s] if s != "ok" else TEXT)
        row["result"] = result

    #  Detail panel 

    def _show_detail(self, tid):
        result = self._rows[tid].get("result")
        for w in self._right.winfo_children():
            w.destroy()

        t = next(x for x in self._tests if x["id"] == tid)

        # Header
        hdr = ctk.CTkFrame(self._right, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 12))

        status = result["status"] if result else "pending"
        ctk.CTkLabel(
            hdr, text=STATUS_ICON[status], font=ctk.CTkFont(size=22),
            text_color=STATUS_COLOR[status],
        ).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(
            hdr, text=t["label"],
            font=ctk.CTkFont(size=FONT_TITLE, weight="bold"), text_color=TEXT,
        ).pack(side="left")

        if not result:
            ctk.CTkLabel(
                self._right, text="ჯერ Run All Tests დააჭირე.",
                text_color=TEXT_MUTED, font=ctk.CTkFont(size=FONT_BODY),
            ).pack(anchor="w")
            return

        scroll = ctk.CTkScrollableFrame(
            self._right, fg_color="transparent", corner_radius=0,
            scrollbar_button_color=BORDER, scrollbar_button_hover_color=ACCENT,
        )
        scroll.pack(fill="both", expand=True)

        def section(title, content, color=TEXT_LABEL):
            ctk.CTkLabel(
                scroll, text=title,
                font=ctk.CTkFont(size=FONT_SMALL, weight="bold"),
                text_color=TEXT_MUTED,
            ).pack(anchor="w", pady=(12, 2))
            box = ctk.CTkFrame(scroll, fg_color=BG_INPUT, corner_radius=8)
            box.pack(fill="x")
            ctk.CTkLabel(
                box, text=content or "(ცარიელი)",
                font=ctk.CTkFont(family="Courier New", size=FONT_SMALL),
                text_color=color, wraplength=560, justify="left", anchor="w",
            ).pack(anchor="w", padx=12, pady=8)

        # Command
        if result["cmd"]:
            section("  გაშვებული ბრძანება", result["cmd"], ACCENT)

        # stdout
        if result["stdout"]:
            section("stdout (გამოსვალი)", result["stdout"])

        # stderr
        if result["stderr"]:
            section("stderr (შეცდომა)", result["stderr"], RED)

        # explanation / fix
        if result["note"]:
            ctk.CTkLabel(
                scroll, text="განმარტება / გამოსავალი",
                font=ctk.CTkFont(size=FONT_SMALL, weight="bold"),
                text_color=TEXT_MUTED,
            ).pack(anchor="w", pady=(14, 4))
            note_box = ctk.CTkFrame(
                scroll,
                fg_color={"ok": "#0d2a18", "fail": "#2a0d0d", "warn": "#2a200d"}.get(status, BG_INPUT),
                corner_radius=8,
            )
            note_box.pack(fill="x")
            ctk.CTkLabel(
                note_box, text=result["note"],
                font=ctk.CTkFont(size=FONT_BODY),
                text_color=STATUS_COLOR[status],
                wraplength=560, justify="left", anchor="w",
            ).pack(anchor="w", padx=14, pady=10)

    #  Export 

    def _export(self):
        from tkinter import filedialog
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text", "*.txt"), ("All", "*.*")],
            initialfile="diagnostic_report.txt",
        )
        if not path:
            return
        lines = ["Android Device Manager — Diagnostic Report",
                 "=" * 60, ""]
        for t in self._tests:
            r = self._rows[t["id"]].get("result")
            lines.append(f"[{t['id']:02d}] {t['group']:10s}  {t['label']}")
            if r:
                lines.append(f"  Status : {r['status'].upper()}")
                if r["cmd"]:
                    lines.append(f"  Command: {r['cmd']}")
                if r["stdout"]:
                    lines.append(f"  Stdout : {r['stdout']}")
                if r["stderr"]:
                    lines.append(f"  Stderr : {r['stderr']}")
                if r["note"]:
                    lines.append(f"  Note   : {r['note']}")
            else:
                lines.append("  Status : NOT RUN")
            lines.append("")
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        tk.messagebox.showinfo("Export", f"ლოგი შენახულია:\n{path}")


# 

if __name__ == "__main__":
    app = DiagWindow()
    app.mainloop()