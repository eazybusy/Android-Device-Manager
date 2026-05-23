import customtkinter as ctk
from tkinter import messagebox
from config.theme import *
from core.storage import Storage
from ui.topbar import TopBar
from ui.sidebar import Sidebar
from ui.profile_dialog import ProfileDialog
from ui.modules import (
    SystemModule, NetworkModule,
    CameraModule, WebViewModule, AppsModule
)

MODULE_ORDER = [
    ("system",  "System",        ),
    ("network", "Network / APN", ),
    ("camera",  "Camera",        ),
    ("webview", "WebView",       ),
    ("apps",    "Apps",          ),
]

MODULE_MAP = {
    "System":        SystemModule,
    "Network / APN": NetworkModule,
    "Camera":        CameraModule,
    "WebView":       WebViewModule,
    "Apps":          AppsModule,
}


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Android Device Manager")
        self.geometry("960x620")
        self.minsize(860, 540)
        self.configure(fg_color=BG_DARK)

        self._storage = Storage()
        self._active_module = None

        self.topbar = TopBar(
            self,
            on_simulate=self._simulate_connect,
            on_open_profiles=self._open_profiles,
            on_run=self._run_all
        )

        body = ctk.CTkFrame(self, fg_color=BG_DARK)
        body.pack(fill="both", expand=True)

        self.sidebar = Sidebar(body, on_select=self._switch)

        self.content = ctk.CTkFrame(body, fg_color=BG_DARK)
        self.content.pack(fill="both", expand=True, padx=16, pady=16)

        self._switch("System")

    def _open_profiles(self):
        ProfileDialog(self, on_select=self._on_profile_selected)

    def _on_profile_selected(self, name: str):
        self._storage.set_profile(name)
        self.topbar.set_profile_name(name)
        self._reload_current_module()

    def _reload_current_module(self):
        for w in self.content.winfo_children():
            w.destroy()
        if self._active_module:
            MODULE_MAP[self._active_module](self.content, self._storage)

    def _switch(self, name: str):
        for w in self.content.winfo_children():
            w.destroy()
        self._active_module = name
        MODULE_MAP[name](self.content, self._storage)

    def _simulate_connect(self):
        self.topbar.set_connected("Pixel 7  |  Android 14")
        self.sidebar.set_adb_status(True)

    def _run_all(self):
        if not self._storage.has_profile():
            ProfileDialog(self, on_select=self._on_profile_selected_then_run)
            return
        self._execute_run()

    def _on_profile_selected_then_run(self, name: str):
        self._on_profile_selected(name)
        self.after(100, self._execute_run)

    def _execute_run(self):
        results = []
        for section_key, module_name in MODULE_ORDER:
            if not self._storage.is_enabled(section_key):
                results.append(f"[{module_name}]: SKIPPED")
                continue

            for w in self.content.winfo_children():
                w.destroy()
            mod = MODULE_MAP[module_name](self.content, self._storage)
            self._active_module = module_name
            self.update()

            ok, msg = mod.apply_all()
            results.append(f"[{module_name}]: {'OK' if ok else 'FAIL'} - {msg}")

        messagebox.showinfo("RUN Complete", "\n".join(results))