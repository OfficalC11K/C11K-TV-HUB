import time
from typing import Optional, List, Dict, Any

from core.adb_handler import ADBHandler
from core.utils import Utils


class RemoteControl:
    def __init__(self, config: dict):
        self.config = config
        self.adb = ADBHandler(config)
        self.key_delay_ms = self.config.get("tv_control", {}).get("remote", {}).get("key_delay_ms", 100)

    def send_key(self, keycode: int, device_serial: Optional[str] = None) -> bool:
        stdout, stderr, code = self.adb.shell(f"input keyevent {keycode}", device_serial)
        if code == 0 and self.key_delay_ms > 0:
            time.sleep(self.key_delay_ms / 1000.0)
        return code == 0

    def send_key_sequence(self, keycodes: List[int], device_serial: Optional[str] = None) -> bool:
        for keycode in keycodes:
            if not self.send_key(keycode, device_serial):
                return False
        return True

    def send_text(self, text: str, device_serial: Optional[str] = None) -> bool:
        escaped = text.replace("'", "\\'")
        stdout, stderr, code = self.adb.shell(f"input text '{escaped}'", device_serial)
        return code == 0

    def press_power(self, device_serial: Optional[str] = None) -> bool:
        return self.send_key(26, device_serial)

    def press_home(self, device_serial: Optional[str] = None) -> bool:
        return self.send_key(3, device_serial)

    def press_back(self, device_serial: Optional[str] = None) -> bool:
        return self.send_key(4, device_serial)

    def press_menu(self, device_serial: Optional[str] = None) -> bool:
        return self.send_key(82, device_serial)

    def press_enter(self, device_serial: Optional[str] = None) -> bool:
        return self.send_key(66, device_serial)

    def press_dpad(self, direction: str, device_serial: Optional[str] = None) -> bool:
        map = {"up": 19, "down": 20, "left": 21, "right": 22, "center": 23}
        keycode = map.get(direction.lower())
        if keycode is None:
            return False
        return self.send_key(keycode, device_serial)

    def press_volume(self, action: str, device_serial: Optional[str] = None) -> bool:
        map = {"up": 24, "down": 25, "mute": 164}
        keycode = map.get(action.lower())
        if keycode is None:
            return False
        return self.send_key(keycode, device_serial)

    def long_press_key(self, keycode: int, duration_ms: int = 500, device_serial: Optional[str] = None) -> bool:
        cmd = f"input keyevent --longpress {keycode}"
        stdout, stderr, code = self.adb.shell(cmd, device_serial)
        if code == 0 and duration_ms > 0:
            time.sleep(duration_ms / 1000.0)
        return code == 0