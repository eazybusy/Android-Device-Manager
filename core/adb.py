import subprocess
import sys
import os
import shutil


def _find_adb() -> str:
    found = shutil.which("adb")
    if found:
        return found

    if sys.platform == "win32":
        candidates = [
            os.path.join(
                os.environ.get("LOCALAPPDATA", ""),
                "Android", "Sdk", "platform-tools", "adb.exe"
            ),
            r"C:\platform-tools\adb.exe",
            r"C:\Android\platform-tools\adb.exe",
        ]
    else:
        candidates = [
            "/usr/local/bin/adb",
            "/opt/homebrew/bin/adb",
            os.path.expanduser("~/Library/Android/sdk/platform-tools/adb"),
            os.path.expanduser("~/Android/Sdk/platform-tools/adb"),
            "/usr/bin/adb",
        ]

    for path in candidates:
        if os.path.isfile(path):
            return path

    return "adb"


def _run_kwargs() -> dict:
    if sys.platform == "win32":
        return {"creationflags": subprocess.CREATE_NO_WINDOW}
    return {}


def run(cmd: list[str]) -> tuple[str, str]:
    result = subprocess.run(
        [_find_adb()] + cmd,
        capture_output=True,
        text=True,
        **_run_kwargs()
    )
    return result.stdout.strip(), result.stderr.strip()


def connected_devices() -> list[str]:
    out, _ = run(["devices"])
    lines = out.splitlines()[1:]
    return [l.split("\t")[0] for l in lines if "device" in l]


def send_broadcast(action: str, extras: dict) -> bool:
    cmd = ["shell", "am", "broadcast", "-a", action]
    for key, value in extras.items():
        cmd += ["--es", key, str(value)]
    out, err = run(cmd)
    return "result=0" in out or "Broadcast completed" in out


def set_setting(namespace: str, key: str, value: str) -> bool:
    out, err = run(["shell", "settings", "put", namespace, key, value])
    return err == ""


def install_apk(path: str) -> tuple[bool, str]:
    out, err = run(["install", "-r", path])
    success = "Success" in out
    return success, out or err