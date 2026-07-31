import time
from typing import Optional, Dict, Any

from core.adb_handler import ADBHandler
from core.utils import Utils


class Screencast:
    def __init__(self, config: dict):
        self.config = config
        self.adb = ADBHandler(config)
        self.output_dir = Utils.ensure_dir("outputs/screencast")
        self.quality = config.get("tv_control", {}).get("screencast", {}).get("quality", "high")
        self.framerate = config.get("tv_control", {}).get("screencast", {}).get("framerate", 30)

    def take_screenshot(self, device_serial: Optional[str] = None) -> Optional[str]:
        remote_path = "/data/local/tmp/screenshot.png"
        local_path = str(self.output_dir / f"screenshot_{Utils.timestamp()}.png")
        self.adb.shell(f"screencap -p {remote_path}", device_serial)
        if self.adb.pull(remote_path, local_path, device_serial):
            self.adb.shell(f"rm -f {remote_path}", device_serial)
            return local_path
        return None

    def record_screen(self, duration_seconds: int = 30, device_serial: Optional[str] = None) -> Optional[str]:
        remote_path = "/data/local/tmp/screenrecord.mp4"
        local_path = str(self.output_dir / f"screenrecord_{Utils.timestamp()}.mp4")
        bitrate = "4M" if self.quality == "high" else "2M"
        framerate = self.framerate
        cmd = f"screenrecord --time-limit {duration_seconds} --bit-rate {bitrate} --size 1920x1080 {remote_path}"
        self.adb.shell(f"nohup {cmd} > /dev/null 2>&1 &", device_serial)
        time.sleep(duration_seconds + 2)
        if self.adb.pull(remote_path, local_path, device_serial):
            self.adb.shell(f"rm -f {remote_path}", device_serial)
            return local_path
        return None

    def stop_recording(self, device_serial: Optional[str] = None) -> bool:
        stdout, stderr, code = self.adb.shell("pkill -f screenrecord", device_serial)
        return code == 0

    def mirror_screen(self, device_serial: Optional[str] = None) -> bool:
        try:
            import subprocess
            cmd = ["scrcpy"]
            if device_serial:
                cmd.extend(["-s", device_serial])
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception:
            return False

    def get_screen_size(self, device_serial: Optional[str] = None) -> Optional[str]:
        stdout, stderr, code = self.adb.shell("wm size", device_serial)
        if code == 0:
            for line in stdout.splitlines():
                if "Physical size:" in line:
                    return line.split(":")[1].strip()
        return None

    def set_screen_resolution(self, width: int, height: int, device_serial: Optional[str] = None) -> bool:
        stdout, stderr, code = self.adb.shell(f"wm size {width}x{height}", device_serial)
        return code == 0

    def reset_screen_resolution(self, device_serial: Optional[str] = None) -> bool:
        stdout, stderr, code = self.adb.shell("wm size reset", device_serial)
        return code == 0