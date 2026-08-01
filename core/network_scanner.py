import ipaddress
import socket
import subprocess
from typing import List, Dict, Optional, Tuple, Any
import nmap

class NetworkScanner:
    def __init__(self, config: dict):
        self.config = config
        self.nmap_binary = config.get("nmap", {}).get("binary_path", "nmap")
        self.default_args = config.get("nmap", {}).get("default_args", "-sV --open -T4 --min-rate=1000")
        self.interesting_ports = config.get("scanning", {}).get("interesting_ports", [5555, 5556, 5557, 5558, 5559, 4444, 8080, 8000])
        self.subnet = config.get("scanning", {}).get("subnet", "192.168.1.0/24")
        self.timeout = config.get("scanning", {}).get("timeout_seconds", 30)
        self.nm = nmap.PortScanner()

    def get_local_ip(self) -> Optional[str]:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return None

    def get_network_range(self, ip: str = None, subnet_mask: str = "255.255.255.0") -> str:
        if ip is None:
            ip = self.get_local_ip()
        if ip is None:
            return self.subnet
        network = ipaddress.IPv4Network(f"{ip}/{subnet_mask}", strict=False)
        return str(network)

    def scan_ports(self, ip: str, ports: List[int] = None) -> Dict[int, Dict[str, Any]]:
        if ports is None:
            ports = self.interesting_ports
        port_str = ",".join(str(p) for p in ports)
        args = f"-p {port_str} --open -T4"
        result = {}
        try:
            self.nm.scan(ip, arguments=args, timeout=self.timeout)
            if ip in self.nm.all_hosts():
                host = self.nm[ip]
                if "tcp" in host:
                    for port, data in host["tcp"].items():
                        if data.get("state") == "open":
                            result[port] = {
                                "state": "open",
                                "service": data.get("name", "unknown"),
                                "product": data.get("product", ""),
                                "version": data.get("version", ""),
                                "extra": data.get("extrainfo", "")
                            }
        except Exception:
            pass
        return result

    def scan_host(self, ip: str) -> Dict[str, Any]:
        result = {
            "ip": ip,
            "hostname": "",
            "os": "",
            "ports": {},
            "mac": "",
            "vendor": "",
            "up": False
        }
        try:
            self.nm.scan(ip, arguments="-O -sV -p- --open -T4", timeout=self.timeout)
            if ip in self.nm.all_hosts():
                host = self.nm[ip]
                result["up"] = True
                if "hostname" in host and host["hostname"]:
                    result["hostname"] = host["hostname"]
                if "osclass" in host:
                    result["os"] = host["osclass"][0].get("osfamily", "")
                if "addresses" in host:
                    result["mac"] = host["addresses"].get("mac", "")
                    result["vendor"] = host["vendor"].get(result["mac"], "") if "vendor" in host else ""
                if "tcp" in host:
                    for port, data in host["tcp"].items():
                        if data.get("state") == "open":
                            result["ports"][port] = {
                                "state": "open",
                                "service": data.get("name", "unknown"),
                                "product": data.get("product", ""),
                                "version": data.get("version", "")
                            }
        except Exception:
            pass
        return result

    def scan_network(self, subnet: str = None) -> List[Dict[str, Any]]:
        if subnet is None:
            subnet = self.subnet
        results = []
        try:
            self.nm.scan(hosts=subnet, arguments="-sn -T4", timeout=self.timeout)
            for host in self.nm.all_hosts():
                if self.nm[host].state() == "up":
                    ip = host
                    hostname = ""
                    mac = ""
                    vendor = ""
                    if "hostname" in self.nm[host]:
                        hostname = self.nm[host]["hostname"]
                    if "addresses" in self.nm[host]:
                        mac = self.nm[host]["addresses"].get("mac", "")
                        vendor = self.nm[host].get("vendor", {}).get(mac, "")
                    results.append({
                        "ip": ip,
                        "hostname": hostname,
                        "mac": mac,
                        "vendor": vendor,
                        "up": True
                    })
        except Exception:
            pass
        return results

    def ping_sweep(self, subnet: str = None) -> List[str]:
        if subnet is None:
            subnet = self.subnet
        up_hosts = []
        try:
            self.nm.scan(hosts=subnet, arguments="-sn -T4", timeout=self.timeout)
            for host in self.nm.all_hosts():
                if self.nm[host].state() == "up":
                    up_hosts.append(host)
        except Exception:
            pass
        return up_hosts

    def discover_adb_devices(self, subnet: str = None) -> List[Dict[str, Any]]:
        if subnet is None:
            subnet = self.subnet
        results = []
        hosts = self.ping_sweep(subnet)
        for ip in hosts:
            ports = self.scan_ports(ip)
            adb_ports = {p: d for p, d in ports.items() if p in self.interesting_ports}
            if adb_ports:
                for port, data in adb_ports.items():
                    results.append({
                        "ip": ip,
                        "port": port,
                        "service": data.get("service", "adb"),
                        "product": data.get("product", ""),
                        "version": data.get("version", "")
                    })
        return results

    def check_port(self, ip: str, port: int, timeout: int = 3) -> bool:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((ip, port))
            sock.close()
            return True
        except Exception:
            return False

    def get_mac_vendor(self, mac: str) -> str:
        vendor_map = {
            "00:15:5d": "sony",
            "00:1a:11": "xiaomi",
            "00:24:8c": "nvidia",
            "00:08:22": "philips",
            "00:0c:8e": "samsung",
            "00:1e:8c": "lg",
            "00:04:4b": "amlogic",
            "00:0a:2b": "mediatek",
            "00:1b:21": "realtek"
        }
        prefix = mac[:8] if mac else ""
        return vendor_map.get(prefix, "unknown")

    def arp_scan(self, subnet: str = None) -> List[Dict[str, str]]:
        if subnet is None:
            subnet = self.subnet
        results = []
        try:
            cmd = ["arp-scan", "--localnet" if subnet == "auto" else subnet]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            lines = proc.stdout.splitlines()
            for line in lines:
                parts = line.split()
                if len(parts) >= 3:
                    ip = parts[0]
                    mac = parts[1]
                    vendor = " ".join(parts[2:])
                    results.append({
                        "ip": ip,
                        "mac": mac,
                        "vendor": vendor
                    })
        except Exception:
            pass
        return results