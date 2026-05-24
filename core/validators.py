"""
core/validators.py — Input validation for all user-facing fields.
"""
import re
from typing import Optional


def validate_ip(ip: str) -> Optional[str]:
    ip = ip.strip()
    if not ip:
        return None
    if not re.match(r'^(\d{1,3}\.){3}\d{1,3}$', ip):
        return f"IP მისამართი არასწორია: '{ip}'"
    if any(int(p) > 255 for p in ip.split(".")):
        return f"IP range-ი არასწორია: '{ip}' (მაქს. 255 თითო octet-ზე)"
    return None


def validate_port(port: str) -> Optional[str]:
    port = port.strip()
    if not port:
        return None
    try:
        n = int(port)
        if not (1 <= n <= 65535):
            raise ValueError
        return None
    except ValueError:
        return f"Port არასწორია: '{port}' — მნიშვნელობა 1-65535 უნდა იყოს"


def validate_url(url: str) -> Optional[str]:
    url = url.strip()
    if not url:
        return None
    if not (url.startswith("http://") or url.startswith("https://")):
        return f"URL-ი https:// ან http://-ით უნდა იწყებოდეს"
    return None


def validate_package_name(pkg: str) -> Optional[str]:
    pkg = pkg.strip()
    if not pkg:
        return None
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*(\.[a-zA-Z][a-zA-Z0-9_]*){1,}$', pkg):
        return f"Package name არასწორია: '{pkg}'\nმაგ: com.example.myapp"
    return None


def validate_mcc_mnc(code: str, name: str) -> Optional[str]:
    code = code.strip()
    if not code:
        return None
    if not re.match(r'^\d{2,3}$', code):
        return f"{name} არასწორია: '{code}' — 2 ან 3 ციფრი უნდა იყოს"
    return None


def validate_profile_name(name: str) -> Optional[str]:
    name = name.strip()
    if not name:
        return "Profile name ცარიელია."
    if not re.match(r'^[A-Za-z0-9_\- ]{1,64}$', name):
        return (
            f"Profile name-ი სწორი არ არის: '{name}'\n"
            "დასაშვებია: ასოები, ციფრები, _ - და ფართი (მაქს. 64 სიმბოლო)."
        )
    return None
