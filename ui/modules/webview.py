"""
ui/modules/webview.py — WebView config module
"""

import customtkinter as ctk
from tkinter import messagebox
from config.theme import *
from ui.helpers import (
    card, row, apply_btn, section_title, make_scrollable,
    entry, option_menu, switch, status_label, run_async, set_btn_busy,
)
from core import adb
from core.validators import validate_url

SECTION = "webview"


class WebViewModule(ctk.CTkFrame):
    def __init__(self, parent, storage):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True)
        self._storage = storage
        self._build()

    def _build(self):
        section_title(self, "WebView")

        scroll = make_scrollable(self)
        scroll.pack(fill="both", expand=True)

        data = self._storage.get(SECTION)

        c = card(scroll, "WebView Config")

        self.url     = ctk.StringVar(value=data.get("url",     ""))
        self.js      = ctk.BooleanVar(value=data.get("js",      True))
        self.cookies = ctk.BooleanVar(value=data.get("cookies", True))
        self.cache   = ctk.StringVar(value=data.get("cache",   "LOAD_DEFAULT"))

        for var, key in [
            (self.url,     "url"),
            (self.js,      "js"),
            (self.cookies, "cookies"),
            (self.cache,   "cache"),
        ]:
            var.trace_add(
                "write",
                lambda *_, k=key, v=var: self._storage.set_value(SECTION, k, v.get()),
            )

        row(c, "Start URL",
            lambda p: entry(
                p, self.url, width=280, placeholder="https://..."
            ).pack(side="left"))

        row(c, "JavaScript",
            lambda p: switch(p, self.js).pack(side="left"))

        row(c, "Cookies",
            lambda p: switch(p, self.cookies).pack(side="left"))

        row(c, "Cache Mode",
            lambda p: option_menu(
                p,
                ["LOAD_DEFAULT", "LOAD_CACHE_ELSE_NETWORK",
                 "LOAD_NO_CACHE", "LOAD_CACHE_ONLY"],
                self.cache, width=220,
            ).pack(side="left"))

        self._apply_btn    = apply_btn(c, "Apply WebView", self._apply)
        self._apply_status = status_label(c)

    def _apply(self):
        url = self.url.get().strip()
        err = validate_url(url)
        if err:
            messagebox.showerror("Validation", err)
            return

        extras = {
            "url":     url,
            "js":      str(self.js.get()),
            "cookies": str(self.cookies.get()),
            "cache":   self.cache.get(),
        }
        set_btn_busy(self._apply_btn, True, "Apply WebView")
        self._apply_status.configure(
            text="Broadcast-ი იგზავნება...", text_color=YELLOW)

        def _work():
            return adb.send_broadcast("com.example.SET_WEBVIEW", extras)

        def _done(result):
            ok, code, msg = result
            set_btn_busy(self._apply_btn, False, "Apply WebView")
            if ok:
                url_short = (url or "(empty)")[:40]
                self._apply_status.configure(
                    text=f"WebView OK — {url_short}", text_color=GREEN)
            elif code == -1:
                self._apply_status.configure(
                    text="Broadcast გაიგზავნა — App-ს SET_WEBVIEW Receiver სჭირდება.",
                    text_color=YELLOW)
            else:
                self._apply_status.configure(
                    text=f"FAIL: {msg[:80]}", text_color=RED)
                messagebox.showerror(
                    "WebView", f"WebView broadcast ვერ გაიგზავნა.\n\n{msg}")

        run_async(self, _work, _done)

    def build_command(self):
        from core.commands import SendBroadcastCommand
        return SendBroadcastCommand(
            action="com.example.SET_WEBVIEW",
            extras={
                "url":     self.url.get(),
                "js":      str(self.js.get()),
                "cookies": str(self.cookies.get()),
                "cache":   self.cache.get(),
            },
            label="WebView Broadcast",
        )
