import customtkinter as ctk
import sys
from tkinter import messagebox
from config.theme import *
from core import profiles


class ProfileDialog(ctk.CTkToplevel):
    def __init__(self, parent, on_select):
        super().__init__(parent)
        self.title("Profiles")
        self.geometry("480x500")
        self.resizable(False, False)
        self.configure(fg_color=BG_DARK)

        self.lift()
        self.focus_force()
        if sys.platform == "darwin":
            self.after(100, self.grab_set)
        else:
            self.grab_set()

        self._on_select = on_select
        self._active_name: str = ""
        self._buttons: dict[str, ctk.CTkButton] = {}

        self._list_frame_outer = ctk.CTkFrame(self, fg_color="transparent")
        self._form_frame_outer = ctk.CTkFrame(self, fg_color="transparent")

        self._build_list_view()
        self._build_form_view()
        self._show_list()

    # ─── List View ────────────────────────────────────────────────────────────

    def _build_list_view(self):
        f = self._list_frame_outer

        ctk.CTkLabel(
            f, text="Profiles",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=TEXT
        ).pack(pady=(20, 10))

        self._list_scroll = ctk.CTkScrollableFrame(
            f, fg_color=BG_PANEL, corner_radius=10, width=400, height=280
        )
        self._list_scroll.pack(padx=24, pady=(0, 12))

        new_row = ctk.CTkFrame(f, fg_color="transparent")
        new_row.pack(fill="x", padx=24, pady=(0, 8))

        self._new_entry = ctk.CTkEntry(
            new_row, placeholder_text="New profile name...",
            fg_color=BG_PANEL, border_color=ACCENT,
            font=ctk.CTkFont(size=12)
        )
        self._new_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(
            new_row, text="Create", width=80, height=32,
            fg_color=ACCENT, hover_color="#1A5FA8",
            font=ctk.CTkFont(size=12),
            command=self._go_to_create
        ).pack(side="left")

        btn_row = ctk.CTkFrame(f, fg_color="transparent")
        btn_row.pack(fill="x", padx=24, pady=(4, 16))

        ctk.CTkButton(
            btn_row, text="Delete", width=100, height=36,
            fg_color=RED, hover_color="#B71C1C",
            font=ctk.CTkFont(size=12),
            command=self._delete
        ).pack(side="left")

        ctk.CTkButton(
            btn_row, text="Select", width=100, height=36,
            fg_color=GREEN, hover_color="#388E3C",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._select
        ).pack(side="right")

    def _refresh_list(self):
        for w in self._list_scroll.winfo_children():
            w.destroy()
        self._buttons.clear()

        names = profiles.list_profiles()
        if not names:
            ctk.CTkLabel(
                self._list_scroll, text="No profiles yet",
                text_color=MUTED, font=ctk.CTkFont(size=12)
            ).pack(pady=20)
            return

        for name in names:
            btn = ctk.CTkButton(
                self._list_scroll,
                text=name, anchor="w",
                height=36, corner_radius=8,
                fg_color="transparent", hover_color="#1A5FA8",
                font=ctk.CTkFont(size=13), text_color=TEXT,
                command=lambda n=name: self._highlight(n)
            )
            btn.pack(fill="x", pady=2, padx=4)
            self._buttons[name] = btn

        if self._active_name in self._buttons:
            self._highlight(self._active_name)

    def _highlight(self, name: str):
        if self._active_name and self._active_name in self._buttons:
            self._buttons[self._active_name].configure(fg_color="transparent")
        self._active_name = name
        self._buttons[name].configure(fg_color=ACCENT)

    def _delete(self):
        if not self._active_name:
            return
        ok = messagebox.askyesno(
            "Delete", f'Delete profile "{self._active_name}"?', parent=self
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

    # ─── Form View ────────────────────────────────────────────────────────────

    def _build_form_view(self):
        f = self._form_frame_outer

        top_row = ctk.CTkFrame(f, fg_color="transparent")
        top_row.pack(fill="x", padx=24, pady=(16, 0))

        ctk.CTkButton(
            top_row, text="Back", width=60, height=28,
            fg_color=BG_PANEL, hover_color=ACCENT,
            font=ctk.CTkFont(size=12), text_color=MUTED,
            command=self._show_list
        ).pack(side="left")

        ctk.CTkLabel(
            top_row, text="New Profile",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=TEXT
        ).pack(side="left", padx=12)

        name_row = ctk.CTkFrame(f, fg_color="transparent")
        name_row.pack(fill="x", padx=24, pady=(10, 4))

        ctk.CTkLabel(
            name_row, text="Profile Name", width=130, anchor="w",
            font=ctk.CTkFont(size=12), text_color=TEXT
        ).pack(side="left")

        self._form_name = ctk.CTkEntry(
            name_row, fg_color=BG_PANEL, border_color=ACCENT,
            font=ctk.CTkFont(size=12), width=240,
            placeholder_text="e.g. Pixel 7"
        )
        self._form_name.pack(side="left")

        self._scroll = ctk.CTkScrollableFrame(
            f, fg_color=BG_PANEL, corner_radius=10
        )
        self._scroll.pack(fill="both", expand=True, padx=24, pady=10)

        self._form_vars: dict = {}
        self._section_enabled: dict[str, ctk.BooleanVar] = {}
        self._section_widgets: dict[str, list] = {}

        self._build_section("system", "System", [
            ("Developer Mode", "dev_mode", "option", ["On", "Off"], "On"),
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
            f, text="Save Profile", height=40, corner_radius=12,
            fg_color=GREEN, hover_color="#388E3C",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#FFFFFF",
            command=self._save_profile
        ).pack(pady=(0, 16), padx=24, fill="x")

    def _build_section(self, section_key: str, title: str, fields: list):
        enabled_var = ctk.BooleanVar(value=False)
        self._section_enabled[section_key] = enabled_var
        self._section_widgets[section_key] = []

        header = ctk.CTkFrame(self._scroll, fg_color="transparent")
        header.pack(fill="x", padx=8, pady=(14, 2))

        ctk.CTkSwitch(
            header, text="", variable=enabled_var,
            onvalue=True, offvalue=False,
            button_color=ACCENT, width=40,
            command=lambda k=section_key: self._toggle_section(k)
        ).pack(side="left", padx=(0, 8))

        ctk.CTkLabel(
            header, text=title,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=ACCENT
        ).pack(side="left")

        ctk.CTkLabel(
            header, text="(off - will be skipped)",
            font=ctk.CTkFont(size=10),
            text_color=MUTED
        ).pack(side="left", padx=6)

        ctk.CTkFrame(self._scroll, fg_color=MUTED, height=1).pack(
            fill="x", padx=8, pady=(0, 6)
        )

        for label, key, kind, options, default in fields:
            row_frame = ctk.CTkFrame(self._scroll, fg_color="transparent")
            row_frame.pack(fill="x", padx=8, pady=3)

            lbl = ctk.CTkLabel(
                row_frame, text=label, width=140, anchor="w",
                font=ctk.CTkFont(size=12), text_color=MUTED
            )
            lbl.pack(side="left")

            if kind == "entry":
                var = ctk.StringVar(value=default)
                widget = ctk.CTkEntry(
                    row_frame, textvariable=var, width=220,
                    fg_color=BG_DARK, border_color=MUTED,
                    font=ctk.CTkFont(size=12),
                    state="disabled"
                )
                widget.pack(side="left")

            elif kind == "option":
                var = ctk.StringVar(value=default)
                widget = ctk.CTkOptionMenu(
                    row_frame, values=options, variable=var,
                    fg_color=BG_DARK, button_color=MUTED, width=220,
                    state="disabled"
                )
                widget.pack(side="left")

            elif kind == "bool":
                var = ctk.BooleanVar(value=default)
                widget = ctk.CTkSwitch(
                    row_frame, text="", variable=var,
                    onvalue=True, offvalue=False,
                    button_color=MUTED,
                    state="disabled"
                )
                widget.pack(side="left")

            self._form_vars[key] = (kind, var)
            self._section_widgets[section_key].append((lbl, widget, kind))

    def _toggle_section(self, section_key: str):
        enabled = self._section_enabled[section_key].get()
        for lbl, widget, kind in self._section_widgets[section_key]:
            if enabled:
                lbl.configure(text_color=TEXT)
                if kind == "bool":
                    widget.configure(state="normal", button_color=ACCENT)
                elif kind == "option":
                    widget.configure(state="normal", button_color=ACCENT)
                else:
                    widget.configure(state="normal", border_color=ACCENT)
            else:
                lbl.configure(text_color=MUTED)
                if kind == "bool":
                    widget.configure(state="disabled", button_color=MUTED)
                elif kind == "option":
                    widget.configure(state="disabled", button_color=MUTED)
                else:
                    widget.configure(state="disabled", border_color=MUTED)

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
                parent=self
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
                "Exists", f'Profile "{name}" already exists. Overwrite?', parent=self
            )
            if not ok:
                return
            profiles.save_profile(name, data)

        self._active_name = name
        self._show_list()

    # ─── Navigation ───────────────────────────────────────────────────────────

    def _show_list(self):
        self._form_frame_outer.pack_forget()
        self._list_frame_outer.pack(fill="both", expand=True)
        self.geometry("480x500")
        self._refresh_list()

    def _go_to_create(self):
        name = self._new_entry.get().strip()
        self._list_frame_outer.pack_forget()
        self._form_frame_outer.pack(fill="both", expand=True)
        self.geometry("480x680")
        self._form_name.delete(0, "end")
        if name:
            self._form_name.insert(0, name)
        for key in self._section_enabled:
            self._section_enabled[key].set(False)
            self._toggle_section(key)