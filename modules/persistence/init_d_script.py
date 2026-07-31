from typing import Optional

from core.adb_handler import ADBHandler


class InitDScript:
    def __init__(self, config: dict):
        self.config = config
        self.adb = ADBHandler(config)
        self.init_d_paths = [
            "/etc/init.d/",
            "/system/etc/init.d/",
            "/data/adb/service.d/"
        ]

    def _find_init_d_path(self, device_serial: Optional[str] = None) -> Optional[str]:
        for path in self.init_d_paths:
            stdout, stderr, code = self.adb.shell(f"test -d {path} && echo 'exists'", device_serial)
            if "exists" in stdout:
                return path
        return None

    def install(self, script_content: str, script_name: str = "c11k_persist.sh", device_serial: Optional[str] = None) -> bool:
        init_path = self._find_init_d_path(device_serial)
        if not init_path:
            return False
        remote_tmp = f"/data/local/tmp/{script_name}"
        self.adb.shell(f"echo '{script_content}' > {remote_tmp}", device_serial)
        self.adb.shell(f"chmod 755 {remote_tmp}", device_serial)
        dest_path = f"{init_path}{script_name}"
        self.adb.shell(f"cp {remote_tmp} {dest_path}", device_serial)
        self.adb.shell(f"chmod 755 {dest_path}", device_serial)
        self.adb.shell(f"rm -f {remote_tmp}", device_serial)
        return True

    def check(self, script_name: str = "c11k_persist.sh", device_serial: Optional[str] = None) -> bool:
        init_path = self._find_init_d_path(device_serial)
        if not init_path:
            return False
        stdout, stderr, code = self.adb.shell(f"test -f {init_path}{script_name} && echo 'exists'", device_serial)
        return "exists" in stdout

    def remove(self, script_name: str = "c11k_persist.sh", device_serial: Optional[str] = None) -> bool:
        init_path = self._find_init_d_path(device_serial)
        if not init_path:
            return False
        self.adb.shell(f"rm -f {init_path}{script_name}", device_serial)
        return True