"""
ui/helpers.py — Shared UI building blocks and async utilities.
"""

import threading
import traceback
import customtkinter as ctk
from tkinter import messagebox
from config.theme import *


# ── Async helper ───────────────────────────────────────────────────────────────

def run_async(widget, fn, callback, on_error=None) -> None:
    """
    Run fn() in a background thread; deliver result to UI thread via callback.

    fn()            — background thread (I/O, ADB calls — NO Tkinter access)
    callback(result)— UI thread (widget updates, messageboxes)
    on_error(exc)   — UI thread, called if fn() raises; default shows messagebox

    If fn() raises and no on_error is provided, the exception is shown
    via messagebox.showerror() and printed to stderr for debugging.
    """
    def _worker():
        try:
            result = fn()
            widget.after(0, lambda: callback(result))
        except Exception as exc:
            traceback.print_exc()
            if on_error:
                widget.after(0, lambda e=exc: on_error(e))
            else:
                widget.after(0, lambda e=exc: messagebox.showerror(
                    "შეუსაბამო შეცდომა",
                    f"მოულოდნელი შეცდომა:\n{e}\n\n"
                    "დეტალები ~/.adm/logs/-ში."
                ))

    threading.Thread(target=_worker, daemon=True).start()


def set_btn_busy(btn: ctk.CTkButton, busy: bool, idle_text: str = "Apply") -> None:
    """Disable/enable a button and show loading indicator."""
    if busy:
        btn.configure(state="disabled", text="...")
    else:
        btn.configure(state="normal", text=idle_text)


# ── Layout helpers ─────────────────────────────────────────────────────────────

def make_scrollable(parent) -> ctk.CTkScrollableFrame:
    return ctk.CTkScrollableFrame(
        parent,
        fg_color="transparent",
        corner_radius=0,
        scrollbar_button_color=BORDER,
        scrollbar_button_hover_color=ACCENT,
    )


def section_title(parent, text: str) -> None:
    ctk.CTkLabel(
        parent,
        text=text,
        font=ctk.CTkFont(size=FONT_TITLE, weight="bold"),
        text_color=TEXT,
    ).pack(anchor="w", pady=(0, 6))

    ctk.CTkFrame(parent, fg_color=BORDER, height=1).pack(
        anchor="w", fill="x", pady=(0, 16)
    )


# ── Card component ─────────────────────────────────────────────────────────────

def card(parent, title: str) -> ctk.CTkFrame:
    outer = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=R_CARD)
    outer.pack(fill="x", pady=(0, 12))

    header = ctk.CTkFrame(outer, fg_color="transparent")
    header.pack(fill="x", padx=16, pady=(14, 0))

    ctk.CTkFrame(header, fg_color=ACCENT, width=3, height=16, corner_radius=2).pack(
        side="left", padx=(0, 10)
    )
    ctk.CTkLabel(
        header, text=title,
        font=ctk.CTkFont(size=FONT_HEAD, weight="bold"),
        text_color=TEXT,
    ).pack(side="left")

    ctk.CTkFrame(outer, fg_color=BORDER, height=1).pack(
        fill="x", padx=16, pady=(10, 4)
    )
    return outer


# ── Row component ──────────────────────────────────────────────────────────────

def row(parent, label: str, widget_fn) -> None:
    r = ctk.CTkFrame(parent, fg_color="transparent")
    r.pack(fill="x", padx=16, pady=5)

    ctk.CTkLabel(
        r, text=label, width=160, anchor="w",
        font=ctk.CTkFont(size=FONT_BODY),
        text_color=TEXT_LABEL,
    ).pack(side="left")

    widget_fn(r)


# ── Button components ──────────────────────────────────────────────────────────

def apply_btn(parent, text: str = "Apply", cmd=None) -> ctk.CTkButton:
    """Primary action button — returns the widget for set_btn_busy()."""
    frame = ctk.CTkFrame(parent, fg_color="transparent")
    frame.pack(fill="x", padx=16, pady=(10, 16))

    btn = ctk.CTkButton(
        frame, text=text, height=36, corner_radius=R_BTN,
        fg_color=ACCENT, hover_color=ACCENT_DARK,
        font=ctk.CTkFont(size=FONT_BODY, weight="bold"),
        text_color="white",
        command=cmd or (lambda: None),
    )
    btn.pack(anchor="e")
    return btn


def ghost_btn(parent, text: str, cmd=None, width: int = 80) -> ctk.CTkButton:
    return ctk.CTkButton(
        parent, text=text, height=32, width=width,
        corner_radius=R_BTN, fg_color="transparent",
        border_width=1, border_color=BORDER, hover_color=BG_HOVER,
        font=ctk.CTkFont(size=FONT_BODY), text_color=TEXT_LABEL,
        command=cmd or (lambda: None),
    )


# ── Inline widgets ─────────────────────────────────────────────────────────────

def entry(parent, textvariable, width: int = 240,
          placeholder: str = "", show: str = "") -> ctk.CTkEntry:
    return ctk.CTkEntry(
        parent, textvariable=textvariable,
        width=width, height=34, corner_radius=R_INPUT,
        fg_color=BG_INPUT, border_color=BORDER, border_width=1,
        text_color=TEXT, placeholder_text=placeholder,
        placeholder_text_color=TEXT_MUTED,
        font=ctk.CTkFont(size=FONT_BODY), show=show,
    )


def option_menu(parent, values, variable, width: int = 160) -> ctk.CTkOptionMenu:
    return ctk.CTkOptionMenu(
        parent, values=values, variable=variable,
        width=width, height=34, corner_radius=R_INPUT,
        fg_color=BG_INPUT, button_color=ACCENT,
        button_hover_color=ACCENT_DARK,
        dropdown_fg_color=BG_CARD, dropdown_hover_color=BG_HOVER,
        text_color=TEXT, dropdown_text_color=TEXT,
        font=ctk.CTkFont(size=FONT_BODY),
    )


def switch(parent, variable) -> ctk.CTkSwitch:
    return ctk.CTkSwitch(
        parent, text="", variable=variable,
        onvalue=True, offvalue=False,
        button_color=ACCENT, button_hover_color=ACCENT_DARK,
        progress_color=ACCENT_SOFT,
    )


# ── Status / info labels ───────────────────────────────────────────────────────

def status_label(parent, text: str = "") -> ctk.CTkLabel:
    """
    Inline feedback label inside a card.
    Update after async ops:
        self._status.configure(text="OK", text_color=GREEN)
    """
    lbl = ctk.CTkLabel(
        parent, text=text,
        font=ctk.CTkFont(size=FONT_SMALL),
        text_color=TEXT_MUTED, anchor="w",
    )
    lbl.pack(anchor="w", padx=16, pady=(2, 8))
    return lbl


def warning_label(parent, text: str) -> None:
    ctk.CTkLabel(
        parent, text=f"[!]  {text}",
        text_color=YELLOW,
        font=ctk.CTkFont(size=FONT_SMALL),
    ).pack(anchor="w", padx=16, pady=(4, 2))
