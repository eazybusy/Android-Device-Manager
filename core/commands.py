"""
core/commands.py — Command Pattern for thread-safe module execution.

UI Thread:  module.build_command() — reads StringVars, creates a Command snapshot
BG Thread:  command.execute(serial) — only I/O, never touches Tkinter

This eliminates the thread-safety violation where apply_all() accessed
Tkinter StringVar objects from a background thread.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from core import adb


# ── Base protocol ──────────────────────────────────────────────────────────────

class Command:
    """Base class for all executable commands."""
    label: str = "Command"

    def execute(self, serial: str | None) -> tuple[bool, str]:
        raise NotImplementedError


# ── Concrete Commands ──────────────────────────────────────────────────────────

@dataclass
class InstallApkCommand(Command):
    apk_path: str
    label: str = "Install APK"

    def execute(self, serial: str | None) -> tuple[bool, str]:
        if not self.apk_path.strip():
            return True, "apk_path empty — skipped"
        return adb.install_apk(self.apk_path.strip(), serial=serial)


@dataclass
class SendBroadcastCommand(Command):
    action: str
    extras: dict
    label: str = "Broadcast"

    def execute(self, serial: str | None) -> tuple[bool, str]:
        ok, code, msg = adb.send_broadcast(self.action, self.extras, serial=serial)
        if ok:
            return True, f"{self.label} OK (result={code})"
        if code == -1:
            # No receiver — app not installed or wrong action string.
            # Treat as WARNING (not hard failure) so Run All continues.
            return True, f"{self.label} — no receiver (result=-1, app not installed?)"
        return False, f"{self.label} FAIL: {msg}"


@dataclass
class SetSettingCommand(Command):
    namespace: str
    key: str
    value: str
    label: str = "Set Setting"

    def execute(self, serial: str | None) -> tuple[bool, str]:
        ok, err = adb.set_setting(self.namespace, self.key, self.value, serial=serial)
        if ok:
            return True, f"{self.namespace}/{self.key} = {self.value}"
        return False, err or f"FAIL: {self.namespace}/{self.key}"


@dataclass
class SetDeviceNameCommand(Command):
    name: str
    label: str = "Set Device Name"

    def execute(self, serial: str | None) -> tuple[bool, str]:
        if not self.name.strip():
            return True, "device_name empty — skipped"
        ok, err = adb.set_device_name(self.name.strip(), serial=serial)
        return ok, err or f"device_name = {self.name}"


@dataclass
class SetSleepCommand(Command):
    sleep_label: str
    label: str = "Set Sleep Timeout"

    def execute(self, serial: str | None) -> tuple[bool, str]:
        ok, err = adb.set_sleep_timeout(self.sleep_label, serial=serial)
        return ok, err or f"sleep = {self.sleep_label}"


@dataclass
class CompositeCommand(Command):
    """Executes a list of Commands sequentially; stops on first hard failure."""
    commands: list = field(default_factory=list)
    label: str = "Composite"
    stop_on_failure: bool = False

    def execute(self, serial: str | None) -> tuple[bool, str]:
        parts = []
        all_ok = True
        for cmd in self.commands:
            ok, msg = cmd.execute(serial)
            parts.append(f"{cmd.label}: {'OK' if ok else 'FAIL'} — {msg}")
            if not ok:
                all_ok = False
                if self.stop_on_failure:
                    break
        return all_ok, " | ".join(parts) if parts else "no commands"


@dataclass
class SkipCommand(Command):
    reason: str = "section disabled"
    label: str = "Skip"

    def execute(self, serial: str | None) -> tuple[bool, str]:
        return True, f"skipped: {self.reason}"
