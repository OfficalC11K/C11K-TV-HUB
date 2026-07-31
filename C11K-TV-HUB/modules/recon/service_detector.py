import socket
from typing import Dict, Any, Optional, List

from core.network_scanner import NetworkScanner
from core.adb_handler import ADBHandler


class ServiceDetector:
    def __init__(self, config: dict):
        self.config = config
        self.scanner = NetworkScanner(config)
        self.adb = ADBHandler(config)

    def detect_adb(self, ip: str, port: int = 5555) -> Dict[str, Any]:
        result = {"ip": ip, "port": port, "service": "adb", "open": False, "fingerprint": ""}
        if self.scanner.check_port(ip, port):
            result["open"] = True
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                sock.connect((ip, port))
                sock.send(b"\x00\x00\x00\x08\x00\x00\x00\x01")
                response = sock.recv(1024)
                sock.close()
                if response:
                    result["fingerprint"] = response.hex()[:50]
            except Exception:
                pass
        return result

    def detect_http(self, ip: str, port: int = 8080) -> Dict[str, Any]:
        result = {"ip": ip, "port": port, "service": "http", "open": False, "server": ""}
        if self.scanner.check_port(ip, port):
            result["open"] = True
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                sock.connect((ip, port))
                sock.send(b"HEAD / HTTP/1.0\r\n\r\n")
                response = sock.recv(1024).decode(errors="ignore")
                sock.close()
                for line in response.splitlines():
                    if "Server:" in line:
                        result["server"] = line.replace("Server:", "").strip()
                        break
            except Exception:
                pass
        return result

    def detect_telnet(self, ip: str, port: int = 23) -> Dict[str, Any]:
        result = {"ip": ip, "port": port, "service": "telnet", "open": False, "banner": ""}
        if self.scanner.check_port(ip, port):
            result["open"] = True
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                sock.connect((ip, port))
                response = sock.recv(1024).decode(errors="ignore")
                sock.close()
                result["banner"] = response[:100]
            except Exception:
                pass
        return result

    def detect_ssh(self, ip: str, port: int = 22) -> Dict[str, Any]:
        result = {"ip": ip, "port": port, "service": "ssh", "open": False, "banner": ""}
        if self.scanner.check_port(ip, port):
            result["open"] = True
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                sock.connect((ip, port))
                response = sock.recv(1024).decode(errors="ignore")
                sock.close()
                result["banner"] = response[:100]
            except Exception:
                pass
        return result

    def detect_all(self, ip: str, ports: Optional[List[int]] = None) -> List[Dict[str, Any]]:
        if ports is None:
            ports = [5555, 8080, 23, 22, 80, 443, 5556, 5557]
        results = []
        for port in ports:
            if port == 5555 or port == 5556 or port == 5557:
                results.append(self.detect_adb(ip, port))
            elif port == 8080 or port == 80 or port == 443:
                results.append(self.detect_http(ip, port))
            elif port == 23:
                results.append(self.detect_telnet(ip, port))
            elif port == 22:
                results.append(self.detect_ssh(ip, port))
            else:
                if self.scanner.check_port(ip, port):
                    results.append({"ip": ip, "port": port, "service": "unknown", "open": True})
        return results