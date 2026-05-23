import customtkinter as ctk
from tkinter import filedialog
from config.theme import *
from ui.helpers import card, row, apply_btn, section_title
from core import adb

SECTION = "apps"


class AppsModule(ctk.CTkFrame):
    def __init__(self, parent, storage):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True)
        self._storage = storage
        self._build()

    def _build(self):
        section_title(self, "Apps")

        data = self._storage.get(SECTION)

        c1 = card(self, "APK Installation")
        self.apk_path = ctk.StringVar(value=data.get("apk_path", ""))
        self.apk_path.trace_add("write", lambda *_: self._storage.set_value(SECTION, "apk_path", self.apk_path.get()))

        def apk_picker(p):
            ctk.CTkEntry(
                p, textvariable=self.apk_path,
                width=200, fg_color=BG_PANEL, border_color=ACCENT,
                placeholder_text="APK file path..."
            ).pack(side="left", padx=(0, 6))
            ctk.CTkButton(
                p, text="Browse", width=60, height=28,
                fg_color=BG_PANEL, hover_color=ACCENT,
                command=self._browse
            ).pack(side="left")

        row(c1, "APK File", apk_picker)
        apply_btn(c1, "Install APK", self._apply_apk)

        c2 = card(self, "App Settings")
        self.pkg  = ctk.StringVar(value=data.get("pkg", ""))
        self.pref = ctk.StringVar(value=data.get("pref", ""))
        self.val  = ctk.StringVar(value=data.get("val", ""))

        for var, key in [(self.pkg, "pkg"), (self.pref, "pref"), (self.val, "val")]:
            var.trace_add("write", lambda *_, k=key, v=var: self._storage.set_value(SECTION, k, v.get()))

        row(c2, "Package Name",
            lambda p: ctk.CTkEntry(p, textvariable=self.pkg,
                width=240, fg_color=BG_PANEL, border_color=ACCENT,
                placeholder_text="com.example.app"
            ).pack(side="left"))
        row(c2, "Preference Key",
            lambda p: ctk.CTkEntry(p, textvariable=self.pref,
                width=240, fg_color=BG_PANEL, border_color=ACCENT
            ).pack(side="left"))
        row(c2, "Value",
            lambda p: ctk.CTkEntry(p, textvariable=self.val,
                width=240, fg_color=BG_PANEL, border_color=ACCENT
            ).pack(side="left"))
        apply_btn(c2, "Send App Settings", self._apply_settings)

    def _browse(self):
        path = filedialog.askopenfilename(filetypes=[("APK", "*.apk")])
        if path:
            self.apk_path.set(path)

    def _apply_apk(self):
        path = self.apk_path.get()
        if path:
            adb.install_apk(path)

    def _apply_settings(self):
        if self.pkg.get() and self.pref.get():
            extras = {
                "package":   self.pkg.get(),
                "prefKey":   self.pref.get(),
                "prefValue": self.val.get(),
            }
            adb.send_broadcast("com.example.SET_PREF", extras)

    def apply_all(self) -> tuple[bool, str]:
        try:
            self._apply_apk()
            self._apply_settings()
            return True, f"APK={self.apk_path.get() or '(none)'} / pkg={self.pkg.get() or '(none)'}"
        except Exception as e:
            return False, str(e)
