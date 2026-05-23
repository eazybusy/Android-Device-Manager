import customtkinter as ctk
import sys
from tkinter import messagebox
from config.theme import *
from core import profiles


class ProfileDialog(ctk.CTkToplevel):
    def __init__(self, parent, on_select):
        super().__init__(parent)
        self.title("Profiles")
        self.geometry("500x520")
        self.resizable(False, False)
        self.configure(fg_color=BG_DARK)

        self.lift()
        self.focus_force()
        if sys.platform == "darwin":
            self.after(100, self.grab_set)
        else:
            self.grab_set()

        self._on_select   = on_select
        self._active_name = ""
        self._buttons: dict[str, ctk.CTkButton] = {}

        self._list_frame_outer = ctk.CTkFrame(self, fg_color="transparent")
        self._form_frame_outer = ctk.CTkFrame(self, fg_color="transparent")

        self._build_list_view()
        self._build_form_view()
        self._show_list()

    # ── List View ─────────────────────────────────────────────────────────────

    def _build_list_view(self):
        f = self._list_frame_outer

        # Header
        header = ctk.CTkFrame(f, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 14))

        ctk.CTkLabel(
            header,
            text="Profiles",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=TEXT,
        ).pack(side="left")

        # Scrollable list
        self._list_scroll = ctk.CTkScrollableFrame(
            f,
            fg_color=BG_PANEL,
            corner_radius=R_CARD,
            width=440,
            height=270,
            scrollbar_button_color=BORDER,
            scrollbar_button_hover_color=ACCENT,
        )
        self._list_scroll.pack(padx=24, pady=(0, 14))

        # New profile row
        new_row = ctk.CTkFrame(f, fg_color="transparent")
        new_row.pack(fill="x", padx=24, pady=(0, 10))

        self._new_entry = ctk.CTkEntry(
            new_row,
            placeholder_text="New profile name...",
            placeholder_text_color=TEXT_MUTED,
            fg_color=BG_INPUT,
            border_color=BORDER,
            border_width=1,
            text_color=TEXT,
            corner_radius=R_INPUT,
            font=ctk.CTkFont(size=13),
        )
        self._new_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkButton(
            new_row,
            text="Create",
            width=84,
            height=34,
            corner_radius=R_BTN,
            fg_color=ACCENT,
            hover_color=ACCENT_DARK,
            font=ctk.CTkFont(size=13),
            text_color="white",
            command=self._go_to_create,
        ).pack(side="left")

        # Action row
        btn_row = ctk.CTkFrame(f, fg_color="transparent")
        btn_row.pack(fill="x", padx=24, pady=(2, 20))

        ctk.CTkButton(
            btn_row,
            text="Delete",
            width=96,
            height=36,
            corner_radius=R_BTN,
            fg_color="transparent",
            border_width=1,
            border_color=RED,
            hover_color="#2A1010",
            font=ctk.CTkFont(size=13),
            text_color=RED,
            command=self._delete,
        ).pack(side="left")

        ctk.CTkButton(
            btn_row,
            text="Select Profile",
            width=130,
            height=36,
            corner_radius=R_BTN,
            fg_color=ACCENT,
            hover_color=ACCENT_DARK,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="white",
            command=self._select,
        ).pack(side="right")

    def _refresh_list(self):
        for w in self._list_scroll.winfo_children():
            w.destroy()
        self._buttons.clear()

        names = profiles.list_profiles()
        if not names:
            ctk.CTkLabel(
                self._list_scroll,
                text="No profiles yet — create one above",
                text_color=TEXT_MUTED,
                font=ctk.CTkFont(size=12),
            ).pack(pady=24)
            return

        for name in names:
            btn = ctk.CTkButton(
                self._list_scroll,
                text=name,
                anchor="w",
                height=38,
                corner_radius=R_BTN,
                fg_color="transparent",
                hover_color=BG_HOVER,
                font=ctk.CTkFont(size=13),
                text_color=TEXT_LABEL,
                command=lambda n=name: self._highlight(n),
            )
            btn.pack(fill="x", pady=2, padx=4)
            self._buttons[name] = btn

        if self._active_name in self._buttons:
            self._highlight(self._active_name)

    def _highlight(self, name: str):
        if self._active_name and self._active_name in self._buttons:
            self._buttons[self._active_name].configure(
                fg_color="transparent", text_color=TEXT_LABEL
            )
        self._active_name = name
        self._buttons[name].configure(fg_color=ACCENT_SOFT, text_color=ACCENT)

    def _delete(self):
        if not self._active_name:
            return
        ok = messagebox.askyesno(
            "Delete Profile",
            f'Delete profile "{self._active_name}"?',
            parent=self,
        )
        if ok:
            profiles.delete_profile(self._active_name)
            self._active_name = ""
            self._refresh_list()

    def _select(self):
        if not self._active_name:
            messagebox.showwarning("No selection", "Select a profile first.", parent=self)
            return
        self._on_select(self._active_name)
        self.destroy()

    # ── Form View ─────────────────────────────────────────────────────────────

    def _build_form_view(self):
        f = self._form_frame_outer

        # Top row: back + title
        top = ctk.CTkFrame(f, fg_color="transparent")
        top.pack(fill="x", padx=24, pady=(18, 0))

        ctk.CTkButton(
            top,
            text="← Back",
            width=70,
            height=30,
            corner_radius=R_BTN,
            fg_color="transparent",
            border_width=1,
            border_color=BORDER,
            hover_color=BG_HOVER,
            font=ctk.CTkFont(size=12),
            text_color=TEXT_LABEL,
            command=self._show_list,
        ).pack(side="left")

        ctk.CTkLabel(
            top,
            text="New Profile",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=TEXT,
        ).pack(side="left", padx=14)

        # Profile name field
        name_row = ctk.CTkFrame(f, fg_color="transparent")
        name_row.pack(fill="x", padx=24, pady=(12, 4))

        ctk.CTkLabel(
            name_row,
            text="Profile Name",
            width=130,
            anchor="w",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_LABEL,
        ).pack(side="left")

        self._form_name = ctk.CTkEntry(
            name_row,
            fg_color=BG_INPUT,
            border_color=BORDER,
            border_width=1,
            text_color=TEXT,
            corner_radius=R_INPUT,
            font=ctk.CTkFont(size=13),
            width=250,
            placeholder_text="e.g. Pixel 7",
            placeholder_text_color=TEXT_MUTED,
        )
        self._form_name.pack(side="left")

        # Scrollable form body
        self._scroll = ctk.CTkScrollableFrame(
            f,
            fg_color=BG_PANEL,
            corner_radius=R_CARD,
            scrollbar_button_color=BORDER,
            scrollbar_button_hover_color=ACCENT,
        )
        self._scroll.pack(fill="both", expand=True, padx=24, pady=12)

        self._form_vars: dict                         = {}
        self._section_enabled: dict[str, ctk.BooleanVar] = {}
        self._section_widgets: dict[str, list]            = {}

        self._build_section("system", "System", [
            ("Developer Mode", "dev_mode", "option",
             ["On", "Off"], "On"),
            ("Sleep Timeout",  "sleep",    "option",
             ["15 sec", "30 sec", "1 min", "2 min", "5 min", "Never"], "30 sec"),
        ])
        self._build_section("network", "Network / APN", [
            ("APN Name", "apn_name", "entry", None, ""),
            ("APN",      "apn",      "entry", None, ""),
            ("MCC",      "mcc",      "entry", None, ""),
            ("MNC",      "mnc",      "entry", None, ""),
            ("Proxy",    "proxy",    "entry", None, ""),
            ("Port",     "port",     "entry", None, ""),
            ("API IP",   "api_ip",   "entry", None, ""),
            ("API Port", "api_port", "entry", None, ""),
            ("API Key",  "api_key",  "entry", None, ""),
        ])
        self._build_section("camera", "Camera", [
            ("Resolution", "resolution", "option",
             ["640x480", "1280x720", "1920x1080", "3840x2160"], "1920x1080"),
            ("FPS",   "fps",   "option", ["15", "24", "30", "60"], "30"),
            ("Flash", "flash", "option", ["Auto", "On", "Off", "Torch"], "Auto"),
        ])
        self._build_section("webview", "WebView", [
            ("Start URL",  "url",     "entry",  None, ""),
            ("JavaScript", "js",      "bool",   None, True),
            ("Cookies",    "cookies", "bool",   None, True),
            ("Cache Mode", "cache",   "option",
             ["LOAD_DEFAULT", "LOAD_CACHE_ELSE_NETWORK",
              "LOAD_NO_CACHE", "LOAD_CACHE_ONLY"], "LOAD_DEFAULT"),
        ])
        self._build_section("apps", "Apps", [
            ("APK Path",       "apk_path", "entry", None, ""),
            ("Package Name",   "pkg",      "entry", None, ""),
            ("Preference Key", "pref",     "entry", None, ""),
            ("Value",          "val",      "entry", None, ""),
        ])

        ctk.CTkButton(
            f,
            text="Save Profile",
            height=40,
            corner_radius=R_BTN,
            fg_color=ACCENT,
            hover_color=ACCENT_DARK,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="white",
            command=self._save_profile,
        ).pack(pady=(0, 18), padx=24, fill="x")

    def _build_section(self, section_key: str, title: str, fields: list):
        enabled_var = ctk.BooleanVar(value=False)
        self._section_enabled[section_key]  = enabled_var
        self._section_widgets[section_key]  = []

        # Section header
        header = ctk.CTkFrame(self._scroll, fg_color="transparent")
        header.pack(fill="x", padx=8, pady=(14, 2))

        ctk.CTkSwitch(
            header,
            text="",
            variable=enabled_var,
            onvalue=True,
            offvalue=False,
            button_color=ACCENT,
            button_hover_color=ACCENT_DARK,
            progress_color=ACCENT_SOFT,
            width=40,
            command=lambda k=section_key: self._toggle_section(k),
        ).pack(side="left", padx=(0, 10))

        ctk.CTkLabel(
            header,
            text=title,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=TEXT,
        ).pack(side="left")

        ctk.CTkLabel(
            header,
            text="(disabled — will be skipped)",
            font=ctk.CTkFont(size=10),
            text_color=TEXT_MUTED,
        ).pack(side="left", padx=8)

        ctk.CTkFrame(self._scroll, fg_color=BORDER, height=1).pack(
            fill="x", padx=8, pady=(2, 6)
        )

        # Fields
        for label, key, kind, options, default in fields:
            row_frame = ctk.CTkFrame(self._scroll, fg_color="transparent")
            row_frame.pack(fill="x", padx=8, pady=3)

            lbl = ctk.CTkLabel(
                row_frame,
                text=label,
                width=140,
                anchor="w",
                font=ctk.CTkFont(size=12),
                text_color=TEXT_MUTED,
            )
            lbl.pack(side="left")

            if kind == "entry":
                var = ctk.StringVar(value=default)
                widget = ctk.CTkEntry(
                    row_frame,
                    textvariable=var,
                    width=220,
                    height=32,
                    corner_radius=R_INPUT,
                    fg_color=BG_DARK,
                    border_color=BORDER,
                    border_width=1,
                    text_color=TEXT_MUTED,
                    font=ctk.CTkFont(size=12),
                    state="disabled",
                )
                widget.pack(side="left")

            elif kind == "option":
                var = ctk.StringVar(value=default)
                widget = ctk.CTkOptionMenu(
                    row_frame,
                    values=options,
                    variable=var,
                    width=220,
                    height=32,
                    corner_radius=R_INPUT,
                    fg_color=BG_DARK,
                    button_color=TEXT_MUTED,
                    button_hover_color=ACCENT_DARK,
                    dropdown_fg_color=BG_CARD,
                    dropdown_hover_color=BG_HOVER,
                    text_color=TEXT_MUTED,
                    font=ctk.CTkFont(size=12),
                    state="disabled",
                )
                widget.pack(side="left")

            elif kind == "bool":
                var = ctk.BooleanVar(value=default)
                widget = ctk.CTkSwitch(
                    row_frame,
                    text="",
                    variable=var,
                    onvalue=True,
                    offvalue=False,
                    button_color=TEXT_MUTED,
                    progress_color=BG_DARK,
                    state="disabled",
                )
                widget.pack(side="left")

            self._form_vars[key] = (kind, var)
            self._section_widgets[section_key].append((lbl, widget, kind))

    def _toggle_section(self, section_key: str):
        enabled = self._section_enabled[section_key].get()
        for lbl, widget, kind in self._section_widgets[section_key]:
            if enabled:
                lbl.configure(text_color=TEXT_LABEL)
                if kind == "bool":
                    widget.configure(state="normal", button_color=ACCENT)
                elif kind == "option":
                    widget.configure(
                        state="normal",
                        button_color=ACCENT,
                        text_color=TEXT,
                        fg_color=BG_INPUT,
                    )
                else:
                    widget.configure(
                        state="normal",
                        border_color=BORDER_ACT,
                        text_color=TEXT,
                        fg_color=BG_INPUT,
                    )
            else:
                lbl.configure(text_color=TEXT_MUTED)
                if kind == "bool":
                    widget.configure(state="disabled", button_color=TEXT_MUTED)
                elif kind == "option":
                    widget.configure(
                        state="disabled",
                        button_color=TEXT_MUTED,
                        text_color=TEXT_MUTED,
                        fg_color=BG_DARK,
                    )
                else:
                    widget.configure(
                        state="disabled",
                        border_color=BORDER,
                        text_color=TEXT_MUTED,
                        fg_color=BG_DARK,
                    )

    def _save_profile(self):
        name = self._form_name.get().strip()
        if not name:
            messagebox.showwarning("Name required", "Enter a profile name.", parent=self)
            return

        enabled = {k: v.get() for k, v in self._section_enabled.items()}

        if not any(enabled.values()):
            messagebox.showwarning(
                "Nothing enabled",
                "Enable at least one section before saving.",
                parent=self,
            )
            return

        data = {
            "_enabled": enabled,
            "system": {
                "dev_mode": self._form_vars["dev_mode"][1].get(),
                "sleep":    self._form_vars["sleep"][1].get(),
            },
            "network": {
                "apn_name": self._form_vars["apn_name"][1].get(),
                "apn":      self._form_vars["apn"][1].get(),
                "mcc":      self._form_vars["mcc"][1].get(),
                "mnc":      self._form_vars["mnc"][1].get(),
                "proxy":    self._form_vars["proxy"][1].get(),
                "port":     self._form_vars["port"][1].get(),
                "api_ip":   self._form_vars["api_ip"][1].get(),
                "api_port": self._form_vars["api_port"][1].get(),
                "api_key":  self._form_vars["api_key"][1].get(),
            },
            "camera": {
                "resolution": self._form_vars["resolution"][1].get(),
                "fps":        self._form_vars["fps"][1].get(),
                "flash":      self._form_vars["flash"][1].get(),
            },
            "webview": {
                "url":     self._form_vars["url"][1].get(),
                "js":      self._form_vars["js"][1].get(),
                "cookies": self._form_vars["cookies"][1].get(),
                "cache":   self._form_vars["cache"][1].get(),
            },
            "apps": {
                "apk_path": self._form_vars["apk_path"][1].get(),
                "pkg":      self._form_vars["pkg"][1].get(),
                "pref":     self._form_vars["pref"][1].get(),
                "val":      self._form_vars["val"][1].get(),
            },
        }

        if profiles.create_profile(name):
            profiles.save_profile(name, data)
        else:
            ok = messagebox.askyesno(
                "Exists",
                f'Profile "{name}" already exists. Overwrite?',
                parent=self,
            )
            if not ok:
                return
            profiles.save_profile(name, data)

        self._active_name = name
        self._show_list()

    # ── Navigation ────────────────────────────────────────────────────────────

    def _show_list(self):
        self._form_frame_outer.pack_forget()
        self._list_frame_outer.pack(fill="both", expand=True)
        self.geometry("500x520")
        self._refresh_list()

    def _go_to_create(self):
        name = self._new_entry.get().strip()
        self._list_frame_outer.pack_forget()
        self._form_frame_outer.pack(fill="both", expand=True)
        self.geometry("500x700")
        self._form_name.delete(0, "end")
        if name:
            self._form_name.insert(0, name)
        for key in self._section_enabled:
            self._section_enabled[key].set(False)
            self._toggle_section(key)