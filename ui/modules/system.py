import customtkinter as ctk
from config.theme import *
from ui.helpers import card, row, apply_btn, section_title
from core import adb

SECTION = "system"


class SystemModule(ctk.CTkFrame):
    def __init__(self, parent, storage):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True)
        self._storage = storage
        self._build()

    def _build(self):
        section_title(self, "System")

        data = self._storage.get(SECTION)

        c1 = card(self, "Developer Mode")
        self.dev_mode = ctk.StringVar(value=data.get("dev_mode", "On"))
        self.dev_mode.trace_add("write", lambda *_: self._save())

        row(c1, "Developer Mode",
            lambda p: ctk.CTkOptionMenu(
                p, values=["On", "Off"],
                variable=self.dev_mode,
                fg_color=BG_PANEL, button_color=ACCENT, width=160
            ).pack(side="left"))
        apply_btn(c1, "Apply Developer Mode", self._apply_devmode)

        c2 = card(self, "Sleep Mode")
        self.sleep = ctk.StringVar(value=data.get("sleep", "30 sec"))
        self.sleep.trace_add("write", lambda *_: self._save())

        row(c2, "Timeout",
            lambda p: ctk.CTkOptionMenu(
                p, values=["15 sec", "30 sec", "1 min", "2 min", "5 min", "Never"],
                variable=self.sleep,
                fg_color=BG_PANEL, button_color=ACCENT, width=160
            ).pack(side="left"))
        apply_btn(c2, "Apply Sleep", self._apply_sleep)

    def _save(self):
        self._storage.set_value(SECTION, "dev_mode", self.dev_mode.get())
        self._storage.set_value(SECTION, "sleep", self.sleep.get())

    def _apply_devmode(self):
        value = "1" if self.dev_mode.get() == "On" else "0"
        adb.set_setting("global", "development_settings_enabled", value)

    def _apply_sleep(self):
        mapping = {
            "15 sec": "15000", "30 sec": "30000",
            "1 min": "60000", "2 min": "120000",
            "5 min": "300000", "Never": "2147483647"
        }
        ms = mapping.get(self.sleep.get(), "30000")
        adb.set_setting("system", "screen_off_timeout", ms)

    def apply_all(self) -> tuple[bool, str]:
        try:
            self._apply_devmode()
            self._apply_sleep()
            return True, "Developer mode and sleep applied"
        except Exception as e:
            return False, str(e)
