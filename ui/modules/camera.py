import customtkinter as ctk
from config.theme import *
from ui.helpers import card, row, apply_btn, section_title
from core import adb

SECTION = "camera"


class CameraModule(ctk.CTkFrame):
    def __init__(self, parent, storage):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True)
        self._storage = storage
        self._build()

    def _build(self):
        section_title(self, "Camera Settings")

        data = self._storage.get(SECTION)

        c = card(self, "Camera Config")
        self.resolution = ctk.StringVar(value=data.get("resolution", "1920x1080"))
        self.fps        = ctk.StringVar(value=data.get("fps", "30"))
        self.flash      = ctk.StringVar(value=data.get("flash", "Auto"))

        for var, key in [
            (self.resolution, "resolution"),
            (self.fps, "fps"),
            (self.flash, "flash"),
        ]:
            var.trace_add("write", lambda *_, k=key, v=var: self._storage.set_value(SECTION, k, v.get()))

        row(c, "Resolution",
            lambda p: ctk.CTkOptionMenu(
                p, values=["640x480", "1280x720", "1920x1080", "3840x2160"],
                variable=self.resolution,
                fg_color=BG_PANEL, button_color=ACCENT, width=160
            ).pack(side="left"))
        row(c, "FPS",
            lambda p: ctk.CTkOptionMenu(
                p, values=["15", "24", "30", "60"],
                variable=self.fps,
                fg_color=BG_PANEL, button_color=ACCENT, width=160
            ).pack(side="left"))
        row(c, "Flash",
            lambda p: ctk.CTkOptionMenu(
                p, values=["Auto", "On", "Off", "Torch"],
                variable=self.flash,
                fg_color=BG_PANEL, button_color=ACCENT, width=160
            ).pack(side="left"))
        apply_btn(c, "Apply Camera Settings", self._apply)

    def _apply(self):
        extras = {
            "resolution": self.resolution.get(),
            "fps":        self.fps.get(),
            "flash":      self.flash.get(),
        }
        adb.send_broadcast("com.example.SET_CAMERA", extras)

    def apply_all(self) -> tuple[bool, str]:
        try:
            self._apply()
            return True, f"Camera: {self.resolution.get()} / {self.fps.get()}fps / flash={self.flash.get()}"
        except Exception as e:
            return False, str(e)
