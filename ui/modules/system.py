"""
ui/modules/system.py — System / Developer Options module
"""

import customtkinter as ctk
from tkinter import messagebox
from config.theme import *
from ui.helpers import (
    card, row, apply_btn, section_title,
    status_label, run_async, set_btn_busy,
)
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
                p, values=["On", "Off"], variable=self.dev_mode,
                fg_color=BG_PANEL, button_color=ACCENT, width=160,
            ).pack(side="left"))

        self._dev_btn    = apply_btn(c1, "Apply Developer Mode", self._apply_devmode)
        self._dev_status = status_label(c1)

        c2 = card(self, "Sleep Mode")

        self.sleep = ctk.StringVar(value=data.get("sleep", "30 sec"))
        self.sleep.trace_add("write", lambda *_: self._save())

        row(c2, "Timeout",
            lambda p: ctk.CTkOptionMenu(
                p,
                values=["15 sec", "30 sec", "1 min", "2 min", "5 min", "Never"],
                variable=self.sleep,
                fg_color=BG_PANEL, button_color=ACCENT, width=160,
            ).pack(side="left"))

        self._sleep_btn    = apply_btn(c2, "Apply Sleep", self._apply_sleep)
        self._sleep_status = status_label(c2)

    def _save(self):
        self._storage.set_value(SECTION, "dev_mode", self.dev_mode.get())
        self._storage.set_value(SECTION, "sleep",    self.sleep.get())

    def _apply_devmode(self):
        enabled = self.dev_mode.get() == "On"
        set_btn_busy(self._dev_btn, True, "Apply Developer Mode")
        self._dev_status.configure(text="Setting...", text_color=YELLOW)

        def _work():
            return adb.set_developer_mode(enabled)

        def _done(result):
            ok, err = result
            set_btn_busy(self._dev_btn, False, "Apply Developer Mode")
            if ok:
                self._dev_status.configure(
                    text=f"Developer Mode: {'On' if enabled else 'Off'}",
                    text_color=GREEN)
            else:
                self._dev_status.configure(
                    text="ვერ დაყენდა — იხილე შეტყობინება", text_color=RED)
                messagebox.showerror("Developer Mode", err)

        run_async(self, _work, _done)

    def _apply_sleep(self):
        label = self.sleep.get()
        set_btn_busy(self._sleep_btn, True, "Apply Sleep")
        self._sleep_status.configure(text="Setting...", text_color=YELLOW)

        def _work():
            return adb.set_sleep_timeout(label)

        def _done(result):
            ok, err = result
            set_btn_busy(self._sleep_btn, False, "Apply Sleep")
            if ok:
                self._sleep_status.configure(
                    text=f"Sleep timeout: {label}", text_color=GREEN)
            else:
                self._sleep_status.configure(text="ვერ დაყენდა.", text_color=RED)
                if err:
                    messagebox.showerror(
                        "Sleep", f"Sleep timeout ვერ დაყენდა.\n\n{err}")

        run_async(self, _work, _done)

    def build_command(self):
        from core.commands import CompositeCommand, SetDeviceNameCommand, SetSleepCommand
        return CompositeCommand(
            commands=[
                SetSleepCommand(
                    sleep_label=self.sleep.get(), label="Sleep Timeout"),
            ],
            label="System",
        )
