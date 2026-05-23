import customtkinter as ctk
from config.theme import *


class TopBar(ctk.CTkFrame):
    def __init__(self, parent, on_simulate, on_open_profiles, on_run):
        super().__init__(parent, fg_color=BG_PANEL, height=54, corner_radius=0)
        self.pack(fill="x", side="top")
        self.pack_propagate(False)

        ctk.CTkLabel(
            self, text="  Android Device Manager",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=TEXT
        ).pack(side="left", padx=18)

        ctk.CTkButton(
            self, text="Simulation: Connect",
            width=170, height=30, corner_radius=16,
            fg_color=ACCENT, hover_color="#1A5FA8",
            font=ctk.CTkFont(size=12),
            command=on_simulate
        ).pack(side="right", padx=6)

        ctk.CTkButton(
            self, text="RUN",
            width=80, height=30, corner_radius=16,
            fg_color=GREEN, hover_color="#388E3C",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#FFFFFF",
            command=on_run
        ).pack(side="right", padx=4)

        self._profile_btn = ctk.CTkButton(
            self, text="Profile: none",
            width=160, height=30, corner_radius=16,
            fg_color=BG_CARD, hover_color=ACCENT,
            font=ctk.CTkFont(size=12),
            text_color=MUTED,
            command=on_open_profiles
        )
        self._profile_btn.pack(side="right", padx=4)

        conn = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=20)
        conn.pack(side="right", padx=10, pady=10)

        self.dot = ctk.CTkLabel(
            conn, text="●", font=ctk.CTkFont(size=12), text_color=YELLOW
        )
        self.dot.pack(side="left", padx=(10, 4))

        self.label = ctk.CTkLabel(
            conn, text="Device not found",
            font=ctk.CTkFont(size=12), text_color=MUTED
        )
        self.label.pack(side="left", padx=(0, 10))

    def set_profile_name(self, name: str):
        self._profile_btn.configure(text=f"Profile: {name}", text_color=TEXT)

    def set_connected(self, device_name: str):
        self.dot.configure(text_color=GREEN)
        self.label.configure(text=device_name, text_color=TEXT)

    def set_disconnected(self):
        self.dot.configure(text_color=YELLOW)
        self.label.configure(text="Device not found", text_color=MUTED)