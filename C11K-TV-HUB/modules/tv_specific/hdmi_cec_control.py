from typing import Optional

from core.adb_handler import ADBHandler


class HDMICECControl:
    def __init__(self, config: dict):
        self.config = config
        self.adb = ADBHandler(config)

    def is_cec_enabled(self, device_serial: Optional[str] = None) -> bool:
        stdout, stderr, code = self.adb.shell("getprop persist.sys.hdmi.cec.enabled", device_serial)
        return code == 0 and stdout == "1"

    def enable_cec(self, device_serial: Optional[str] = None) -> bool:
        stdout, stderr, code = self.adb.shell("setprop persist.sys.hdmi.cec.enabled 1", device_serial)
        return code == 0

    def disable_cec(self, device_serial: Optional[str] = None) -> bool:
        stdout, stderr, code = self.adb.shell("setprop persist.sys.hdmi.cec.enabled 0", device_serial)
        return code == 0

    def tv_power_on(self, device_serial: Optional[str] = None) -> bool:
        stdout, stderr, code = self.adb.shell("input keyevent 26", device_serial)
        return code == 0

    def tv_power_off(self, device_serial: Optional[str] = None) -> bool:
        stdout, stderr, code = self.adb.shell("input keyevent 26", device_serial)
        return code == 0

    def switch_hdmi_input(self, hdmi_port: int = 1, device_serial: Optional[str] = None) -> bool:
        if hdmi_port < 1 or hdmi_port > 4:
            return False
        cmd = f"am broadcast -a android.intent.action.VIEW -d \"hdmi://{hdmi_port}\""
        stdout, stderr, code = self.adb.shell(cmd, device_serial)
        return code == 0

    def get_cec_devices(self, device_serial: Optional[str] = None) -> str:
        stdout, stderr, code = self.adb.shell("dumpsys hdmi_control", device_serial)
        return stdout if code == 0 else ""

    def send_cec_command(self, command: str, device_serial: Optional[str] = None) -> bool:
        stdout, stderr, code = self.adb.shell(f"am broadcast -a com.example.CEC_COMMAND --es command \"{command}\"", device_serial)
        return code == 0