import os
from typing import Optional

from core.adb_handler import ADBHandler


class SystemAppInstall:
    def __init__(self, config: dict):
        self.config = config
        self.adb = ADBHandler(config)

    def install(self, apk_path: str, package_name: str = "c11k_app", device_serial: Optional[str] = None) -> bool:
        if not os.path.exists(apk_path):
            return False
        self.adb.root(device_serial)
        self.adb.shell("mount -o rw,remount /system", device_serial)
        remote_apk = f"/system/app/{package_name}.apk"
        if self.adb.push(apk_path, remote_apk, device_serial):
            self.adb.shell(f"chmod 644 {remote_apk}", device_serial)
            return True
        return False

    def check(self, package_name: str = "c11k_app", device_serial: Optional[str] = None) -> bool:
        remote_apk = f"/system/app/{package_name}.apk"
        stdout, stderr, code = self.adb.shell(f"test -f {remote_apk} && echo 'exists'", device_serial)
        return "exists" in stdout

    def remove(self, package_name: str = "c11k_app", device_serial: Optional[str] = None) -> bool:
        remote_apk = f"/system/app/{package_name}.apk"
        self.adb.shell(f"rm -f {remote_apk}", device_serial)
        return True