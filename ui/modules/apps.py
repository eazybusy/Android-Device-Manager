"""
ui/modules/apps.py — Apps module (APK install + App Settings broadcast)
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

SECTION = "apps"


class AppsModule(ctk.CTkFrame):
    def __init__(self, parent, storage):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True)
        self._storage = storage
        self._build()

    def _build(self):
        section_title(self, "Apps")

        scroll = make_scrollable(self)
        scroll.pack(fill="both", expand=True)

        data = self._storage.get(SECTION)

        c1 = card(scroll, "APK Installation")

        self.apk_path = ctk.StringVar(value=data.get("apk_path", ""))
        self.apk_path.trace_add(
            "write",
            lambda *_: self._storage.set_value(
                SECTION, "apk_path", self.apk_path.get()),
        )

        def apk_picker(p):
            entry(p, self.apk_path, width=190,
                  placeholder="APK file path...").pack(side="left", padx=(0, 8))
            ghost_btn(p, "Browse", self._browse, width=74).pack(side="left")

        row(c1, "APK File", apk_picker)
        self._apk_btn    = apply_btn(c1, "Install APK", self._apply_apk)
        self._apk_status = status_label(c1)

        c2 = card(scroll, "App Settings (Broadcast)")

        self.pkg  = ctk.StringVar(value=data.get("pkg",  ""))
        self.pref = ctk.StringVar(value=data.get("pref", ""))
        self.val  = ctk.StringVar(value=data.get("val",  ""))

        for var, key in [
            (self.pkg,  "pkg"),
            (self.pref, "pref"),
            (self.val,  "val"),
        ]:
            var.trace_add(
                "write",
                lambda *_, k=key, v=var: self._storage.set_value(SECTION, k, v.get()),
            )

        row(c2, "Package Name",
            lambda p: entry(p, self.pkg, width=240,
                            placeholder="com.example.app").pack(side="left"))
        row(c2, "Preference Key",
            lambda p: entry(p, self.pref, width=240).pack(side="left"))
        row(c2, "Value",
            lambda p: entry(p, self.val, width=240).pack(side="left"))

        self._pref_btn    = apply_btn(c2, "Send App Settings", self._apply_settings)
        self._pref_status = status_label(c2)

    def _browse(self):
        path = filedialog.askopenfilename(filetypes=[("APK", "*.apk")])
        if path:
            self.apk_path.set(path)

    def _apply_apk(self):
        path = self.apk_path.get().strip()
        if not path:
            messagebox.showwarning("APK", "APK ფაილი არ არის მითითებული.")
            return

        set_btn_busy(self._apk_btn, True, "Install APK")
        self._apk_status.configure(
            text="ინსტალაცია მიმდინარეობს...", text_color=YELLOW)

        def _work():
            return adb.install_apk(path)

        def _done(result):
            ok, msg = result
            set_btn_busy(self._apk_btn, False, "Install APK")
            if ok:
                self._apk_status.configure(
                    text="წარმატებით დაინსტალირდა.", text_color=GREEN)
                messagebox.showinfo("Install APK", msg)
            else:
                self._apk_status.configure(
                    text="ინსტალაცია ვერ მოხდა.", text_color=RED)
                messagebox.showerror(
                    "Install APK", f"ვერ დაინსტალირდა.\n\n{msg}")

        run_async(self, _work, _done)

    def _apply_settings(self):
        pkg  = self.pkg.get().strip()
        pref = self.pref.get().strip()
        val  = self.val.get()

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
                    text="Broadcast გაიგზავნა — App-ს Receiver სჭირდება.",
                    text_color=YELLOW)
            else:
                self._pref_status.configure(
                    text=f"FAIL: {msg[:80]}", text_color=RED)
                messagebox.showerror(
                    "App Settings", f"Broadcast ვერ გაიგზავნა.\n\n{msg}")

        run_async(self, _work, _done)

    def build_command(self):
        from core.commands import InstallApkCommand, SendBroadcastCommand, CompositeCommand
        cmds = [InstallApkCommand(
            apk_path=self.apk_path.get(), label="Install APK")]
        pkg  = self.pkg.get().strip()
        pref = self.pref.get().strip()
        if pkg and pref:
            cmds.append(SendBroadcastCommand(
                action="com.example.SET_PREF",
                extras={"package": pkg, "prefKey": pref,
                        "prefValue": self.val.get()},
                label="SET_PREF Broadcast",
            ))
        return CompositeCommand(commands=cmds, label="Apps")
