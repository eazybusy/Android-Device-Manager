"""
core/storage.py — In-memory profile data with thread-safe flush.
"""
import copy
import threading
from core import profiles as prof

DEFAULT_CONFIG = prof.DEFAULT_CONFIG


class Storage:
    def __init__(self):
        self._profile_name: str = ""
        self._data: dict = {}
        self._lock = threading.Lock()

    def set_profile(self, name: str) -> None:
        with self._lock:
            self._profile_name = name
            self._data = prof.load_profile(name)

    def get_profile_name(self) -> str:
        return self._profile_name

    def has_profile(self) -> bool:
        return bool(self._profile_name)

    def is_enabled(self, section: str) -> bool:
        enabled = self._data.get("_enabled", {})
        return enabled.get(section, True)

    def get(self, section: str) -> dict:
        """
        Returns a shallow copy of the section dict.
        Callers cannot mutate internal storage state accidentally.
        """
        with self._lock:
            if section not in self._data:
                self._data[section] = dict(DEFAULT_CONFIG.get(section, {}))
            return dict(self._data[section])

    def set_value(self, section: str, key: str, value) -> None:
        with self._lock:
            if section not in self._data:
                self._data[section] = dict(DEFAULT_CONFIG.get(section, {}))
            self._data[section][key] = value
            self._flush_locked()

    def _flush_locked(self) -> None:
        """Must be called with self._lock held."""
        if self._profile_name:
            try:
                prof.save_profile(self._profile_name, copy.deepcopy(self._data))
            except Exception:
                pass   # never crash the UI thread on a save error
