import customtkinter as ctk
from config.theme import *


# ── Layout helpers ─────────────────────────────────────────────────────────────

def make_scrollable(parent) -> ctk.CTkScrollableFrame:
    """Scrollable content wrapper for module pages."""
    return ctk.CTkScrollableFrame(
        parent,
        fg_color="transparent",
        corner_radius=0,
        scrollbar_button_color=BORDER,
        scrollbar_button_hover_color=ACCENT,
    )


def section_title(parent, text: str) -> None:
    """Top-level page heading with accent underline."""
    ctk.CTkLabel(
        parent,
        text=text,
        font=ctk.CTkFont(size=FONT_TITLE, weight="bold"),
        text_color=TEXT,
    ).pack(anchor="w", pady=(0, 6))

    ctk.CTkFrame(
        parent, fg_color=BORDER, height=1
    ).pack(anchor="w", fill="x", pady=(0, 16))


# ── Card component ─────────────────────────────────────────────────────────────

def card(parent, title: str) -> ctk.CTkFrame:
    """Elevated card with left-accent header bar."""
    outer = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=R_CARD)
    outer.pack(fill="x", pady=(0, 12))

    # Header row
    header = ctk.CTkFrame(outer, fg_color="transparent")
    header.pack(fill="x", padx=16, pady=(14, 0))

    # Left accent mark
    ctk.CTkFrame(
        header, fg_color=ACCENT, width=3, height=16, corner_radius=2
    ).pack(side="left", padx=(0, 10))

    ctk.CTkLabel(
        header,
        text=title,
        font=ctk.CTkFont(size=FONT_HEAD, weight="bold"),
        text_color=TEXT,
    ).pack(side="left")

    # Divider below header
    ctk.CTkFrame(outer, fg_color=BORDER, height=1).pack(
        fill="x", padx=16, pady=(10, 4)
    )

    return outer


# ── Row component ──────────────────────────────────────────────────────────────

def row(parent, label: str, widget_fn) -> None:
    """Label + widget row with consistent spacing."""
    r = ctk.CTkFrame(parent, fg_color="transparent")
    r.pack(fill="x", padx=16, pady=5)

    ctk.CTkLabel(
        r,
        text=label,
        width=160,
        anchor="w",
        font=ctk.CTkFont(size=FONT_BODY),
        text_color=TEXT_LABEL,
    ).pack(side="left")

    widget_fn(r)


# ── Button components ──────────────────────────────────────────────────────────

def apply_btn(parent, text: str = "Apply", cmd=None) -> None:
    """Right-aligned primary action button."""
    frame = ctk.CTkFrame(parent, fg_color="transparent")
    frame.pack(fill="x", padx=16, pady=(10, 16))

    ctk.CTkButton(
        frame,
        text=text,
        height=36,
        corner_radius=R_BTN,
        fg_color=ACCENT,
        hover_color=ACCENT_DARK,
        font=ctk.CTkFont(size=FONT_BODY, weight="bold"),
        text_color="white",
        command=cmd or (lambda: None),
    ).pack(anchor="e")


def ghost_btn(parent, text: str, cmd=None, width: int = 80) -> ctk.CTkButton:
    """Outlined ghost button — secondary action."""
    return ctk.CTkButton(
        parent,
        text=text,
        height=32,
        width=width,
        corner_radius=R_BTN,
        fg_color="transparent",
        border_width=1,
        border_color=BORDER,
        hover_color=BG_HOVER,
        font=ctk.CTkFont(size=FONT_BODY),
        text_color=TEXT_LABEL,
        command=cmd or (lambda: None),
    )


# ── Inline widgets ─────────────────────────────────────────────────────────────

def entry(parent, textvariable, width: int = 240, placeholder: str = "",
          show: str = "") -> ctk.CTkEntry:
    """Styled text entry."""
    return ctk.CTkEntry(
        parent,
        textvariable=textvariable,
        width=width,
        height=34,
        corner_radius=R_INPUT,
        fg_color=BG_INPUT,
        border_color=BORDER,
        border_width=1,
        text_color=TEXT,
        placeholder_text=placeholder,
        placeholder_text_color=TEXT_MUTED,
        font=ctk.CTkFont(size=FONT_BODY),
        show=show,
    )


def option_menu(parent, values, variable, width: int = 160) -> ctk.CTkOptionMenu:
    """Styled dropdown option menu."""
    return ctk.CTkOptionMenu(
        parent,
        values=values,
        variable=variable,
        width=width,
        height=34,
        corner_radius=R_INPUT,
        fg_color=BG_INPUT,
        button_color=ACCENT,
        button_hover_color=ACCENT_DARK,
        dropdown_fg_color=BG_CARD,
        dropdown_hover_color=BG_HOVER,
        text_color=TEXT,
        dropdown_text_color=TEXT,
        font=ctk.CTkFont(size=FONT_BODY),
    )


def switch(parent, variable) -> ctk.CTkSwitch:
    """Styled toggle switch."""
    return ctk.CTkSwitch(
        parent,
        text="",
        variable=variable,
        onvalue=True,
        offvalue=False,
        button_color=ACCENT,
        button_hover_color=ACCENT_DARK,
        progress_color=ACCENT_SOFT,
    )


# ── Info / warning labels ──────────────────────────────────────────────────────

def warning_label(parent, text: str) -> None:
    """Yellow inline warning text."""
    ctk.CTkLabel(
        parent,
        text=f"⚠  {text}",
        text_color=YELLOW,
        font=ctk.CTkFont(size=FONT_SMALL),
    ).pack(anchor="w", padx=16, pady=(4, 2))