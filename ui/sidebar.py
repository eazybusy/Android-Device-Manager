"""
ui/sidebar.py — Left navigation sidebar.
ADB indicator supports three states: connected / disconnected / connecting (None).
"""

import customtkinter as ctk
from config.theme import *

MODULES = [
    "App",
    "Network / APN",
    "Camera",
    "WebView",
    "Settings",
]


class Sidebar(ctk.CTkFrame):
    def __init__(self, parent, on_select):
        super().__init__(parent, fg_color=BG_PANEL, width=200, corner_radius=0)
        self.pack(fill="y", side="left")
        self.pack_propagate(False)

        self.on_select = on_select
        self.active    = "App"
        self.buttons   = {}

        ctk.CTkLabel(
            self, text="MODULES",
            font=ctk.CTkFont(size=FONT_MICRO, weight="bold"),
            text_color=TEXT_MUTED,
        ).pack(pady=(24, 8), padx=16, anchor="w")

        for name in MODULES:
            is_active = name == self.active
            btn = ctk.CTkButton(
                self, text=f"  {name}", anchor="w", height=38,
                corner_radius=R_BTN,
                fg_color=ACCENT_SOFT if is_active else "transparent",
                hover_color=BG_HOVER, border_width=0,
                font=ctk.CTkFont(
                    size=FONT_BODY,
                    weight="bold" if is_active else "normal"),
                text_color=ACCENT if is_active else TEXT_LABEL,
                command=lambda n=name: self._select(n),
            )
            btn.pack(fill="x", padx=10, pady=2)
            self.buttons[name] = btn

        ctk.CTkFrame(self, fg_color=BORDER, height=1).pack(
            fill="x", padx=16, pady=(24, 18))

        ctk.CTkLabel(
            self, text="ADB STATUS",
            font=ctk.CTkFont(size=FONT_MICRO, weight="bold"),
            text_color=TEXT_MUTED,
        ).pack(padx=16, anchor="w", pady=(0, 6))

        status_card = ctk.CTkFrame(self, fg_color=BG_INPUT, corner_radius=R_BTN)
        status_card.pack(fill="x", padx=10)

        dot_row = ctk.CTkFrame(status_card, fg_color="transparent")
        dot_row.pack(padx=12, pady=10, anchor="w")

        self.adb_dot = ctk.CTkLabel(
            dot_row, text="●",
            font=ctk.CTkFont(size=FONT_SMALL), text_color=RED,
        )
        self.adb_dot.pack(side="left")

        self.adb_label = ctk.CTkLabel(
            dot_row, text=" Disconnected",
            font=ctk.CTkFont(size=FONT_SMALL), text_color=RED,
        )
        self.adb_label.pack(side="left")

    def _select(self, name: str):
        self.buttons[self.active].configure(
            fg_color="transparent", text_color=TEXT_LABEL,
            font=ctk.CTkFont(size=FONT_BODY))
        self.active = name
        self.buttons[name].configure(
            fg_color=ACCENT_SOFT, text_color=ACCENT,
            font=ctk.CTkFont(size=FONT_BODY, weight="bold"))
        self.on_select(name)

    def set_adb_status(self, connected) -> None:
        """
        True  -> green Connected
        False -> red Disconnected
        None  -> yellow Connecting...
        """
        if connected is True:
            self.adb_dot.configure(text_color=GREEN)
            self.adb_label.configure(text=" Connected", text_color=GREEN)
        elif connected is False:
            self.adb_dot.configure(text_color=RED)
            self.adb_label.configure(text=" Disconnected", text_color=RED)
        else:
            self.adb_dot.configure(text_color=YELLOW)
            self.adb_label.configure(text=" Connecting...", text_color=YELLOW)
