import subprocess
import re
from typing import List, Optional, Tuple

class ADBHandler:
    def __init__(self, config: dict):
        self.adb_binary = config.get("adb", {}).get("binary_path", "adb")
        self.default_port = config.get("adb", {}).get("default_port", 5555)
        self.connection_timeout = config.get("adb", {}).get("connection_timeout", 15)
        self.max_retries = config.get("adb", {}).get("max_connection_retries", 5)

    def _run_command(self, args: List[str], timeout: int = 30) -> Tuple[str, str, int]:
        cmd = [self.adb_binary] + args
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return process.stdout.strip(), process.stderr.strip(), process.returncode

    def start_server(self) -> bool:
        stdout, stderr, code = self._run_command(["start-server"])
        return code == 0

    def kill_server(self) -> bool:
        stdout, stderr, code = self._run_command(["kill-server"])
        return code == 0

    def list_devices(self) -> List[dict]:
        stdout, stderr, code = self._run_command(["devices", "-l"])
        devices = []
        if code == 0:
            lines = stdout.splitlines()[1:]
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        devices.append({
                            "serial": parts[0],
                            "status": parts[1],
                            "details": " ".join(parts[2:])
                        })
        return devices

    def connect(self, ip: str, port: int = None) -> bool:
        if port is None:
            port = self.default_port
        target = f"{ip}:{port}"
        stdout, stderr, code = self._run_command(["connect", target])
        if code == 0 and ("connected" in stdout.lower() or "already connected" in stdout.lower()):
            return True
        return False

    def disconnect(self, ip: str = None, port: int = None) -> bool:
        if ip and port:
            target = f"{ip}:{port}"
        elif ip:
            target = ip
        else:
            target = "all"
        stdout, stderr, code = self._run_command(["disconnect", target])
        return code == 0

    def shell(self, command: str, device_serial: str = None) -> Tuple[str, str, int]:
        args = ["shell"]
        if device_serial:
            args = ["-s", device_serial] + args
        args.append(command)
        return self._run_command(args)

    def push(self, local_path: str, remote_path: str, device_serial: str = None) -> bool:
        args = []
        if device_serial:
            args = ["-s", device_serial]
        args += ["push", local_path, remote_path]
        stdout, stderr, code = self._run_command(args)
        return code == 0

    def pull(self, remote_path: str, local_path: str, device_serial: str = None) -> bool:
        args = []
        if device_serial:
            args = ["-s", device_serial]
        args += ["pull", remote_path, local_path]
        stdout, stderr, code = self._run_command(args)
        return code == 0

    def install(self, apk_path: str, device_serial: str = None, options: List[str] = None) -> bool:
        args = []
        if device_serial:
            args = ["-s", device_serial]
        args.append("install")
        if options:
            args.extend(options)
        args.append(apk_path)
        stdout, stderr, code = self._run_command(args)
        return code == 0

    def uninstall(self, package: str, device_serial: str = None, keep_data: bool = False) -> bool:
        args = []
        if device_serial:
            args = ["-s", device_serial]
        args.append("uninstall")
        if keep_data:
            args.append("-k")
        args.append(package)
        stdout, stderr, code = self._run_command(args)
        return code == 0

    def tcpip(self, port: int, device_serial: str = None) -> bool:
        args = []
        if device_serial:
            args = ["-s", device_serial]
        args += ["tcpip", str(port)]
        stdout, stderr, code = self._run_command(args)
        return code == 0

    def root(self, device_serial: str = None) -> bool:
        args = []
        if device_serial:
            args = ["-s", device_serial]
        args.append("root")
        stdout, stderr, code = self._run_command(args)
        return code == 0

    def get_property(self, prop: str, device_serial: str = None) -> Optional[str]:
        cmd = f"getprop {prop}"
        stdout, stderr, code = self.shell(cmd, device_serial)
        if code == 0:
            return stdout
        return None

    def set_property(self, prop: str, value: str, device_serial: str = None) -> bool:
        cmd = f"setprop {prop} {value}"
        stdout, stderr, code = self.shell(cmd, device_serial)
        return code == 0

    def is_connected(self, ip: str, port: int = None) -> bool:
        if port is None:
            port = self.default_port
        target = f"{ip}:{port}"
        devices = self.list_devices()
        for device in devices:
            if target in device.get("details", "") or target == device.get("serial", ""):
                return device.get("status") == "device"
        return False

    def get_device_model(self, device_serial: str = None) -> Optional[str]:
        return self.get_property("ro.product.model", device_serial)

    def get_device_brand(self, device_serial: str = None) -> Optional[str]:
        return self.get_property("ro.product.brand", device_serial)

    def get_android_version(self, device_serial: str = None) -> Optional[str]:
        return self.get_property("ro.build.version.release", device_serial)

    def reboot(self, mode: str = "system", device_serial: str = None) -> bool:
        valid_modes = ["system", "recovery", "bootloader", "fastboot"]
        if mode not in valid_modes:
            return False
        if mode == "system":
            cmd = "reboot"
        else:
            cmd = f"reboot {mode}"
        stdout, stderr, code = self.shell(cmd, device_serial)
        return code == 0

    def forward(self, local_port: int, remote_port: int, device_serial: str = None) -> bool:
        args = []
        if device_serial:
            args = ["-s", device_serial]
        args += ["forward", f"tcp:{local_port}", f"tcp:{remote_port}"]
        stdout, stderr, code = self._run_command(args)
        return code == 0

    def reverse(self, remote_port: int, local_port: int, device_serial: str = None) -> bool:
        args = []
        if device_serial:
            args = ["-s", device_serial]
        args += ["reverse", f"tcp:{remote_port}", f"tcp:{local_port}"]
        stdout, stderr, code = self._run_command(args)
        return code == 0