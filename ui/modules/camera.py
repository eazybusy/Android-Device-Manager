"""
ui/modules/camera.py — Camera config module
"""

import customtkinter as ctk
from tkinter import messagebox
from config.theme import *
from ui.helpers import (
    card, row, apply_btn, section_title, make_scrollable,
    option_menu, status_label, run_async, set_btn_busy,
)
from core import adb

SECTION = "camera"


class CameraModule(ctk.CTkFrame):
    def __init__(self, parent, storage):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True)
        self._storage = storage
        self._build()

    def _build(self):
        section_title(self, "Camera")

        scroll = make_scrollable(self)
        scroll.pack(fill="both", expand=True)

        data = self._storage.get(SECTION)

        c = card(scroll, "Camera Config")

        self.resolution = ctk.StringVar(value=data.get("resolution", "1920x1080"))
        self.fps        = ctk.StringVar(value=data.get("fps",        "30"))
        self.flash      = ctk.StringVar(value=data.get("flash",      "Auto"))

        for var, key in [
            (self.resolution, "resolution"),
            (self.fps,        "fps"),
            (self.flash,      "flash"),
        ]:
            var.trace_add(
                "write",
                lambda *_, k=key, v=var: self._storage.set_value(SECTION, k, v.get()),
            )

        row(c, "Resolution",
            lambda p: option_menu(
                p,
                ["640x480", "1280x720", "1920x1080", "3840x2160"],
                self.resolution, width=180,
            ).pack(side="left"))

        row(c, "FPS",
            lambda p: option_menu(
                p, ["15", "24", "30", "60"],
                self.fps, width=180,
            ).pack(side="left"))

        row(c, "Flash Mode",
            lambda p: option_menu(
                p, ["Auto", "On", "Off", "Torch"],
                self.flash, width=180,
            ).pack(side="left"))

        self._apply_btn    = apply_btn(c, "Apply Camera Settings", self._apply)
        self._apply_status = status_label(c)

    def _apply(self):
        extras = {
            "resolution": self.resolution.get(),
            "fps":        self.fps.get(),
            "flash":      self.flash.get(),
        }
        set_btn_busy(self._apply_btn, True, "Apply Camera Settings")
        self._apply_status.configure(
            text="Broadcast-ი იგზავნება...", text_color=YELLOW)

        def _work():
            return adb.send_broadcast("com.example.SET_CAMERA", extras)

        def _done(result):
            ok, code, msg = result
            set_btn_busy(self._apply_btn, False, "Apply Camera Settings")
            if ok:
                self._apply_status.configure(
                    text=f"Camera OK — {extras['resolution']} / {extras['fps']}fps",
                    text_color=GREEN)
            elif code == -1:
                self._apply_status.configure(
                    text="Broadcast გაიგზავნა — App-ს SET_CAMERA Receiver სჭირდება.",
                    text_color=YELLOW)
            else:
                self._apply_status.configure(
                    text=f"FAIL: {msg[:80]}", text_color=RED)
                messagebox.showerror(
                    "Camera", f"Camera broadcast ვერ გაიგზავნა.\n\n{msg}")

        run_async(self, _work, _done)

    def build_command(self):
        from core.commands import SendBroadcastCommand
        return SendBroadcastCommand(
            action="com.example.SET_CAMERA",
            extras={
                "resolution": self.resolution.get(),
                "fps":        self.fps.get(),
                "flash":      self.flash.get(),
            },
            label="Camera Broadcast",
        )
