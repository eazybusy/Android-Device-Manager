import customtkinter as ctk
from config.theme import *
from ui.helpers import card, row, apply_btn, section_title


class WebViewModule(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True)
        self._build()

    def _build(self):
        section_title(self, "🌐  WebView სეთინგები")

        c = card(self, "🔧  WebView Config")
        self.url     = ctk.StringVar()
        self.js      = ctk.BooleanVar(value=True)
        self.cookies = ctk.BooleanVar(value=True)
        self.cache   = ctk.StringVar(value="LOAD_DEFAULT")

        row(c, "საწყისი URL",
            lambda p: ctk.CTkEntry(p, textvariable=self.url,
                width=280, fg_color=BG_PANEL, border_color=ACCENT,
                placeholder_text="https://..."
            ).pack(side="left"))
        row(c, "JavaScript",
            lambda p: ctk.CTkSwitch(
                p, text="", variable=self.js,
                onvalue=True, offvalue=False, button_color=ACCENT
            ).pack(side="left"))
        row(c, "Cookies",
            lambda p: ctk.CTkSwitch(
                p, text="", variable=self.cookies,
                onvalue=True, offvalue=False, button_color=ACCENT
            ).pack(side="left"))
        row(c, "Cache Mode",
            lambda p: ctk.CTkOptionMenu(
                p, values=["LOAD_DEFAULT","LOAD_CACHE_ELSE_NETWORK",
                           "LOAD_NO_CACHE","LOAD_CACHE_ONLY"],
                variable=self.cache,
                fg_color=BG_PANEL, button_color=ACCENT, width=220
            ).pack(side="left"))
        apply_btn(c, "▶  WebView გამოყენება", self._apply)

    def _apply(self):
        pass  # TODO: adb broadcast webview config
