import customtkinter as ctk
from tkinter import filedialog
from config.theme import *
from ui.helpers import card, row, apply_btn, section_title, make_scrollable, entry, ghost_btn
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

        scroll = make_scrollable(self)
        scroll.pack(fill="both", expand=True)

        data = self._storage.get(SECTION)

        # ── APK Installation ───────────────────────────────────────────────────
        c1 = card(scroll, "APK Installation")

        self.apk_path = ctk.StringVar(value=data.get("apk_path", ""))
        self.apk_path.trace_add(
            "write",
            lambda *_: self._storage.set_value(SECTION, "apk_path", self.apk_path.get()),
        )

        def apk_picker(p):
            entry(p, self.apk_path, width=190,
                  placeholder="APK file path...").pack(side="left", padx=(0, 8))
            ghost_btn(p, "Browse", self._browse, width=74).pack(side="left")

        row(c1, "APK File", apk_picker)
        apply_btn(c1, "Install APK", self._apply_apk)

        # ── App Settings ───────────────────────────────────────────────────────
        c2 = card(scroll, "App Settings")

        self.pkg  = ctk.StringVar(value=data.get("pkg",  ""))
        self.pref = ctk.StringVar(value=data.get("pref", ""))
        self.val  = ctk.StringVar(value=data.get("val",  ""))

        for var, key in [
            (self.pkg,  "pkg"),
            (self.pref, "pref"),
            (self.val,  "val"),
        ]:
            var.trace_add(
                "write",
                lambda *_, k=key, v=var: self._storage.set_value(SECTION, k, v.get()),
            )

        row(c2, "Package Name",
            lambda p: entry(p, self.pkg, width=240,
                            placeholder="com.example.app").pack(side="left"))
        row(c2, "Preference Key",
            lambda p: entry(p, self.pref, width=240).pack(side="left"))
        row(c2, "Value",
            lambda p: entry(p, self.val, width=240).pack(side="left"))

        apply_btn(c2, "Send App Settings", self._apply_settings)

    def _browse(self):
        path = filedialog.askopenfilename(filetypes=[("APK", "*.apk")])
        if path:
            self.apk_path.set(path)

    def _apply_apk(self):
        if self.apk_path.get():
            adb.install_apk(self.apk_path.get())

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
            return True, (
                f"APK={self.apk_path.get() or '(none)'} / "
                f"pkg={self.pkg.get() or '(none)'}"
            )
        except Exception as e:
            return False, str(e)