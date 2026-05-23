import customtkinter as ctk
from config.theme import *
from ui.topbar  import TopBar
from ui.sidebar import Sidebar
from ui.modules import (
    SystemModule, NetworkModule,
    CameraModule, WebViewModule, AppsModule
)

MODULE_MAP = {
    "სისტემა":      SystemModule,
    "ქსელი / APN":  NetworkModule,
    "კამერა":        CameraModule,
    "WebView":       WebViewModule,
    "აპლიკაციები":  AppsModule,
}


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Android Device Manager")
        self.geometry("960x620")
        self.minsize(860, 540)
        self.configure(fg_color=BG_DARK)

        self.topbar = TopBar(self, on_simulate=self._simulate_connect)

        body = ctk.CTkFrame(self, fg_color=BG_DARK)
        body.pack(fill="both", expand=True)

        self.sidebar = Sidebar(body, on_select=self._switch)

        self.content = ctk.CTkFrame(body, fg_color=BG_DARK)
        self.content.pack(fill="both", expand=True, padx=16, pady=16)

        self._switch("სისტემა")

    def _switch(self, name: str):
        for w in self.content.winfo_children():
            w.destroy()
        MODULE_MAP[name](self.content)

    def _simulate_connect(self):
        self.topbar.set_connected("Pixel 7  |  Android 14")
        self.sidebar.set_adb_status(True)
