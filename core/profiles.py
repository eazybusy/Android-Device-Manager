"""
core/profiles.py — Profile storage (JSON files under ~/.adm/profiles/)
"""

import json
import os
import re
import copy

PROFILES_DIR = os.path.join(os.path.expanduser("~"), ".adm", "profiles")

DEFAULT_CONFIG = {
    "system": {
        "dev_mode":    "On",
        "sleep":       "30 sec",
        "device_name": "",
    },
    "network": {
        "apn_name": "", "apn":  "", "mcc":      "", "mnc":  "",
        "proxy":    "", "port": "", "api_ip":   "", "api_port": "", "api_key": "",
    },
    "camera": {
        "resolution": "1920x1080", "fps": "30", "flash": "Auto",
    },
    "webview": {
        "url": "", "js": True, "cookies": True, "cache": "LOAD_DEFAULT",
    },
    "apps": {
        "apk_path": "", "pkg": "", "pref": "", "val": "",
    },
}

# Only alphanumeric, space, hyphen, underscore — prevents path traversal
_SAFE_NAME = re.compile(r'^[A-Za-z0-9_\- ]{1,64}$')


def _validate_name(name: str) -> str:
    name = name.strip()
    if not name:
        raise ValueError("Profile name ცარიელია.")
    if not _SAFE_NAME.match(name):
        raise ValueError(
            f"Profile name-ი სწორი არ არის: '{name}'\n"
            "დასაშვებია: ასოები, ციფრები, _ - და ფართი (მაქს. 64 სიმბოლო)."
        )
    return name


def ensure_dir() -> None:
    os.makedirs(PROFILES_DIR, exist_ok=True)


def list_profiles() -> list[str]:
    ensure_dir()
    try:
        names = [f[:-5] for f in os.listdir(PROFILES_DIR) if f.endswith(".json")]
    except OSError:
        return []
    return sorted(names)


def profile_path(name: str) -> str:
    name = _validate_name(name)
    resolved_dir  = os.path.realpath(PROFILES_DIR)
    ensure_dir()
    path = os.path.realpath(os.path.join(resolved_dir, f"{name}.json"))
    # Guard: path must still be inside PROFILES_DIR after symlink resolution
    if not path.startswith(resolved_dir + os.sep) and path != resolved_dir:
        raise ValueError("Path traversal attempt blocked.")
    return path


def create_profile(name: str) -> bool:
    ensure_dir()
    path = profile_path(name)
    if os.path.exists(path):
        return False
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(DEFAULT_CONFIG, f, ensure_ascii=False, indent=2)
    return True


def delete_profile(name: str) -> bool:
    path = profile_path(name)
    if os.path.exists(path):
        os.remove(path)
        return True
    return False


def load_profile(name: str) -> dict:
    data = copy.deepcopy(DEFAULT_CONFIG)
    path = profile_path(name)

    if not os.path.isfile(path):
        return data

    try:
        with open(path, "r", encoding="utf-8") as f:
            saved = json.load(f)
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        return data

    for section, values in saved.items():
        if section == "_enabled":
            data["_enabled"] = values
        elif section in data and isinstance(values, dict):
            data[section].update(values)

    return data


def save_profile(name: str, data: dict) -> None:
    ensure_dir()
    path = profile_path(name)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def rename_profile(old_name: str, new_name: str) -> bool:
    old_path = profile_path(old_name)
    new_path = profile_path(new_name)
    if not os.path.exists(old_path) or os.path.exists(new_path):
        return False
    import shutil
    shutil.move(old_path, new_path)   # atomic-er than os.rename across drives
    return True
