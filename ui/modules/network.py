import customtkinter as ctk
from config.theme import *
from ui.helpers import card, row, apply_btn, section_title


class NetworkModule(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True)
        self._build()

    def _build(self):
        section_title(self, "📡  ქსელი / APN")

        # APN
        c1 = card(self, "🌐  APN სეთინგები")
        self.apn_vars = {}
        for label, key in [("APN სახელი","name"),("APN","apn"),
                           ("MCC","mcc"),("MNC","mnc"),
                           ("Proxy","proxy"),("Port","port")]:
            v = ctk.StringVar()
            self.apn_vars[key] = v
            row(c1, label,
                lambda p, var=v: ctk.CTkEntry(
                    p, textvariable=var, width=240,
                    fg_color=BG_PANEL, border_color=ACCENT
                ).pack(side="left"))

        ctk.CTkLabel(
            c1,
            text="⚠️  APN-ის ჩაწერა Root ან Carrier Privilege-ს მოითხოვს",
            text_color=YELLOW, font=ctk.CTkFont(size=11)
        ).pack(anchor="w", padx=18, pady=(4, 0))
        apply_btn(c1, "▶  APN გამოყენება", self._apply_apn)

        # API
        c2 = card(self, "🔑  API სეთინგები")
        self.api_ip   = ctk.StringVar()
        self.api_port = ctk.StringVar()
        self.api_key  = ctk.StringVar()

        row(c2, "IP მისამართი",
            lambda p: ctk.CTkEntry(p, textvariable=self.api_ip,
                width=240, fg_color=BG_PANEL, border_color=ACCENT
            ).pack(side="left"))
        row(c2, "Port",
            lambda p: ctk.CTkEntry(p, textvariable=self.api_port,
                width=240, fg_color=BG_PANEL, border_color=ACCENT
            ).pack(side="left"))
        row(c2, "API Key",
            lambda p: ctk.CTkEntry(p, textvariable=self.api_key,
                width=240, fg_color=BG_PANEL, border_color=ACCENT, show="●"
            ).pack(side="left"))
        apply_btn(c2, "▶  API გაგზავნა ტელეფონზე", self._apply_api)

    def _apply_apn(self):
        pass  # TODO: adb broadcast APN intent

    def _apply_api(self):
        pass  # TODO: adb.send_broadcast("com.example.SET_API", {...})
