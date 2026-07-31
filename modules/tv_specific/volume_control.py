from typing import Optional

from core.adb_handler import ADBHandler


class VolumeControl:
    def __init__(self, config: dict):
        self.config = config
        self.adb = ADBHandler(config)

    def volume_up(self, device_serial: Optional[str] = None) -> bool:
        stdout, stderr, code = self.adb.shell("input keyevent 24", device_serial)
        return code == 0

    def volume_down(self, device_serial: Optional[str] = None) -> bool:
        stdout, stderr, code = self.adb.shell("input keyevent 25", device_serial)
        return code == 0

    def volume_mute(self, device_serial: Optional[str] = None) -> bool:
        stdout, stderr, code = self.adb.shell("input keyevent 164", device_serial)
        return code == 0

    def set_volume_level(self, level: int, device_serial: Optional[str] = None) -> bool:
        if level < 0 or level > 15:
            return False
        stdout, stderr, code = self.adb.shell(f"media volume --set {level}", device_serial)
        return code == 0

    def get_volume_level(self, device_serial: Optional[str] = None) -> Optional[int]:
        stdout, stderr, code = self.adb.shell("media volume --get", device_serial)
        if code == 0 and stdout:
            try:
                return int(stdout.strip())
            except ValueError:
                return None
        return None

    def get_volume_info(self, device_serial: Optional[str] = None) -> str:
        stdout, stderr, code = self.adb.shell("dumpsys audio", device_serial)
        return stdout if code == 0 else ""

    def set_audio_stream_type(self, stream_type: str = "music", device_serial: Optional[str] = None) -> bool:
        stdout, stderr, code = self.adb.shell(f"media volume --stream {stream_type}", device_serial)
        return code == 0