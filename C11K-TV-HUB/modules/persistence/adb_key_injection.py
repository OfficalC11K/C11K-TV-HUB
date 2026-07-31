import os
from pathlib import Path
from typing import Optional

from core.adb_handler import ADBHandler


class ADBKeyInjection:
    def __init__(self, config: dict):
        self.config = config
        self.adb = ADBHandler(config)

    def _generate_adb_key(self) -> bool:
        key_dir = Path.home() / ".android"
        key_dir.mkdir(parents=True, exist_ok=True)
        try:
            import subprocess
            subprocess.run(
                ["adb", "keygen", str(key_dir / "adbkey")],
                check=True,
                capture_output=True
            )
            return True
        except Exception:
            return False

    def _get_public_key(self) -> Optional[str]:
        key_path = Path.home() / ".android" / "adbkey.pub"
        if not key_path.exists():
            if not self._generate_adb_key():
                return None
        try:
            with open(key_path, "r") as f:
                return f.read().strip()
        except Exception:
            return None

    def inject(self, device_serial: Optional[str] = None) -> bool:
        public_key = self._get_public_key()
        if not public_key:
            return False
        remote_path = "/data/misc/adb/adb_keys"
        cmd = f"echo '{public_key}' >> {remote_path}"
        stdout, stderr, code = self.adb.shell(cmd, device_serial)
        return code == 0

    def check(self, device_serial: Optional[str] = None) -> bool:
        stdout, stderr, code = self.adb.shell("cat /data/misc/adb/adb_keys", device_serial)
        if code == 0 and stdout:
            return True
        return False

    def remove(self, device_serial: Optional[str] = None) -> bool:
        stdout, stderr, code = self.adb.shell("rm -f /data/misc/adb/adb_keys", device_serial)
        return code == 0