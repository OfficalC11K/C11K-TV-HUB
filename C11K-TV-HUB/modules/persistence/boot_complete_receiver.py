from typing import Optional

from core.adb_handler import ADBHandler


class BootCompleteReceiver:
    def __init__(self, config: dict):
        self.config = config
        self.adb = ADBHandler(config)

    def create_receiver_manifest(self, package_name: str = "com.c11k.agent", service_name: str = "com.c11k.agent.BootReceiver") -> str:
        return f'''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="{package_name}">
    <application>
        <receiver android:name="{service_name}" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.BOOT_COMPLETED" />
                <action android:name="android.intent.action.QUICKBOOT_POWERON" />
                <category android:name="android.intent.category.DEFAULT" />
            </intent-filter>
        </receiver>
    </application>
</manifest>'''

    def inject_receiver(self, manifest_content: str, device_serial: Optional[str] = None) -> bool:
        remote_path = "/data/local/tmp/AndroidManifest.xml"
        self.adb.shell(f"echo '{manifest_content}' > {remote_path}", device_serial)
        self.adb.shell("mkdir -p /data/local/tmp/receiver", device_serial)
        self.adb.shell("mv /data/local/tmp/AndroidManifest.xml /data/local/tmp/receiver/", device_serial)
        return True

    def create_receiver_class(self, package_name: str = "com.c11k.agent", service_name: str = "BootReceiver", start_activity: str = "MainActivity") -> str:
        return f'''package {package_name};

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.os.Build;
import android.util.Log;

public class {service_name} extends BroadcastReceiver {{
    @Override
    public void onReceive(Context context, Intent intent) {{
        if (Intent.ACTION_BOOT_COMPLETED.equals(intent.getAction())) {{
            Intent i = new Intent(context, {start_activity}.class);
            i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            context.startActivity(i);
        }}
    }}
}}'''

    def inject_java_class(self, class_content: str, device_serial: Optional[str] = None) -> bool:
        remote_path = "/data/local/tmp/receiver/BootReceiver.java"
        self.adb.shell(f"echo '{class_content}' > {remote_path}", device_serial)
        return True

    def apply(self, package_name: str = "com.c11k.agent", device_serial: Optional[str] = None) -> bool:
        manifest = self.create_receiver_manifest(package_name)
        if not self.inject_receiver(manifest, device_serial):
            return False
        java_class = self.create_receiver_class(package_name)
        if not self.inject_java_class(java_class, device_serial):
            return False
        self.adb.shell("chmod -R 755 /data/local/tmp/receiver", device_serial)
        return True