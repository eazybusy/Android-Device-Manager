import customtkinter as ctk
from config.theme import *
from ui.helpers import card, row, apply_btn, section_title


class CameraModule(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="both", expand=True)
        self._build()

    def _build(self):
        section_title(self, "📷  კამერის სეთინგები")

        c = card(self, "📸  Camera Config")
        self.resolution = ctk.StringVar(value="1920x1080")
        self.fps        = ctk.StringVar(value="30")
        self.flash      = ctk.StringVar(value="Auto")

        row(c, "გარჩევადობა",
            lambda p: ctk.CTkOptionMenu(
                p, values=["640x480","1280x720","1920x1080","3840x2160"],
                variable=self.resolution,
                fg_color=BG_PANEL, button_color=ACCENT, width=160
            ).pack(side="left"))
        row(c, "FPS",
            lambda p: ctk.CTkOptionMenu(
                p, values=["15","24","30","60"],
                variable=self.fps,
                fg_color=BG_PANEL, button_color=ACCENT, width=160
            ).pack(side="left"))
        row(c, "Flash",
            lambda p: ctk.CTkOptionMenu(
                p, values=["Auto","On","Off","Torch"],
                variable=self.flash,
                fg_color=BG_PANEL, button_color=ACCENT, width=160
            ).pack(side="left"))
        apply_btn(c, "▶  კამერის სეთინგები", self._apply)

    def _apply(self):
        pass  # TODO: adb broadcast camera settings
