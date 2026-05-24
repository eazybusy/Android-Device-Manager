"""
ui/modules/network.py — Network / APN module
"""

import customtkinter as ctk
from tkinter import messagebox
from config.theme import *
from ui.helpers import (
    card, row, apply_btn, section_title, make_scrollable,
    entry, warning_label, status_label, run_async, set_btn_busy,
)
from core import adb
from core.validators import validate_ip, validate_port, validate_mcc_mnc

SECTION = "network"


class NetworkModule(ctk.CTkFrame):
    def __init__(self, parent, storage):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True)
        self._storage = storage
        self._build()

    def _build(self):
        section_title(self, "Network / APN")

        scroll = make_scrollable(self)
        scroll.pack(fill="both", expand=True)

        data = self._storage.get(SECTION)

        # ── APN Settings ──────────────────────────────────────────────────────
        c1 = card(scroll, "APN Settings")

        self.apn_vars = {}
        fields = [
            ("APN Name", "apn_name"),
            ("APN",      "apn"),
            ("MCC",      "mcc"),
            ("MNC",      "mnc"),
            ("Proxy",    "proxy"),
            ("Port",     "port"),
        ]

        for label, key in fields:
            v = ctk.StringVar(value=data.get(key, ""))
            v.trace_add(
                "write",
                lambda *_, k=key, var=v: self._storage.set_value(SECTION, k, var.get()),
            )
            self.apn_vars[key] = v
            row(c1, label,
                lambda p, var=v: entry(p, var, width=240).pack(side="left"))

        warning_label(c1, "APN write requires Carrier Privilege or Root (Android 5+)")
        self._apn_btn    = apply_btn(c1, "Apply APN", self._apply_apn)
        self._apn_status = status_label(c1)

        # ── API Settings ──────────────────────────────────────────────────────
        c2 = card(scroll, "API Settings")

        self.api_ip   = ctk.StringVar(value=data.get("api_ip",   ""))
        self.api_port = ctk.StringVar(value=data.get("api_port", ""))
        self.api_key  = ctk.StringVar(value=data.get("api_key",  ""))

        for var, key in [
            (self.api_ip,   "api_ip"),
            (self.api_port, "api_port"),
            (self.api_key,  "api_key"),
        ]:
            var.trace_add(
                "write",
                lambda *_, k=key, v=var: self._storage.set_value(SECTION, k, v.get()),
            )

        row(c2, "IP Address",
            lambda p: entry(p, self.api_ip, width=240,
                            placeholder="192.168.x.x").pack(side="left"))
        row(c2, "Port",
            lambda p: entry(p, self.api_port, width=240,
                            placeholder="8080").pack(side="left"))
        row(c2, "API Key",
            lambda p: entry(p, self.api_key, width=240,
                            show="*").pack(side="left"))

        self._api_btn    = apply_btn(c2, "Send API to Device", self._apply_api)
        self._api_status = status_label(c2)

    # ── Handlers ──────────────────────────────────────────────────────────────

    def _validate_apn_fields(self) -> list[str]:
        errors = []
        for name, key in [("MCC", "mcc"), ("MNC", "mnc")]:
            err = validate_mcc_mnc(self.apn_vars[key].get(), name)
            if err:
                errors.append(err)
        return errors

    def _validate_api_fields(self) -> list[str]:
        errors = []
        err = validate_ip(self.api_ip.get())
        if err:
            errors.append(err)
        err = validate_port(self.api_port.get())
        if err:
            errors.append(err)
        return errors

    def _apply_apn(self):
        errors = self._validate_apn_fields()
        if errors:
            messagebox.showerror("Validation", "\n".join(errors))
            return

        extras = {k: v.get() for k, v in self.apn_vars.items()}
        set_btn_busy(self._apn_btn, True, "Apply APN")
        self._apn_status.configure(
            text="Broadcast-ი იგზავნება...", text_color=YELLOW)

        def _work():
            return adb.send_broadcast("com.example.SET_APN", extras)

        def _done(result):
            ok, code, msg = result
            set_btn_busy(self._apn_btn, False, "Apply APN")
            if ok:
                self._apn_status.configure(
                    text="APN broadcast OK (result=0)", text_color=GREEN)
            elif code == -1:
                self._apn_status.configure(
                    text="Broadcast გაიგზავნა — App-ი ვერ მიიღო (result=-1).\n"
                         "APK დაინსტალირებულია?",
                    text_color=YELLOW)
            else:
                self._apn_status.configure(
                    text=f"FAIL: {msg[:80]}", text_color=RED)
                messagebox.showerror(
                    "APN", f"APN broadcast ვერ გაიგზავნა.\n\n{msg}")

        run_async(self, _work, _done)

    def _apply_api(self):
        errors = self._validate_api_fields()
        if errors:
            messagebox.showerror("Validation", "\n".join(errors))
            return

        extras = {
            "ip":   self.api_ip.get(),
            "port": self.api_port.get(),
            "key":  self.api_key.get(),
        }
        set_btn_busy(self._api_btn, True, "Send API to Device")
        self._api_status.configure(
            text="Broadcast-ი იგზავნება...", text_color=YELLOW)

        def _work():
            return adb.send_broadcast("com.example.SET_API", extras)

        def _done(result):
            ok, code, msg = result
            set_btn_busy(self._api_btn, False, "Send API to Device")
            if ok:
                self._api_status.configure(
                    text="API broadcast OK (result=0)", text_color=GREEN)
            elif code == -1:
                self._api_status.configure(
                    text="Broadcast გაიგზავნა — App-ს SET_API Receiver სჭირდება.",
                    text_color=YELLOW)
            else:
                self._api_status.configure(
                    text=f"FAIL: {msg[:80]}", text_color=RED)
                messagebox.showerror(
                    "API", f"API broadcast ვერ გაიგზავნა.\n\n{msg}")

        run_async(self, _work, _done)

    # ── build_command ─────────────────────────────────────────────────────────

    def build_command(self):
        from core.commands import SendBroadcastCommand, CompositeCommand
        apn_cmd = SendBroadcastCommand(
            action="com.example.SET_APN",
            extras={k: v.get() for k, v in self.apn_vars.items()},
            label="APN Broadcast",
        )
        api_cmd = SendBroadcastCommand(
            action="com.example.SET_API",
            extras={
                "ip":   self.api_ip.get(),
                "port": self.api_port.get(),
                "key":  self.api_key.get(),
            },
            label="API Broadcast",
        )
        return CompositeCommand(
            commands=[apn_cmd, api_cmd], label="Network / APN")
