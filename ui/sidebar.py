import customtkinter as ctk
from config.theme import *


MODULES = [
    "System",
    "Network / APN",
    "Camera",
    "WebView",
    "Apps",
]


class Sidebar(ctk.CTkFrame):
    def __init__(self, parent, on_select):
        super().__init__(parent, fg_color=BG_PANEL, width=190, corner_radius=0)
        self.pack(fill="y", side="left")
        self.pack_propagate(False)

        self.on_select = on_select
        self.active    = "System"
        self.buttons   = {}

        ctk.CTkLabel(
            self, text="Modules",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=MUTED
        ).pack(pady=(22, 8), padx=16, anchor="w")

        for name in MODULES:
            btn = ctk.CTkButton(
                self,
                text=f"  {name}",
                anchor="w", height=40, corner_radius=10,
                fg_color=ACCENT if name == self.active else "transparent",
                hover_color="#1A5FA8",
                font=ctk.CTkFont(size=13), text_color=TEXT,
                command=lambda n=name: self._select(n)
            )
            btn.pack(fill="x", padx=10, pady=3)
            self.buttons[name] = btn

        ctk.CTkFrame(self, fg_color=MUTED, height=1).pack(
            fill="x", padx=12, pady=(20, 10)
        )
        ctk.CTkLabel(
            self, text="ADB Status",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=MUTED
        ).pack(padx=16, anchor="w")

        self.adb_label = ctk.CTkLabel(
            self, text="●  Disconnected",
            font=ctk.CTkFont(size=11), text_color=RED
        )
        self.adb_label.pack(padx=16, pady=4, anchor="w")

    def _select(self, name: str):
        self.buttons[self.active].configure(fg_color="transparent")
        self.active = name
        self.buttons[name].configure(fg_color=ACCENT)
        self.on_select(name)

    def set_adb_status(self, connected: bool):
        if connected:
            self.adb_label.configure(text="●  Connected", text_color=GREEN)
        else:
            self.adb_label.configure(text="●  Disconnected", text_color=RED)
