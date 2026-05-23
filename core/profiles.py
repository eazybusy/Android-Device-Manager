import json
import os

PROFILES_DIR = os.path.join(os.path.expanduser("~"), ".adm", "profiles")

DEFAULT_CONFIG = {
    "system": {
        "dev_mode": "On",
        "sleep": "30 sec"
    },
    "network": {
        "apn_name": "", "apn": "", "mcc": "", "mnc": "",
        "proxy": "", "port": "", "api_ip": "", "api_port": "", "api_key": ""
    },
    "camera": {
        "resolution": "1920x1080", "fps": "30", "flash": "Auto"
    },
    "webview": {
        "url": "", "js": True, "cookies": True, "cache": "LOAD_DEFAULT"
    },
    "apps": {
        "apk_path": "", "pkg": "", "pref": "", "val": ""
    }
}


def ensure_dir():
    os.makedirs(PROFILES_DIR, exist_ok=True)


def list_profiles() -> list[str]:
    ensure_dir()
    names = []
    for f in os.listdir(PROFILES_DIR):
        if f.endswith(".json"):
            names.append(f[:-5])
    return sorted(names)


def profile_path(name: str) -> str:
    return os.path.join(PROFILES_DIR, f"{name}.json")


def create_profile(name: str) -> bool:
    ensure_dir()
    path = profile_path(name)
    if os.path.exists(path):
        return False
    with open(path, "w", encoding="utf-8") as f:
        json.dump(DEFAULT_CONFIG, f, ensure_ascii=False, indent=2)
    return True


def delete_profile(name: str) -> bool:
    path = profile_path(name)
    if os.path.exists(path):
        os.remove(path)
        return True
    return False


def load_profile(name: str) -> dict:
    import copy
    path = profile_path(name)
    data = copy.deepcopy(DEFAULT_CONFIG)
    if os.path.isfile(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                saved = json.load(f)
            for section, values in saved.items():
                if section in data and isinstance(values, dict):
                    data[section].update(values)
        except (json.JSONDecodeError, OSError):
            pass
    return data


def save_profile(name: str, data: dict):
    ensure_dir()
    path = profile_path(name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)