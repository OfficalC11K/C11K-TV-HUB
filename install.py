#!/usr/bin/env python3
import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

class C11KInstaller:
    def __init__(self):
        self.os_type = platform.system()
        self.is_kali = self._check_kali()
        self.project_dir = Path(__file__).parent.absolute()

    def _check_kali(self):
        try:
            with open("/etc/os-release", "r") as f:
                return "kali" in f.read().lower()
        except:
            return False

    def _run(self, cmd, error_msg=None):
        print(f"[+] Calistiriliyor: {cmd}")
        try:
            result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
            if result.stdout:
                print(result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            print(f"[-] Hata: {e.stderr if e.stderr else str(e)}")
            if error_msg:
                print(f"[!] {error_msg}")
            return False

    def install_system_packages(self):
        packages = [
            "adb",
            "nmap",
            "metasploit-framework",
            "scrcpy",
            "python3-pip",
            "python3-venv",
            "git",
            "openssl"
        ]
        if self.is_kali:
            cmd = f"sudo apt update && sudo apt install -y {' '.join(packages)}"
        else:
            cmd = f"sudo apt-get update && sudo apt-get install -y {' '.join(packages)}"
        return self._run(cmd, "Sistem paketleri kurulamadi. Manuel kurulum gerekebilir.")

    def install_python_packages(self):
        req_file = self.project_dir / "requirements.txt"
        if not req_file.exists():
            print("[-] requirements.txt bulunamadi.")
            return False
        return self._run(f"pip3 install -r {req_file}", "Python paketleri kurulamadi.")

    def check_adb(self):
        return shutil.which("adb") is not None

    def setup_alias(self):
        alias_cmd = 'alias c11k-tv="python3 ' + str(self.project_dir / "C11K-TV-HUB.py") + '"'
        rc_files = [Path.home() / ".bashrc", Path.home() / ".zshrc"]
        for rc in rc_files:
            if rc.exists():
                with open(rc, "a") as f:
                    f.write(f"\n# C11K-TV-HUB alias\n{alias_cmd}\n")
                print(f"[+] Alias eklendi: {rc}")

    def run(self):
        print("""
╔═══════════════════════════════════════════╗
║   C11K-TV-HUB - Kali Kurulum Aracı        ║
║   Yapımcı: deniz.pro                      ║
╚═══════════════════════════════════════════╝
        """)
        if self.is_kali:
            print("[✓] Kali Linux tespit edildi.")
        else:
            print("[!] Uyari: Bu tool Kali icin optimize edilmistir.")
            if input("Devam et? (y/n): ").lower() != "y":
                sys.exit(1)
        if not self.install_system_packages():
            print("[!] Sistem paketleri kurulumunda sorun yasandi.")
        if not self.install_python_packages():
            print("[!] Python paketleri kurulumunda sorun yasandi.")
        if self.check_adb():
            print("[✓] ADB kurulu.")
        else:
            print("[!] ADB bulunamadi! Lutfen manuel kurun.")
        self.setup_alias()
        print("\n[✓] Kurulum tamamlandi!")
        print("Calistirmak icin: python3 C11K-TV-HUB.py")
        print("veya: c11k-tv (alias)")

if __name__ == "__main__":
    installer = C11KInstaller()
    installer.run()
