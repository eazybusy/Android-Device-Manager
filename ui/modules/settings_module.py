"""
ui/modules/settings_module.py — System / App Settings module
"""

import customtkinter as ctk
from tkinter import messagebox
from config.theme import *
from ui.helpers import (
    card, row, apply_btn, section_title, make_scrollable,
    entry, warning_label, status_label, run_async, set_btn_busy,
)
from core import adb
from core.validators import validate_package_name

SECTION_SYS  = "system"
SECTION_APPS = "apps"

_SLEEP_OPTIONS = ["15 sec", "30 sec", "1 min", "2 min", "5 min", "Never"]


class SettingsModule(ctk.CTkFrame):
    def __init__(self, parent, storage):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True)
        self._storage = storage
        self._build()

    def _build(self):
        section_title(self, "Settings")

        scroll = make_scrollable(self)
        scroll.pack(fill="both", expand=True)

        sys_data  = self._storage.get(SECTION_SYS)
        apps_data = self._storage.get(SECTION_APPS)

        # ── Device Name ────────────────────────────────────────────────────────
        c1 = card(scroll, "Device Name")

        self._device_name = ctk.StringVar(value=sys_data.get("device_name", ""))
        self._device_name.trace_add(
            "write",
            lambda *_: self._storage.set_value(
                SECTION_SYS, "device_name", self._device_name.get()),
        )

        row(c1, "Device Name",
            lambda p: entry(p, self._device_name, width=240,
                            placeholder="My Phone").pack(side="left"))

        warning_label(
            c1, "Android 8+ requires WRITE_SECURE_SETTINGS or Developer Options")
        self._name_btn    = apply_btn(c1, "Apply Device Name", self._apply_device_name)
        self._name_status = status_label(c1)

        # ── Sleep ──────────────────────────────────────────────────────────────
        c2 = card(scroll, "Sleep Mode")

        self._sleep = ctk.StringVar(value=sys_data.get("sleep", "30 sec"))
        self._sleep.trace_add(
            "write",
            lambda *_: self._storage.set_value(
                SECTION_SYS, "sleep", self._sleep.get()),
        )

        row(c2, "Screen Timeout",
            lambda p: ctk.CTkOptionMenu(
                p, values=_SLEEP_OPTIONS, variable=self._sleep,
                fg_color=BG_PANEL, button_color=ACCENT, width=160,
            ).pack(side="left"))

        self._sleep_btn    = apply_btn(c2, "Apply Sleep", self._apply_sleep)
        self._sleep_status = status_label(c2)

        # ── App Preference ─────────────────────────────────────────────────────
        c3 = card(scroll, "App Settings (Broadcast)")

        self._pkg  = ctk.StringVar(value=apps_data.get("pkg",  ""))
        self._pref = ctk.StringVar(value=apps_data.get("pref", ""))
        self._val  = ctk.StringVar(value=apps_data.get("val",  ""))

        for var, key, section in [
            (self._pkg,  "pkg",  SECTION_APPS),
            (self._pref, "pref", SECTION_APPS),
            (self._val,  "val",  SECTION_APPS),
        ]:
            var.trace_add(
                "write",
                lambda *_, k=key, v=var, s=section: self._storage.set_value(s, k, v.get()),
            )

        row(c3, "Package Name",
            lambda p: entry(p, self._pkg, width=240,
                            placeholder="com.example.app").pack(side="left"))
        row(c3, "Preference Key",
            lambda p: entry(p, self._pref, width=240).pack(side="left"))
        row(c3, "Value",
            lambda p: entry(p, self._val, width=240).pack(side="left"))

        self._pref_btn    = apply_btn(c3, "Send App Settings", self._apply_pref)
        self._pref_status = status_label(c3)

    # ── Handlers ──────────────────────────────────────────────────────────────

    def _apply_device_name(self):
        name = self._device_name.get().strip()
        if not name:
            messagebox.showwarning("Device Name", "Device name ცარიელია.")
            return

        set_btn_busy(self._name_btn, True, "Apply Device Name")
        self._name_status.configure(text="Setting...", text_color=YELLOW)

        def _work():
            return adb.set_device_name(name)

        def _done(result):
            ok, err = result
            set_btn_busy(self._name_btn, False, "Apply Device Name")
            if ok:
                suffix = f" ({err})" if err else ""
                self._name_status.configure(
                    text=f"Device name set: {name}{suffix}", text_color=GREEN)
            else:
                self._name_status.configure(
                    text="ვერ დაყენდა — იხილე შეტყობინება", text_color=RED)
                messagebox.showerror("Device Name", err)

        run_async(self, _work, _done)

    def _apply_sleep(self):
        label = self._sleep.get()
        set_btn_busy(self._sleep_btn, True, "Apply Sleep")
        self._sleep_status.configure(text="Setting...", text_color=YELLOW)

        def _work():
            return adb.set_sleep_timeout(label)

        def _done(result):
            ok, err = result
            set_btn_busy(self._sleep_btn, False, "Apply Sleep")
            if ok:
                self._sleep_status.configure(
                    text=f"Sleep timeout: {label}", text_color=GREEN)
            else:
                self._sleep_status.configure(
                    text="ვერ დაყენდა.", text_color=RED)
                if err:
                    messagebox.showerror(
                        "Sleep", f"Sleep timeout ვერ დაყენდა.\n\n{err}")

        run_async(self, _work, _done)

    def _apply_pref(self):
        pkg  = self._pkg.get().strip()
        pref = self._pref.get().strip()
        val  = self._val.get()

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

    # ── build_command ─────────────────────────────────────────────────────────

    def build_command(self):
        from core.commands import (
            CompositeCommand, SetDeviceNameCommand,
            SetSleepCommand, SendBroadcastCommand,
        )
        commands = [
            SetDeviceNameCommand(
                name=self._device_name.get(), label="Device Name"),
            SetSleepCommand(
                sleep_label=self._sleep.get(), label="Sleep Timeout"),
        ]
        pkg  = self._pkg.get().strip()
        pref = self._pref.get().strip()
        if pkg and pref:
            commands.append(SendBroadcastCommand(
                action="com.example.SET_PREF",
                extras={"package": pkg, "prefKey": pref,
                        "prefValue": self._val.get()},
                label="SET_PREF Broadcast",
            ))
        return CompositeCommand(commands=commands, label="Settings")
