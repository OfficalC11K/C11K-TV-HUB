import time
from typing import Optional, Dict, Any, List

from core.adb_handler import ADBHandler
from core.auth_bypass import AuthBypass
from core.network_scanner import NetworkScanner
from core.tv_profiler import TVProfiler
from core.utils import Utils

class Connect:
    def __init__(self, config: dict):
        self.config = config
        self.adb = ADBHandler(config)
        self.scanner = NetworkScanner(config)
        self.bypass = AuthBypass(config)
        self.profiler = TVProfiler(config, self.adb)

    def connect_adb(self, ip: str, port: int = 5555) -> Dict[str, Any]:
        result = {"success": False, "ip": ip, "port": port, "message": "", "device_info": None}
        self.adb.kill_server()
        self.adb.start_server()
        if self.adb.connect(ip, port):
            result["success"] = True
            result["message"] = f"ADB baglantisi kuruldu: {ip}:{port}"
            device_info = self.profiler.get_device_info()
            result["device_info"] = device_info
            return result
        result["message"] = f"ADB baglantisi basarisiz: {ip}:{port}"
        return result

    def connect_with_bypass(self, ip: str, port: int = 5555) -> Dict[str, Any]:
        result = {"success": False, "ip": ip, "port": port, "message": "", "bypass_used": False}
        normal = self.connect_adb(ip, port)
        if normal["success"]:
            result["success"] = True
            result["message"] = normal["message"]
            result["bypass_used"] = False
            return result
        if self.bypass.bypass_connect(ip, port):
            if self.adb.connect(ip, port):
                result["success"] = True
                result["message"] = f"Bypass ile baglanti kuruldu: {ip}:{port}"
                result["bypass_used"] = True
                return result
        result["message"] = "Normal ADB ve bypass denenmesi basarisiz"
        return result

    def discover_and_connect(self, subnet: str = None) -> List[Dict[str, Any]]:
        if subnet is None:
            subnet = self.config.get("network", {}).get("scan_subnet", "192.168.1.0/24")
        results = []
        adb_devices = self.scanner.discover_adb_devices(subnet)
        for device in adb_devices:
            ip = device["ip"]
            port = device["port"]
            conn_result = self.connect_with_bypass(ip, port)
            if conn_result["success"]:
                results.append(conn_result)
        return results

    def disconnect_all(self) -> bool:
        return self.adb.disconnect()