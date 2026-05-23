"""
ADB კავშირის ლოგიკა — მოგვიანებით დასრულდება.
"""
import subprocess


def run(cmd: list[str]) -> tuple[str, str]:
    """ADB ბრძანების გაშვება. დააბრუნებს (stdout, stderr)."""
    result = subprocess.run(
        ["adb"] + cmd,
        capture_output=True, text=True
    )
    return result.stdout.strip(), result.stderr.strip()


def connected_devices() -> list[str]:
    """დაკავშირებული მოწყობილობების სია."""
    out, _ = run(["devices"])
    lines = out.splitlines()[1:]
    return [l.split("\t")[0] for l in lines if "device" in l]


def send_broadcast(action: str, extras: dict) -> bool:
    """Intent Broadcast გაგზავნა ტელეფონზე."""
    cmd = ["shell", "am", "broadcast", "-a", action]
    for key, value in extras.items():
        cmd += ["--es", key, str(value)]
    out, err = run(cmd)
    return "result=0" in out or "Broadcast completed" in out


def set_setting(namespace: str, key: str, value: str) -> bool:
    """სისტემური სეთინგის შეცვლა (system / global / secure)."""
    out, err = run(["shell", "settings", "put", namespace, key, value])
    return err == ""


def install_apk(path: str) -> tuple[bool, str]:
    """APK-ის ინსტალაცია."""
    out, err = run(["install", "-r", path])
    success = "Success" in out
    return success, out or err
