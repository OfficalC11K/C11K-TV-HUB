import json
import re
from pathlib import Path
from typing import Optional, Dict, Any, List

class TVProfiler:
    def __init__(self, config: dict, adb_handler):
        self.config = config
        self.adb = adb_handler
        self.data_dir = Path("data")
        self.models_file = self.data_dir / "tv_models.json"
        self.models_db = self._load_models()

    def _load_models(self) -> Dict[str, Any]:
        if self.models_file.exists():
            with open(self.models_file, "r") as f:
                data = json.load(f)
                return data.get("models", {})
        return {}

    def get_device_info(self, device_serial: str = None) -> Dict[str, Any]:
        info = {}
        props = [
            "ro.product.model",
            "ro.product.brand",
            "ro.product.manufacturer",
            "ro.build.version.release",
            "ro.build.version.sdk",
            "ro.build.fingerprint",
            "ro.product.device",
            "ro.board.platform",
            "ro.hardware"
        ]
        for prop in props:
            value = self.adb.get_property(prop, device_serial)
            if value:
                key = prop.split(".")[-1]
                info[key] = value
        info["android_version"] = info.get("release", "unknown")
        info["sdk_level"] = int(info.get("sdk", "0")) if info.get("sdk", "").isdigit() else 0
        info["model_lower"] = info.get("model", "").lower()
        info["brand_lower"] = info.get("brand", "").lower()
        info["manufacturer_lower"] = info.get("manufacturer", "").lower()
        return info

    def get_hardware_info(self, device_serial: str = None) -> Dict[str, Any]:
        hardware = {}
        stdout, stderr, code = self.adb.shell("cat /proc/cpuinfo", device_serial)
        if code == 0:
            hardware["cpu_info"] = stdout
            for line in stdout.splitlines():
                if "processor" in line:
                    hardware["cpu_cores"] = len(re.findall(r"processor\s+:\s+\d+", stdout))
        stdout, stderr, code = self.adb.shell("cat /proc/meminfo", device_serial)
        if code == 0:
            mem_match = re.search(r"MemTotal:\s+(\d+)", stdout)
            if mem_match:
                hardware["ram_kb"] = int(mem_match.group(1))
        stdout, stderr, code = self.adb.shell("getprop ro.sf.lcd_density", device_serial)
        if code == 0 and stdout:
            hardware["lcd_density"] = stdout
        stdout, stderr, code = self.adb.shell("wm size", device_serial)
        if code == 0:
            size_match = re.search(r"Physical size:\s+(\d+x\d+)", stdout)
            if size_match:
                hardware["resolution"] = size_match.group(1)
        stdout, stderr, code = self.adb.shell("getprop ro.product.display.resolution", device_serial)
        if code == 0 and stdout:
            hardware["display_resolution"] = stdout
        return hardware

    def get_network_info(self, device_serial: str = None) -> Dict[str, Any]:
        network = {}
        stdout, stderr, code = self.adb.shell("ip addr show", device_serial)
        if code == 0:
            network["ip_interfaces"] = stdout
        stdout, stderr, code = self.adb.shell("getprop net.wlan0.dns1", device_serial)
        if code == 0 and stdout:
            network["dns"] = stdout
        stdout, stderr, code = self.adb.shell("getprop net.wlan0.gw", device_serial)
        if code == 0 and stdout:
            network["gateway"] = stdout
        stdout, stderr, code = self.adb.shell("getprop wifi.interface", device_serial)
        if code == 0 and stdout:
            network["wifi_interface"] = stdout
        return network

    def get_adb_status(self, device_serial: str = None) -> Dict[str, Any]:
        status = {"adb_enabled": False, "rooted": False, "wireless_debugging": False}
        stdout, stderr, code = self.adb.shell("getprop persist.adb.tcp.port", device_serial)
        if code == 0 and stdout and stdout != "0":
            status["adb_enabled"] = True
            status["adb_port"] = int(stdout) if stdout.isdigit() else 5555
        stdout, stderr, code = self.adb.shell("getprop ro.secure", device_serial)
        if code == 0 and stdout == "0":
            status["rooted"] = True
        stdout, stderr, code = self.adb.shell("getprop service.adb.tcp.port", device_serial)
        if code == 0 and stdout and stdout != "0":
            status["wireless_debugging"] = True
            status["wireless_port"] = int(stdout) if stdout.isdigit() else 0
        stdout, stderr, code = self.adb.shell("which su", device_serial)
        if code == 0 and stdout:
            status["has_su"] = True
        return status

    def identify_model(self, device_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not device_info:
            return None
        model = device_info.get("model_lower", "")
        brand = device_info.get("brand_lower", "")
        manufacturer = device_info.get("manufacturer_lower", "")
        for key, model_data in self.models_db.items():
            if "models" in model_data:
                for m in model_data["models"]:
                    if m.lower() in model or model in m.lower():
                        return model_data
            if "brands" in model_data:
                for b in model_data["brands"]:
                    if b.lower() in brand or brand in b.lower():
                        return model_data
            if "manufacturers" in model_data:
                for m in model_data["manufacturers"]:
                    if m.lower() in manufacturer or manufacturer in m.lower():
                        return model_data
        return None

    def get_model_vulnerabilities(self, model_data: Dict[str, Any]) -> List[str]:
        if not model_data:
            return []
        return model_data.get("cves", [])

    def is_root_available(self, device_serial: str = None) -> bool:
        status = self.get_adb_status(device_serial)
        return status.get("rooted", False) or status.get("has_su", False)

    def get_full_profile(self, device_serial: str = None) -> Dict[str, Any]:
        device_info = self.get_device_info(device_serial)
        hardware = self.get_hardware_info(device_serial)
        network = self.get_network_info(device_serial)
        adb_status = self.get_adb_status(device_serial)
        model_data = self.identify_model(device_info)
        profile = {
            "device_info": device_info,
            "hardware": hardware,
            "network": network,
            "adb_status": adb_status,
            "model_data": model_data,
            "vulnerabilities": self.get_model_vulnerabilities(model_data) if model_data else [],
            "is_rooted": self.is_root_available(device_serial)
        }
        return profile