import customtkinter as ctk
from config.theme import *
from ui.helpers import (
    card, row, apply_btn, section_title,
    make_scrollable, entry, warning_label,
)
from core import adb

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

        # ── APN Settings ───────────────────────────────────────────────────────
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
                lambda *_, k=key, var=v: self._save_apn(k, var),
            )
            self.apn_vars[key] = v
            row(c1, label,
                lambda p, var=v: entry(p, var, width=240).pack(side="left"))

        warning_label(c1, "APN write requires Root or Carrier Privilege")
        apply_btn(c1, "Apply APN", self._apply_apn)

        # ── API Settings ───────────────────────────────────────────────────────
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
                lambda *_, k=key, v=var: self._save_api(k, v),
            )

        row(c2, "IP Address",
            lambda p: entry(p, self.api_ip, width=240,
                            placeholder="192.168.x.x").pack(side="left"))
        row(c2, "Port",
            lambda p: entry(p, self.api_port, width=240,
                            placeholder="8080").pack(side="left"))
        row(c2, "API Key",
            lambda p: entry(p, self.api_key, width=240, show="*").pack(side="left"))

        apply_btn(c2, "Send API to Device", self._apply_api)

    def _save_apn(self, key: str, var: ctk.StringVar):
        self._storage.set_value(SECTION, key, var.get())

    def _save_api(self, key: str, var: ctk.StringVar):
        self._storage.set_value(SECTION, key, var.get())

    def _apply_apn(self):
        extras = {k: v.get() for k, v in self.apn_vars.items()}
        adb.send_broadcast("com.example.SET_APN", extras)

    def _apply_api(self):
        extras = {
            "ip":   self.api_ip.get(),
            "port": self.api_port.get(),
            "key":  self.api_key.get(),
        }
        adb.send_broadcast("com.example.SET_API", extras)

    def apply_all(self) -> tuple[bool, str]:
        try:
            self._apply_apn()
            self._apply_api()
            return True, "APN and API settings sent"
        except Exception as e:
            return False, str(e)