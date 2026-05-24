"""
ui/app.py — Main application window.
"""

import copy
import threading
import customtkinter as ctk
from tkinter import messagebox
from config.theme import *
from core.storage import Storage
from core import adb
from core.commands import (
    Command, CompositeCommand, InstallApkCommand, SendBroadcastCommand,
    SetSettingCommand, SetDeviceNameCommand, SetSleepCommand, SkipCommand,
)
from ui.topbar import TopBar
from ui.sidebar import Sidebar
from ui.profile_dialog import ProfileDialog
from ui.modules import (
    NetworkModule, CameraModule, WebViewModule,
    AppMainModule, SettingsModule,
)

MODULE_ORDER = [
    ("apps",     "App"),
    ("network",  "Network / APN"),
    ("camera",   "Camera"),
    ("webview",  "WebView"),
    ("settings", "Settings"),
]

MODULE_MAP = {
    "App":           AppMainModule,
    "Network / APN": NetworkModule,
    "Camera":        CameraModule,
    "WebView":       WebViewModule,
    "Settings":      SettingsModule,
}

_POLL_INTERVAL_MS = 8000   # 8-second disconnect polling


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Android Device Manager")
        self.geometry("960x620")
        self.minsize(860, 540)
        self.configure(fg_color=BG_DARK)

        self._storage          = Storage()
        self._active_module    = None
        self._selected_serial: str | None = None
        self._run_in_progress  = False
        self._polling          = False
        self._poll_job         = None

        self.topbar = TopBar(
            self,
            on_connect=self._connect,
            on_open_profiles=self._open_profiles,
            on_run=self._run_all,
        )

        body = ctk.CTkFrame(self, fg_color=BG_DARK)
        body.pack(fill="both", expand=True)

        self.sidebar = Sidebar(body, on_select=self._switch)

        self.content = ctk.CTkFrame(body, fg_color=BG_DARK)
        self.content.pack(fill="both", expand=True, padx=16, pady=16)

        self._switch("App")

    # ── Profile management ─────────────────────────────────────────────────────

    def _open_profiles(self):
        ProfileDialog(self, on_select=self._on_profile_selected)

    def _on_profile_selected(self, name: str):
        self._storage.set_profile(name)
        self.topbar.set_profile_name(name)
        self._reload_current_module()

    def _reload_current_module(self):
        for w in self.content.winfo_children():
            w.destroy()
        if self._active_module:
            MODULE_MAP[self._active_module](self.content, self._storage)

    # ── Module switching ───────────────────────────────────────────────────────

    def _switch(self, name: str):
        for w in self.content.winfo_children():
            w.destroy()
        self._active_module = name
        MODULE_MAP[name](self.content, self._storage)

    # ── ADB Connect ───────────────────────────────────────────────────────────

    def _connect(self):
        self.topbar.set_connecting()
        self.sidebar.set_adb_status(None)

        def _worker():
            # Ensure ADB daemon is running before scanning
            adb.ensure_server_running()
            authorized, unauthorized = adb.connect_and_classify()
            self.after(0, lambda: self._on_connect_result(authorized, unauthorized))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_connect_result(self, authorized: list, unauthorized: list):
        if authorized:
            d = self._selected_serial = authorized[0]["serial"]

            def _get_info():
                info = adb.get_device_info(d)
                self.after(0, lambda: self.topbar.set_connected(info))

            threading.Thread(target=_get_info, daemon=True).start()
            self.sidebar.set_adb_status(True)
            self._start_polling()

        elif unauthorized:
            self._selected_serial = None
            self.topbar.set_disconnected()
            self.sidebar.set_adb_status(False)
            self._stop_polling()
            messagebox.showwarning(
                "ADB — ავტორიზაცია",
                "ტელეფონი ჩართულია, მაგრამ ავტორიზაცია სჭირდება.\n\n"
                "ტელეფონზე გამოჩნდება dialog:\n"
                "  \"Allow USB debugging?\"\n\n"
                "დაადასტურე და კვლავ დააჭირე Connect.",
            )
        else:
            self._selected_serial = None
            self.topbar.set_disconnected()
            self.sidebar.set_adb_status(False)
            self._stop_polling()

            if not adb.adb_available():
                messagebox.showerror(
                    "ADB ვერ მოიძებნა",
                    "ADB (Android Debug Bridge) არ არის დაინსტალირებული.\n\n"
                    "გადმოწერე:\n"
                    "https://developer.android.com/tools/releases/platform-tools\n\n"
                    "გაშალე ZIP და PATH-ში დაამატე.",
                )
            else:
                messagebox.showwarning(
                    "მოწყობილობა ვერ მოიძებნა",
                    "ADB მუშაობს, მაგრამ ტელეფონი ვერ მოიძებნა.\n\n"
                    "შეამოწმე:\n"
                    "  1. USB Debugging ჩართულია Settings -> Developer Options\n"
                    "  2. USB კაბელი სწორად არის ჩართული\n"
                    "  3. USB რეჟიმი: File Transfer (MTP), არა Charging Only\n"
                    "  4. ტელეფონი განბლოკილია\n\n"
                    "სცადე: adb kill-server   შემდეგ კვლავ Connect.",
                )

    # ── Disconnect polling ─────────────────────────────────────────────────────

    def _start_polling(self):
        self._polling = True
        self._schedule_poll()

    def _stop_polling(self):
        self._polling = False
        if self._poll_job:
            self.after_cancel(self._poll_job)
            self._poll_job = None

    def _schedule_poll(self):
        if self._polling:
            self._poll_job = self.after(_POLL_INTERVAL_MS, self._poll_once)

    def _poll_once(self):
        if not self._polling or not self._selected_serial:
            return
        serial = self._selected_serial

        def _check():
            auth, _ = adb.connect_and_classify()
            return any(d["serial"] == serial for d in auth)

        def _on_result(still_connected: bool):
            if not still_connected and self._selected_serial == serial:
                self._selected_serial = None
                self.topbar.set_disconnected()
                self.sidebar.set_adb_status(False)
                self._stop_polling()
            else:
                self._schedule_poll()

        from ui.helpers import run_async
        run_async(self, _check, _on_result)

    # ── Run All ────────────────────────────────────────────────────────────────

    def _run_all(self):
        if self._run_in_progress:
            messagebox.showwarning("Run All", "Run All უკვე მიმდინარეობს...")
            return
        if not self._storage.has_profile():
            ProfileDialog(self, on_select=self._on_profile_selected_then_run)
            return
        self._execute_run()

    def _on_profile_selected_then_run(self, name: str):
        self._on_profile_selected(name)
        self.after(150, self._execute_run)

    def _execute_run(self):
        """
        Build Command snapshots on the UI thread (reads StringVars safely),
        then execute them all in a background thread (pure I/O).
        """
        self._run_in_progress = True
        self.topbar.set_run_busy(True)
        serial = self._selected_serial

        # UI thread: snapshot all module data via storage (no StringVar access in thread)
        plan: list[tuple[str, object]] = []
        for section_key, module_name in MODULE_ORDER:
            if not self._storage.is_enabled(section_key):
                plan.append((module_name, SkipCommand(reason="section disabled in profile")))
                continue
            # build_command_from_storage creates Command purely from storage dict
            cmd = _build_command_from_storage(module_name, self._storage, serial)
            plan.append((module_name, cmd))

        def _worker():
            results = []
            for module_name, cmd in plan:
                try:
                    ok, msg = cmd.execute(serial)
                    results.append((module_name, "OK" if ok else "FAIL", msg))
                except Exception as exc:
                    results.append((module_name, "EXCEPTION", str(exc)))
            self.after(0, lambda: self._on_run_complete(results))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_run_complete(self, results: list[tuple]):
        self._run_in_progress = False
        self.topbar.set_run_busy(False)

        ok_count   = sum(1 for _, s, _ in results if s == "OK")
        fail_count = sum(1 for _, s, _ in results if s == "FAIL")
        skip_count = sum(1 for _, s, _ in results if s == "SKIPPED")

        lines = [f"OK: {ok_count}   FAIL: {fail_count}   SKIPPED: {skip_count}", "-" * 44]
        for name, status, msg in results:
            lines.append(f"[{name}]: {status} - {msg}")

        messagebox.showinfo("Run Complete", "\n".join(lines))


# ── Command factory (storage-based, thread-safe) ───────────────────────────────

def _build_command_from_storage(
    module_name: str,
    storage: Storage,
    serial: str | None,
) -> "Command":
    """
    Reads from storage (dict snapshots, NOT StringVars).
    Safe to call from UI thread; result is safe to execute in background thread.
    """
    if module_name == "App":
        data = storage.get("apps")
        return InstallApkCommand(apk_path=data.get("apk_path", ""), label="App / Install APK")

    elif module_name == "Network / APN":
        data = storage.get("network")
        apn_cmd = SendBroadcastCommand(
            action="com.example.SET_APN",
            extras={k: data.get(k, "") for k in ("apn_name", "apn", "mcc", "mnc", "proxy", "port")},
            label="APN Broadcast",
        )
        api_cmd = SendBroadcastCommand(
            action="com.example.SET_API",
            extras={"ip": data.get("api_ip", ""), "port": data.get("api_port", ""),
                    "key": data.get("api_key", "")},
            label="API Broadcast",
        )
        return CompositeCommand(commands=[apn_cmd, api_cmd], label="Network / APN")

    elif module_name == "Camera":
        data = storage.get("camera")
        return SendBroadcastCommand(
            action="com.example.SET_CAMERA",
            extras={"resolution": data.get("resolution", "1920x1080"),
                    "fps": data.get("fps", "30"),
                    "flash": data.get("flash", "Auto")},
            label="Camera Broadcast",
        )

    elif module_name == "WebView":
        data = storage.get("webview")
        return SendBroadcastCommand(
            action="com.example.SET_WEBVIEW",
            extras={"url": data.get("url", ""),
                    "js": str(data.get("js", True)),
                    "cookies": str(data.get("cookies", True)),
                    "cache": data.get("cache", "LOAD_DEFAULT")},
            label="WebView Broadcast",
        )

    elif module_name == "Settings":
        data_sys  = storage.get("system")
        data_apps = storage.get("apps")
        commands  = [
            SetDeviceNameCommand(name=data_sys.get("device_name", ""),  label="Device Name"),
            SetSleepCommand(sleep_label=data_sys.get("sleep", "30 sec"), label="Sleep Timeout"),
        ]
        pkg  = data_apps.get("pkg", "").strip()
        pref = data_apps.get("pref", "").strip()
        if pkg and pref:
            commands.append(SendBroadcastCommand(
                action="com.example.SET_PREF",
                extras={"package": pkg, "prefKey": pref,
                        "prefValue": data_apps.get("val", "")},
                label="SET_PREF Broadcast",
            ))
        return CompositeCommand(commands=commands, label="Settings")

    from core.commands import SkipCommand
    return SkipCommand(reason=f"unknown module: {module_name}")
