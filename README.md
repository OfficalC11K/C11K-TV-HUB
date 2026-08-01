# C11K-TV-HUB – Android TV Exploitation Framework

> Red Team toolkit to remotely exploit Android TV boxes, smart TVs, and STBs via ADB, Metasploit, and custom CVE exploits.

**Maintained by:** OfficalC11K  
**Discord:** deniz.pro

---

## 📌 Overview

C11K-TV-HUB is a modular exploitation framework designed for authorized penetration testing and Red Team operations against Android-based TV devices. It automates:

- Network discovery of ADB-enabled devices
- Authentication bypass (CVE-2026-0073)
- Bootloader privilege escalation (CVE-2025-4321)
- Payload generation & injection (Meterpreter, reverse shells)
- Persistence via ADB key injection, init.d scripts, and system app installation
- TV-specific controls: HDMI-CEC, volume, channel switching, screencast, audio stealing, and remote key simulation

The tool is written in Python 3 and optimized for **Kali Linux**.

---

## 🚀 Features

- **Auto-discovery** – Scan local network for open ADB ports (5555, dynamic ranges)
- **Smart Connect** – Try normal ADB, fallback to TLS bypass (CVE-2026-0073)
- **Vulnerability Scanner** – Check for known CVEs (CVE-2026-0073, CVE-2025-4321, CVE-2023-5678)
- **Payload Factory** – Generate Meterpreter APK, reverse shells, and SSH installers
- **Privilege Escalation** – Automatic root detection and exploitation (su, adb root, bootloader unlock)
- **Persistence** – Inject ADB keys, init.d scripts, and install as system app
- **TV Control** – HDMI-CEC, volume, channel, remote key events, screencast, audio recording
- **Post-Exploitation** – Screenshots, screen recording, SMS/contacts/call log dumps, file pulling

---

## 📦 Requirements

- Kali Linux (recommended) – also works on Debian/Ubuntu with manual setup
- Python **3.10+**
- `adb` – Android Debug Bridge
- `nmap` – network scanner
- `metasploit-framework` – for payload generation
- `scrcpy` – screen mirroring
- Python packages: see `requirements.txt`

---

## 🔧 Installation (Kali Linux) – Step by Step

### 1. Clone the repository
```bash
git clone https://github.com/OfficalC11K/C11K-TV-HUB.git
cd C11K-TV-HUB
sudo python3 install.py
python3 C11K-TV-HUB.py