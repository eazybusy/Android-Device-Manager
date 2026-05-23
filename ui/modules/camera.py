import customtkinter as ctk
from config.theme import *
from ui.helpers import card, row, apply_btn, section_title, make_scrollable, option_menu
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
                self.resolution,
                width=160,
            ).pack(side="left"))

        row(c, "FPS",
            lambda p: option_menu(
                p, ["15", "24", "30", "60"], self.fps, width=160
            ).pack(side="left"))

        row(c, "Flash Mode",
            lambda p: option_menu(
                p, ["Auto", "On", "Off", "Torch"], self.flash, width=160
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
            return True, (
                f"Camera: {self.resolution.get()} / "
                f"{self.fps.get()}fps / flash={self.flash.get()}"
            )
        except Exception as e:
            return False, str(e)