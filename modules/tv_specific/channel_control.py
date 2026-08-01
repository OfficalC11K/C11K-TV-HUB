from typing import Optional

from core.adb_handler import ADBHandler


class ChannelControl:
    def __init__(self, config: dict):
        self.config = config
        self.adb = ADBHandler(config)

    def channel_up(self, device_serial: Optional[str] = None) -> bool:
        stdout, stderr, code = self.adb.shell("input keyevent 166", device_serial)
        return code == 0

    def channel_down(self, device_serial: Optional[str] = None) -> bool:
        stdout, stderr, code = self.adb.shell("input keyevent 167", device_serial)
        return code == 0

    def goto_channel(self, channel_number: int, device_serial: Optional[str] = None) -> bool:
        digits = str(channel_number)
        for digit in digits:
            keycode = 7 + int(digit)
            self.adb.shell(f"input keyevent {keycode}", device_serial)
        self.adb.shell("input keyevent 66", device_serial)
        return True

    def tv_guide(self, device_serial: Optional[str] = None) -> bool:
        stdout, stderr, code = self.adb.shell("input keyevent 175", device_serial)
        return code == 0

    def tv_info(self, device_serial: Optional[str] = None) -> bool:
        stdout, stderr, code = self.adb.shell("input keyevent 171", device_serial)
        return code == 0

    def switch_input(self, input_type: str = "hdmi1", device_serial: Optional[str] = None) -> bool:
        input_map = {
            "hdmi1": "input keyevent 178 && input keyevent 19 && input keyevent 66",
            "hdmi2": "input keyevent 178 && input keyevent 20 && input keyevent 66",
            "tv": "input keyevent 178 && input keyevent 19 && input keyevent 19 && input keyevent 66",
            "av": "input keyevent 178 && input keyevent 20 && input keyevent 20 && input keyevent 66"
        }
        cmd = input_map.get(input_type.lower(), "input keyevent 178")
        stdout, stderr, code = self.adb.shell(cmd, device_serial)
        return code == 0

    def set_channel_by_am(self, channel: str, device_serial: Optional[str] = None) -> bool:
        am_cmd = f"am broadcast -a android.intent.action.VIEW -d \"tv://{channel}\""
        stdout, stderr, code = self.adb.shell(am_cmd, device_serial)
        return code == 0