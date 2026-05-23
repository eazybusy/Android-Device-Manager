import copy
from core import profiles as prof

DEFAULT_CONFIG = prof.DEFAULT_CONFIG


class Storage:
    def __init__(self):
        self._profile_name: str = ""
        self._data: dict = {}

    def set_profile(self, name: str) -> None:
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
        if section not in self._data:
            self._data[section] = dict(DEFAULT_CONFIG.get(section, {}))
        return self._data[section]

    def set_value(self, section: str, key: str, value) -> None:
        if section not in self._data:
            self._data[section] = dict(DEFAULT_CONFIG.get(section, {}))
        self._data[section][key] = value
        self._flush()

    def _flush(self):
        if self._profile_name:
            prof.save_profile(self._profile_name, self._data)