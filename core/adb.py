"""
core/adb.py — ADB communication layer
"""

import subprocess
import sys
import os
import re
import shutil
from typing import NamedTuple
from core.logger import get_logger

_log = get_logger("adb")

_ADB_PATH_CACHE: str | None = None
_ADB_CACHE_LOCK = None   # lazy init (avoids import-time threading cost)

DEFAULT_TIMEOUT = 15
INSTALL_TIMEOUT = 120

BROADCAST_ERROR_PREFIXES = (
    "error:",
    "exception",
    "failed to",
    "unable to",
    "permission denied",
    "java.lang.",
)


# ── Result type ────────────────────────────────────────────────────────────────

class AdbResult(NamedTuple):
    stdout: str
    stderr: str
    returncode: int

    @property
    def ok(self) -> bool:
        if self.returncode != 0:
            return False
        if self.stderr.lower().startswith("error:"):
            return False
        return True

    @property
    def combined(self) -> str:
        parts = [p for p in (self.stdout, self.stderr) if p]
        return "\n".join(parts)

    @property
    def timed_out(self) -> bool:
        return self.returncode == -2

    @property
    def adb_missing(self) -> bool:
        return self.returncode == -1


# ── ADB binary discovery ───────────────────────────────────────────────────────

def _get_lock():
    global _ADB_CACHE_LOCK
    if _ADB_CACHE_LOCK is None:
        import threading
        _ADB_CACHE_LOCK = threading.Lock()
    return _ADB_CACHE_LOCK


def _find_adb() -> str:
    """Thread-safe ADB binary lookup with caching."""
    global _ADB_PATH_CACHE
    with _get_lock():
        if _ADB_PATH_CACHE:
            return _ADB_PATH_CACHE

        found = shutil.which("adb")
        if found:
            _ADB_PATH_CACHE = found
            return found

        if sys.platform == "win32":
            candidates = [
                os.path.join(os.environ.get("LOCALAPPDATA", ""),
                             "Android", "Sdk", "platform-tools", "adb.exe"),
                os.path.join(os.environ.get("APPDATA", ""),
                             "Android", "Sdk", "platform-tools", "adb.exe"),
                r"C:\platform-tools\adb.exe",
                r"C:\Android\platform-tools\adb.exe",
                r"C:\tools\platform-tools\adb.exe",
            ]
        else:
            candidates = [
                "/usr/local/bin/adb",
                "/opt/homebrew/bin/adb",
                os.path.expanduser("~/Library/Android/sdk/platform-tools/adb"),
                os.path.expanduser("~/Android/Sdk/platform-tools/adb"),
                os.path.expanduser("~/.local/share/android-sdk/platform-tools/adb"),
                "/usr/bin/adb",
            ]

        for path in candidates:
            if os.path.isfile(path):
                _ADB_PATH_CACHE = path
                return path

        _ADB_PATH_CACHE = "adb"
        return "adb"


def reset_adb_cache() -> None:
    global _ADB_PATH_CACHE
    with _get_lock():
        _ADB_PATH_CACHE = None


def _win_flags() -> dict:
    if sys.platform == "win32":
        return {"creationflags": subprocess.CREATE_NO_WINDOW}
    return {}


# ── Core runner ───────────────────────────────────────────────────────────────

def run(
    cmd: list[str],
    timeout: int = DEFAULT_TIMEOUT,
    serial: str | None = None,
) -> AdbResult:
    adb_path = _find_adb()
    full_cmd = [adb_path]
    if serial:
        full_cmd += ["-s", serial]
    full_cmd += cmd

    _log.debug("CMD: %s (timeout=%ds)", " ".join(full_cmd), timeout)

    try:
        proc = subprocess.run(
            full_cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            **_win_flags(),
        )
        result = AdbResult(proc.stdout.strip(), proc.stderr.strip(), proc.returncode)
        if not result.ok:
            _log.warning("FAIL rc=%d stderr=%r stdout=%r",
                         result.returncode, result.stderr[:200], result.stdout[:200])
        return result

    except FileNotFoundError:
        msg = (
            f"ADB ვერ მოიძებნა: '{adb_path}'. "
            "გადმოწერე: https://developer.android.com/tools/releases/platform-tools"
        )
        _log.error("ADB not found: %s", adb_path)
        return AdbResult("", msg, -1)

    except subprocess.TimeoutExpired:
        msg = (
            f"Timeout ({timeout}s) — ტელეფონი არ პასუხობს. "
            "სცადე: adb kill-server და შეაერთე კვლავ."
        )
        _log.error("TIMEOUT (%ds): %s", timeout, " ".join(full_cmd))
        return AdbResult("", msg, -2)

    except Exception as exc:
        _log.exception("Unexpected error running ADB")
        return AdbResult("", str(exc), -3)


# ── Server management ─────────────────────────────────────────────────────────

def ensure_server_running() -> bool:
    """
    Start ADB daemon if not already running.
    Safe to call repeatedly — fast no-op when server is already up.
    """
    result = run(["start-server"], timeout=10)
    ok = result.returncode == 0
    if ok:
        _log.debug("ADB server OK")
    else:
        _log.warning("adb start-server: %s", result.combined)
    return ok


# ── Device discovery ──────────────────────────────────────────────────────────

def connect_and_classify() -> tuple[list[dict], list[dict]]:
    """
    Single 'adb devices -l' call.
    Returns: (authorized_devices, unauthorized_devices)
    Each dict: {"serial": str, "state": str, "model": str}
    """
    result = run(["devices", "-l"])
    authorized, unauthorized = [], []

    for line in result.stdout.splitlines()[1:]:
        line = line.strip()
        if not line:
            continue

        tab = line.find("\t")
        if tab != -1:
            serial = line[:tab].strip()
            rest   = line[tab + 1:].strip()
        else:
            parts = line.split(None, 1)
            if len(parts) < 2:
                continue
            serial, rest = parts[0].strip(), parts[1].strip()

        tokens = rest.split()
        if not tokens:
            continue
        state = tokens[0]

        model = ""
        for tok in tokens[1:]:
            if tok.startswith("model:"):
                model = tok[6:].replace("_", " ")
                break

        if state == "device":
            authorized.append({"serial": serial, "state": state, "model": model})
        elif state in ("unauthorized", "offline", "no", "no permissions"):
            unauthorized.append({"serial": serial, "state": state, "model": ""})

    _log.debug("Devices — authorized: %d, unauthorized: %d",
               len(authorized), len(unauthorized))
    return authorized, unauthorized


def connected_devices(include_unauthorized: bool = False) -> list[dict]:
    """Convenience wrapper around connect_and_classify()."""
    auth, unauth = connect_and_classify()
    if include_unauthorized:
        return auth + unauth
    return auth


def first_serial() -> str | None:
    auth, _ = connect_and_classify()
    return auth[0]["serial"] if auth else None


def get_device_info(serial: str | None = None) -> str:
    """
    Returns human-readable device info.
    Single shell session — 3 getprop calls batched via semicolon.
    """
    result = run(
        ["shell",
         "getprop ro.product.brand; "
         "getprop ro.product.model; "
         "getprop ro.build.version.release"],
        serial=serial,
        timeout=8,
    )
    lines = [l.strip() for l in result.stdout.splitlines() if l.strip()]
    brand   = lines[0] if len(lines) > 0 else ""
    model   = lines[1] if len(lines) > 1 else "Unknown"
    version = lines[2] if len(lines) > 2 else "?"

    full_model = (
        f"{brand} {model}"
        if brand and brand.lower() not in model.lower()
        else model
    )
    parts = [full_model, f"Android {version}"]
    if serial:
        parts.append(serial)
    return "  |  ".join(parts)


def adb_available() -> bool:
    result = run(["version"], timeout=5)
    return "Android Debug Bridge" in result.stdout


# ── Broadcast ─────────────────────────────────────────────────────────────────

def send_broadcast(
    action: str,
    extras: dict,
    serial: str | None = None,
) -> tuple[bool, int, str]:
    """
    Returns (success, result_code, message).
      result_code 0   — receiver handled intent OK
      result_code -1  — no registered receiver (app not installed / wrong action)
      result_code -99 — ADB-level error
    """
    cmd = ["shell", "am", "broadcast", "-a", action]
    for key, value in extras.items():
        cmd += ["--es", key, str(value)]

    result = run(cmd, serial=serial)
    _log.debug("broadcast %s extras=%s", action, extras)

    if result.returncode < 0:
        return False, -99, result.stderr

    # Check stderr for actual error prefixes only (not content-based false positives)
    err_lower = result.stderr.lower().strip()
    if any(err_lower.startswith(p) for p in BROADCAST_ERROR_PREFIXES):
        return False, -99, result.stderr or result.stdout

    match = re.search(r"result=(-?\d+)", result.stdout)
    if match:
        code = int(match.group(1))
        _log.debug("broadcast result_code=%d", code)
        return code == 0, code, result.stdout

    if "Broadcast completed" in result.stdout:
        return True, 0, result.stdout

    combined_lower = result.combined.lower()
    if "no devices" in combined_lower or "device not found" in combined_lower:
        return False, -99, "მოწყობილობა ვერ მოიძებნა."

    _log.warning("broadcast uncertain result: %s", result.combined[:200])
    return False, -99, result.combined or "უცნობი შეცდომა"


# ── Settings ──────────────────────────────────────────────────────────────────

_SLEEP_MAP = {
    "15 sec":  "15000",
    "30 sec":  "30000",
    "1 min":   "60000",
    "2 min":   "120000",
    "5 min":   "300000",
    "Never":   "2147483647",
}


def set_setting(
    namespace: str,
    key: str,
    value: str,
    serial: str | None = None,
) -> tuple[bool, str]:
    result = run(["shell", "settings", "put", namespace, key, value], serial=serial)
    combined = result.combined.lower()

    if any(kw in combined for kw in (
        "permission denied", "securityexception", "securitiesexception",
        "requires android.permission", "not allowed", "exception",
    )):
        _log.warning("settings put %s/%s DENIED: %s", namespace, key, result.combined[:200])
        return False, result.combined

    if result.returncode != 0:
        return False, result.stderr or result.stdout or "returncode != 0"

    _log.debug("settings put %s/%s = %s OK", namespace, key, value)
    return True, ""


def set_sleep_timeout(label: str, serial: str | None = None) -> tuple[bool, str]:
    ms = _SLEEP_MAP.get(label, "30000")
    return set_setting("system", "screen_off_timeout", ms, serial=serial)


def set_developer_mode(enabled: bool, serial: str | None = None) -> tuple[bool, str]:
    value = "1" if enabled else "0"
    ok, err = set_setting("global", "development_settings_enabled", value, serial=serial)
    if not ok:
        return False, (
            f"{err}\n\n"
            "Android 8+ requires WRITE_SECURE_SETTINGS.\n"
            "გამოსავალი: adb shell pm grant <your.package> "
            "android.permission.WRITE_SECURE_SETTINGS"
        )
    return True, ""


def set_device_name(name: str, serial: str | None = None) -> tuple[bool, str]:
    ok, err = set_setting("global", "device_name", name, serial=serial)
    if ok:
        return True, ""

    ok2, err2 = set_setting("secure", "bluetooth_name", name, serial=serial)
    if ok2:
        return True, "device_name წვდომა შეიზღუდა — bluetooth_name განახლდა."

    return False, (
        f"device_name: {err}\n"
        f"bluetooth_name: {err2}\n\n"
        "Android 8+-ზე WRITE_SECURE_SETTINGS ნებართვა სჭირდება.\n"
        "გამოსავალი: Settings -> Developer Options -> Device Name."
    )


# ── APK Installation ──────────────────────────────────────────────────────────

def install_apk(
    path: str,
    serial: str | None = None,
    allow_test: bool = True,
    allow_downgrade: bool = False,
) -> tuple[bool, str]:
    if not path or not path.strip():
        return False, "APK ფაილის გზა არ არის მითითებული."

    path = path.strip()

    if not os.path.isfile(path):
        return False, f"ფაილი ვერ მოიძებნა:\n{path}"

    if not path.lower().endswith(".apk"):
        return False, f"ფაილი არ არის APK ფორმატი:\n{path}"

    cmd = ["install", "-r"]
    if allow_test:
        cmd.append("-t")
    if allow_downgrade:
        cmd.append("-d")
    cmd.append(path)

    _log.info("Installing APK: %s", path)
    result = run(cmd, timeout=INSTALL_TIMEOUT, serial=serial)
    combined = result.combined

    if "Success" in result.stdout:
        _log.info("APK install SUCCESS: %s", path)
        return True, "APK წარმატებით დაინსტალირდა."

    error_map = {
        "INSTALL_FAILED_ALREADY_EXISTS":
            "APK უკვე დაინსტალირებულია (სხვა signature-ით).\n"
            "გამოსავალი: ჯერ წაშალე: adb uninstall <package>",
        "INSTALL_FAILED_INVALID_APK":
            "APK ფაილი დაზიანებულია ან სწორი format-ი არ არის.",
        "INSTALL_FAILED_INSUFFICIENT_STORAGE":
            "ტელეფონზე ადგილი არ არის.",
        "INSTALL_FAILED_UPDATE_INCOMPATIBLE":
            "Signature განსხვავდება. ჯერ წაშალე ძველი:\nadb uninstall <package>",
        "INSTALL_FAILED_OLDER_SDK":
            "APK-ს minSdkVersion მაღალია ამ ტელეფონისთვის.",
        "INSTALL_FAILED_NEWER_SDK":
            "APK-ს targetSdkVersion ძალიან მაღალია.",
        "INSTALL_FAILED_CPU_ABI_INCOMPATIBLE":
            "CPU ABI არ ემთხვევა (ARM vs x86).",
        "INSTALL_FAILED_TEST_ONLY":
            "APK test-only-ია. -t ფლაგი ჩართულია ავტომატურად — სცადე ხელახლა.",
        "INSTALL_FAILED_VERSION_DOWNGRADE":
            "ვერსია დაბალია. Downgrade-ისთვის ჩართე 'Allow version downgrade'.",
        "INSTALL_FAILED_USER_RESTRICTED":
            "ტელეფონი ბლოკავს გარე წყაროებიდან ინსტალაციას.\n"
            "Settings -> Security -> Install Unknown Apps -> ჩართე.",
        "INSTALL_FAILED_ABORTED":
            "ინსტალაცია გაუქმდა.",
        "INSTALL_FAILED_INVALID_URI":
            "APK ფაილის გზა არასწორია.",
        "INSTALL_FAILED_DUPLICATE_PACKAGE":
            "ამ package name-ით სხვა APK უკვე დაინსტალირებულია.",
        "INSTALL_FAILED_MISSING_SHARED_LIBRARY":
            "საჭირო shared library არ არის.",
        "INSTALL_FAILED_REPLACE_COULDNT_DELETE":
            "ძველი APK-ს წაშლა ვერ მოხდა.",
        "INSTALL_FAILED_DEXOPT":
            "DEX optimization ვერ შესრულდა.",
        "INSTALL_FAILED_CONFLICTING_PROVIDER":
            "ContentProvider conflict.",
        "INSTALL_FAILED_MISSING_FEATURE":
            "ტელეფონს სჭირდება feature, რომელიც არ არის.",
        "INSTALL_FAILED_VERIFICATION_FAILURE":
            "APK verification ვერ გაიარა.",
        "INSTALL_FAILED_UID_CHANGED":
            "UID conflict — ჯერ წაშალე ძველი version.",
        "INSTALL_PARSE_FAILED_NOT_APK":
            "ფაილი APK არ არის.",
        "INSTALL_PARSE_FAILED_MANIFEST_MALFORMED":
            "AndroidManifest.xml დაზიანებულია.",
    }

    for code, msg in error_map.items():
        if code in combined:
            _log.warning("APK install FAIL (%s): %s", code, path)
            return False, msg

    combined_lower = combined.lower()
    if "no devices" in combined_lower or "device not found" in combined_lower:
        return False, "ADB მოწყობილობა ვერ მოიძებნა. შეამოწმე USB კავშირი."

    _log.error("APK install UNKNOWN FAIL: %s", combined[:300])
    return False, combined or "APK ინსტალაცია ვერ მოხდა — უცნობი შეცდომა."
