from typing import List, Dict, Any, Optional

from core.network_scanner import NetworkScanner
from core.adb_handler import ADBHandler
from core.utils import Utils


class NetworkMapper:
    def __init__(self, config: dict):
        self.config = config
        self.scanner = NetworkScanner(config)
        self.adb = ADBHandler(config)

    def scan_subnet(self, subnet: Optional[str] = None) -> List[Dict[str, Any]]:
        if subnet is None:
            subnet = self.config.get("network", {}).get("scan_subnet", "192.168.1.0/24")
        return self.scanner.scan_network(subnet)

    def ping_sweep(self, subnet: Optional[str] = None) -> List[str]:
        if subnet is None:
            subnet = self.config.get("network", {}).get("scan_subnet", "192.168.1.0/24")
        return self.scanner.ping_sweep(subnet)

    def discover_adb(self, subnet: Optional[str] = None) -> List[Dict[str, Any]]:
        if subnet is None:
            subnet = self.config.get("network", {}).get("scan_subnet", "192.168.1.0/24")
        return self.scanner.discover_adb_devices(subnet)

    def scan_ports(self, ip: str, ports: Optional[List[int]] = None) -> Dict[int, Dict[str, Any]]:
        if ports is None:
            ports = self.config.get("network", {}).get("scanning", {}).get("interesting_ports", [5555, 5556, 5557, 5558, 5559])
        return self.scanner.scan_ports(ip, ports)

    def arp_scan(self, subnet: Optional[str] = None) -> List[Dict[str, str]]:
        if subnet is None:
            subnet = self.config.get("network", {}).get("scan_subnet", "192.168.1.0/24")
        return self.scanner.arp_scan(subnet)

    def get_local_ip(self) -> Optional[str]:
        return self.scanner.get_local_ip()

    def get_network_range(self) -> str:
        return self.scanner.get_network_range()