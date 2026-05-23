import customtkinter as ctk
from config.theme import *
from ui.helpers import card, row, apply_btn, section_title
from core import adb

SECTION = "webview"


class WebViewModule(ctk.CTkFrame):
    def __init__(self, parent, storage):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True)
        self._storage = storage
        self._build()

    def _build(self):
        section_title(self, "WebView Settings")

        data = self._storage.get(SECTION)

        c = card(self, "WebView Config")
        self.url     = ctk.StringVar(value=data.get("url", ""))
        self.js      = ctk.BooleanVar(value=data.get("js", True))
        self.cookies = ctk.BooleanVar(value=data.get("cookies", True))
        self.cache   = ctk.StringVar(value=data.get("cache", "LOAD_DEFAULT"))

        self.url.trace_add("write", lambda *_: self._storage.set_value(SECTION, "url", self.url.get()))
        self.js.trace_add("write", lambda *_: self._storage.set_value(SECTION, "js", self.js.get()))
        self.cookies.trace_add("write", lambda *_: self._storage.set_value(SECTION, "cookies", self.cookies.get()))
        self.cache.trace_add("write", lambda *_: self._storage.set_value(SECTION, "cache", self.cache.get()))

        row(c, "Start URL",
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
                p, values=["LOAD_DEFAULT", "LOAD_CACHE_ELSE_NETWORK",
                           "LOAD_NO_CACHE", "LOAD_CACHE_ONLY"],
                variable=self.cache,
                fg_color=BG_PANEL, button_color=ACCENT, width=220
            ).pack(side="left"))
        apply_btn(c, "Apply WebView", self._apply)

    def _apply(self):
        extras = {
            "url":     self.url.get(),
            "js":      str(self.js.get()),
            "cookies": str(self.cookies.get()),
            "cache":   self.cache.get(),
        }
        adb.send_broadcast("com.example.SET_WEBVIEW", extras)

    def apply_all(self) -> tuple[bool, str]:
        try:
            self._apply()
            return True, f"WebView: url={self.url.get() or '(empty)'}"
        except Exception as e:
            return False, str(e)
