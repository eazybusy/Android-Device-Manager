import customtkinter as ctk
from tkinter import filedialog
from config.theme import *
from ui.helpers import card, row, apply_btn, section_title


class AppsModule(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True)
        self._build()

    def _build(self):
        section_title(self, "📦  აპლიკაციები")

        # APK ინსტალაცია
        c1 = card(self, "📲  APK ინსტალაცია")
        self.apk_path = ctk.StringVar()

        def apk_picker(p):
            ctk.CTkEntry(
                p, textvariable=self.apk_path,
                width=200, fg_color=BG_PANEL, border_color=ACCENT,
                placeholder_text="APK ფაილის გზა..."
            ).pack(side="left", padx=(0, 6))
            ctk.CTkButton(
                p, text="📂", width=36, height=28,
                fg_color=BG_PANEL, hover_color=ACCENT,
                command=self._browse
            ).pack(side="left")

        row(c1, "APK ფაილი", apk_picker)
        apply_btn(c1, "▶  APK დაყენება", self._apply_apk)

        # App სეთინგები
        c2 = card(self, "🔧  App სეთინგების გაწერა")
        self.pkg  = ctk.StringVar()
        self.pref = ctk.StringVar()
        self.val  = ctk.StringVar()

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
        apply_btn(c2, "▶  სეთინგების გაგზავნა", self._apply_settings)

    def _browse(self):
        path = filedialog.askopenfilename(filetypes=[("APK", "*.apk")])
        if path:
            self.apk_path.set(path)

    def _apply_apk(self):
        pass  # TODO: adb.install_apk(self.apk_path.get())

    def _apply_settings(self):
        pass  # TODO: adb broadcast app settings
