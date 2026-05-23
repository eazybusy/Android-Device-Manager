import customtkinter as ctk
from config.theme import *
from ui.helpers import card, row, apply_btn, section_title


class SystemModule(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True)
        self._build()

    def _build(self):
        section_title(self, "⚙️  სისტემა")

        # Developer Mode
        c1 = card(self, "🛠  Developer Mode")
        self.dev_mode = ctk.StringVar(value="ჩართვა")
        row(c1, "Developer Mode",
            lambda p: ctk.CTkOptionMenu(
                p, values=["ჩართვა", "გამორთვა"],
                variable=self.dev_mode,
                fg_color=BG_PANEL, button_color=ACCENT, width=160
            ).pack(side="left"))
        apply_btn(c1, "▶  Developer Mode", self._apply_devmode)

        # Sleep Mode
        c2 = card(self, "💤  Sleep Mode")
        self.sleep = ctk.StringVar(value="30 წამი")
        row(c2, "Timeout",
            lambda p: ctk.CTkOptionMenu(
                p, values=["15 წამი", "30 წამი", "1 წუთი",
                           "2 წუთი", "5 წუთი", "არასდროს"],
                variable=self.sleep,
                fg_color=BG_PANEL, button_color=ACCENT, width=160
            ).pack(side="left"))
        apply_btn(c2, "▶  Sleep გამოყენება", self._apply_sleep)

    def _apply_devmode(self):
        pass  # TODO: adb.set_setting(...)

    def _apply_sleep(self):
        pass  # TODO: adb.set_setting("system", "screen_off_timeout", ...)
