import customtkinter as ctk
from config.theme import *


def card(parent, title: str) -> ctk.CTkFrame:
    frame = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=14)
    frame.pack(fill="x", pady=8)
    ctk.CTkLabel(
        frame, text=title,
        font=ctk.CTkFont(size=13, weight="bold"),
        text_color=ACCENT
    ).pack(anchor="w", padx=18, pady=(14, 6))
    return frame


def row(parent, label: str, widget_fn) -> None:
    r = ctk.CTkFrame(parent, fg_color="transparent")
    r.pack(fill="x", padx=18, pady=5)
    ctk.CTkLabel(
        r, text=label, width=160, anchor="w",
        font=ctk.CTkFont(size=12), text_color=TEXT
    ).pack(side="left")
    widget_fn(r)


def apply_btn(parent, text="Apply", cmd=None) -> None:
    ctk.CTkButton(
        parent, text=text, height=38, corner_radius=12,
        fg_color=GREEN, hover_color="#388E3C",
        font=ctk.CTkFont(size=13, weight="bold"),
        text_color="#FFFFFF",
        command=cmd or (lambda: None)
    ).pack(pady=(18, 14), padx=18, anchor="e")


def section_title(parent, text: str) -> None:
    ctk.CTkLabel(
        parent, text=text,
        font=ctk.CTkFont(size=18, weight="bold"),
        text_color=TEXT
    ).pack(anchor="w", pady=(0, 12))
