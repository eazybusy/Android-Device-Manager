import customtkinter as ctk
from config.theme import *


class TopBar(ctk.CTkFrame):
    """Main application top bar — branding, device status, action buttons."""

    def __init__(self, parent, on_simulate, on_open_profiles, on_run):
        super().__init__(parent, fg_color=BG_PANEL, height=56, corner_radius=0)
        self.pack(fill="x", side="top")
        self.pack_propagate(False)

        # ── Brand ──────────────────────────────────────────────────────────────
        brand = ctk.CTkFrame(self, fg_color="transparent")
        brand.pack(side="left", padx=(16, 0), fill="y")

        ctk.CTkLabel(
            brand,
            text="ADM",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=ACCENT,
            width=34, height=34,
            corner_radius=8,
            fg_color=ACCENT_SOFT,
        ).pack(side="left", pady=11)

        ctk.CTkLabel(
            brand,
            text="  Android Device Manager",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TEXT,
        ).pack(side="left")

        # ── Right actions ──────────────────────────────────────────────────────
        right = ctk.CTkFrame(self, fg_color="transparent")
        right.pack(side="right", padx=14, fill="y")

        ctk.CTkButton(
            right,
            text="▶  Run All",
            height=34, width=100, corner_radius=R_BTN,
            fg_color=ACCENT, hover_color=ACCENT_DARK,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="white",
            command=on_run,
        ).pack(side="right", padx=(6, 0), pady=11)

        ctk.CTkButton(
            right,
            text="Profiles",
            height=34, width=88, corner_radius=R_BTN,
            fg_color="transparent",
            border_width=1, border_color=BORDER,
            hover_color=BG_HOVER,
            font=ctk.CTkFont(size=12),
            text_color=TEXT_LABEL,
            command=on_open_profiles,
        ).pack(side="right", padx=4, pady=11)

        ctk.CTkButton(
            right,
            text="Connect",
            height=34, width=88, corner_radius=R_BTN,
            fg_color="transparent",
            border_width=1, border_color=BORDER,
            hover_color=BG_HOVER,
            font=ctk.CTkFont(size=12),
            text_color=TEXT_LABEL,
            command=on_simulate,
        ).pack(side="right", padx=4, pady=11)

        # ── Centre status ──────────────────────────────────────────────────────
        center = ctk.CTkFrame(self, fg_color="transparent")
        center.pack(fill="both", expand=True, padx=16)

        ctk.CTkFrame(center, fg_color=BORDER, width=1).pack(
            side="left", fill="y", pady=14
        )

        info = ctk.CTkFrame(center, fg_color="transparent")
        info.pack(side="left", fill="y", padx=16)

        dev_row = ctk.CTkFrame(info, fg_color="transparent")
        dev_row.pack(anchor="w", pady=(10, 1))

        self._dev_dot = ctk.CTkLabel(
            dev_row, text="●",
            font=ctk.CTkFont(size=9), text_color=RED,
        )
        self._dev_dot.pack(side="left")

        self._dev_label = ctk.CTkLabel(
            dev_row,
            text="  No device connected",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_MUTED,
        )
        self._dev_label.pack(side="left")

        prof_row = ctk.CTkFrame(info, fg_color="transparent")
        prof_row.pack(anchor="w")

        ctk.CTkLabel(
            prof_row,
            text="Profile: ",
            font=ctk.CTkFont(size=FONT_MICRO),
            text_color=TEXT_MUTED,
        ).pack(side="left")

        self._prof_label = ctk.CTkLabel(
            prof_row,
            text="None",
            font=ctk.CTkFont(size=FONT_MICRO, weight="bold"),
            text_color=TEXT_LABEL,
        )
        self._prof_label.pack(side="left")

    def set_connected(self, device_str: str) -> None:
        self._dev_dot.configure(text_color=GREEN)
        self._dev_label.configure(text=f"  {device_str}", text_color=TEXT)

    def set_disconnected(self) -> None:
        self._dev_dot.configure(text_color=RED)
        self._dev_label.configure(text="  No device connected", text_color=TEXT_MUTED)

    def set_profile_name(self, name: str) -> None:
        self._prof_label.configure(text=name or "None")