"""
ui/modules/app_main.py — App module (ADB check + APK install)
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from config.theme import *
from ui.helpers import (
    card, row, apply_btn, section_title, make_scrollable,
    entry, ghost_btn, status_label, run_async, set_btn_busy,
)
from core import adb
from core.validators import validate_package_name

SECTION_APP = "apps"


class AppMainModule(ctk.CTkFrame):
    def __init__(self, parent, storage):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True)
        self._storage = storage
        self._build()

    def _build(self):
        section_title(self, "App")

        scroll = make_scrollable(self)
        scroll.pack(fill="both", expand=True)

        app_data = self._storage.get(SECTION_APP)

        # ── ADB Connection Status ──────────────────────────────────────────────
        c_conn = card(scroll, "ADB Connection")

        status_row = ctk.CTkFrame(c_conn, fg_color="transparent")
        status_row.pack(fill="x", padx=16, pady=(6, 4))

        self._conn_dot = ctk.CTkLabel(
            status_row, text="●  ADB: შეუერთებელი",
            font=ctk.CTkFont(size=FONT_BODY), text_color=RED,
        )
        self._conn_dot.pack(side="left", expand=True, anchor="w")

        self._check_btn = ghost_btn(status_row, "Check ADB", self._check_adb, width=120)
        self._check_btn.pack(side="right")

        self._conn_status = status_label(c_conn)

        # ── APK Installation ───────────────────────────────────────────────────
        c_apk = card(scroll, "APK Installation")

        self._apk_path = ctk.StringVar(value=app_data.get("apk_path", ""))
        self._apk_path.trace_add(
            "write",
            lambda *_: self._storage.set_value(
                SECTION_APP, "apk_path", self._apk_path.get()
            ),
        )

        def _apk_row(p):
            entry(p, self._apk_path, width=190,
                  placeholder="APK file path...").pack(side="left", padx=(0, 8))
            ghost_btn(p, "Browse", self._browse_apk, width=74).pack(side="left")

        row(c_apk, "APK File", _apk_row)

        self._install_btn    = apply_btn(c_apk, "Install APK", self._install_apk)
        self._install_status = status_label(c_apk)

        # ── App Preference (broadcast) ─────────────────────────────────────────
        c_pref = card(scroll, "App Settings (Broadcast)")

        self._pkg  = ctk.StringVar(value=app_data.get("pkg",  ""))
        self._pref = ctk.StringVar(value=app_data.get("pref", ""))
        self._val  = ctk.StringVar(value=app_data.get("val",  ""))

        for var, key in [
            (self._pkg,  "pkg"),
            (self._pref, "pref"),
            (self._val,  "val"),
        ]:
            var.trace_add(
                "write",
                lambda *_, k=key, v=var: self._storage.set_value(SECTION_APP, k, v.get()),
            )

        row(c_pref, "Package Name",
            lambda p: entry(p, self._pkg, width=240,
                            placeholder="com.example.app").pack(side="left"))
        row(c_pref, "Preference Key",
            lambda p: entry(p, self._pref, width=240).pack(side="left"))
        row(c_pref, "Value",
            lambda p: entry(p, self._val,  width=240).pack(side="left"))

        self._pref_btn    = apply_btn(c_pref, "Send App Settings", self._apply_pref)
        self._pref_status = status_label(c_pref)

    # ── Handlers ──────────────────────────────────────────────────────────────

    def _check_adb(self):
        set_btn_busy(self._check_btn, True, "Check ADB")
        self._conn_status.configure(text="ADB-ს შემოწმება...", text_color=YELLOW)

        def _work():
            adb.ensure_server_running()
            return adb.connect_and_classify()

        def _done(result):
            authorized, unauthorized = result
            set_btn_busy(self._check_btn, False, "Check ADB")
            if authorized:
                d = authorized[0]
                label = d["model"] or d["serial"]
                self._conn_dot.configure(
                    text=f"●  ADB: {label}", text_color=GREEN)
                self._conn_status.configure(
                    text=f"Connected — {d['serial']}", text_color=GREEN)
            elif unauthorized:
                self._conn_dot.configure(
                    text="●  ADB: ავტორიზაცია სჭირდება", text_color=YELLOW)
                self._conn_status.configure(
                    text='ტელეფონზე "Allow USB debugging?" დაადასტურე.',
                    text_color=YELLOW)
            else:
                self._conn_dot.configure(
                    text="●  ADB: მოწყობილობა ვერ მოიძებნა", text_color=RED)
                self._conn_status.configure(
                    text="USB Debugging ჩართულია? USB კაბელი სწორად?",
                    text_color=RED)

        run_async(self, _work, _done)

    def _browse_apk(self):
        path = filedialog.askopenfilename(filetypes=[("APK", "*.apk")])
        if path:
            self._apk_path.set(path)

    def _install_apk(self):
        path = self._apk_path.get().strip()
        if not path:
            messagebox.showwarning("APK", "APK ფაილი არ არის მითითებული.")
            return

        set_btn_busy(self._install_btn, True, "Install APK")
        self._install_status.configure(
            text="ინსტალაცია მიმდინარეობს...", text_color=YELLOW)

        def _work():
            return adb.install_apk(path)

        def _done(result):
            ok, msg = result
            set_btn_busy(self._install_btn, False, "Install APK")
            if ok:
                self._install_status.configure(
                    text="წარმატებით დაინსტალირდა.", text_color=GREEN)
                messagebox.showinfo("Install APK", msg)
            else:
                self._install_status.configure(
                    text="ინსტალაცია ვერ მოხდა.", text_color=RED)
                messagebox.showerror(
                    "Install APK", f"ვერ დაინსტალირდა.\n\n{msg}")

        run_async(self, _work, _done)

    def _apply_pref(self):
        pkg  = self._pkg.get().strip()
        pref = self._pref.get().strip()
        val  = self._val.get()

        # Validate package name before sending
        err = validate_package_name(pkg)
        if err:
            messagebox.showerror("Validation", err)
            return
        if not pref:
            messagebox.showwarning("App Settings", "Preference Key ცარიელია.")
            return

        extras = {"package": pkg, "prefKey": pref, "prefValue": val}
        set_btn_busy(self._pref_btn, True, "Send App Settings")
        self._pref_status.configure(
            text="Broadcast-ი იგზავნება...", text_color=YELLOW)

        def _work():
            return adb.send_broadcast("com.example.SET_PREF", extras)

        def _done(result):
            ok, code, msg = result
            set_btn_busy(self._pref_btn, False, "Send App Settings")
            if ok:
                self._pref_status.configure(
                    text=f"SET_PREF OK — {pref}={val}", text_color=GREEN)
            elif code == -1:
                self._pref_status.configure(
                    text="Broadcast გაიგზავნა — App-ს SET_PREF Receiver სჭირდება.",
                    text_color=YELLOW)
            else:
                self._pref_status.configure(
                    text=f"FAIL: {msg[:80]}", text_color=RED)
                messagebox.showerror(
                    "App Settings", f"Broadcast ვერ გაიგზავნა.\n\n{msg}")

        run_async(self, _work, _done)

    # ── build_command (Command Pattern — UI thread snapshot) ──────────────────

    def build_command(self):
        from core.commands import InstallApkCommand
        return InstallApkCommand(
            apk_path=self._apk_path.get(),
            label="App / Install APK",
        )
