import json
import base64
import hashlib
import time
import re
import os
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from ipaddress import ip_address, ip_network

class Utils:
    @staticmethod
    def load_json(file_path: Union[str, Path]) -> Optional[Dict[str, Any]]:
        path = Path(file_path)
        if not path.exists():
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    @staticmethod
    def save_json(file_path: Union[str, Path], data: Dict[str, Any], indent: int = 4) -> bool:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)
            return True
        except Exception:
            return False

    @staticmethod
    def merge_configs(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        result = base.copy()
        for key, value in override.items():
            if isinstance(value, dict) and key in result and isinstance(result[key], dict):
                result[key] = Utils.merge_configs(result[key], value)
            else:
                result[key] = value
        return result

    @staticmethod
    def is_valid_ip(ip: str) -> bool:
        try:
            ip_address(ip)
            return True
        except ValueError:
            return False

    @staticmethod
    def is_valid_port(port: int) -> bool:
        return 0 < port < 65536

    @staticmethod
    def is_valid_subnet(subnet: str) -> bool:
        try:
            ip_network(subnet, strict=False)
            return True
        except ValueError:
            return False

    @staticmethod
    def b64_encode(data: Union[str, bytes]) -> str:
        if isinstance(data, str):
            data = data.encode()
        return base64.b64encode(data).decode()

    @staticmethod
    def b64_decode(data: str) -> str:
        return base64.b64decode(data).decode()

    @staticmethod
    def sha256(data: Union[str, bytes]) -> str:
        if isinstance(data, str):
            data = data.encode()
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def md5(data: Union[str, bytes]) -> str:
        if isinstance(data, str):
            data = data.encode()
        return hashlib.md5(data).hexdigest()

    @staticmethod
    def timestamp() -> int:
        return int(time.time())

    @staticmethod
    def datetime_str(fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
        return datetime.now().strftime(fmt)

    @staticmethod
    def ensure_dir(path: Union[str, Path]) -> Path:
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def truncate_string(s: str, max_len: int = 100, suffix: str = "...") -> str:
        if len(s) <= max_len:
            return s
        return s[:max_len - len(suffix)] + suffix

    @staticmethod
    def extract_ip_from_output(output: str) -> Optional[str]:
        pattern = r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b"
        match = re.search(pattern, output)
        if match:
            ip = match.group(0)
            if Utils.is_valid_ip(ip):
                return ip
        return None

    @staticmethod
    def extract_mac_from_output(output: str) -> Optional[str]:
        pattern = r"([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})"
        match = re.search(pattern, output)
        return match.group(0) if match else None

    @staticmethod
    def parse_key_value_lines(output: str, separator: str = "=") -> Dict[str, str]:
        result = {}
        for line in output.splitlines():
            if separator in line:
                key, value = line.split(separator, 1)
                result[key.strip()] = value.strip()
        return result

    @staticmethod
    def safe_execute(func, *args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception:
            return None

    @staticmethod
    def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
        return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

    @staticmethod
    def size_format(bytes_count: int) -> str:
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if bytes_count < 1024.0:
                return f"{bytes_count:.2f} {unit}"
            bytes_count /= 1024.0
        return f"{bytes_count:.2f} PB"

    @staticmethod
    def create_temp_file(content: str, suffix: str = ".tmp") -> Path:
        temp_dir = Path("/tmp/c11k-tv")
        temp_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{int(time.time())}_{hashlib.md5(content.encode()).hexdigest()[:8]}{suffix}"
        path = temp_dir / filename
        with open(path, "w") as f:
            f.write(content)
        return path

    @staticmethod
    def remove_temp_files(older_than_seconds: int = 3600) -> int:
        temp_dir = Path("/tmp/c11k-tv")
        if not temp_dir.exists():
            return 0
        deleted = 0
        now = time.time()
        for file in temp_dir.iterdir():
            if file.is_file():
                if now - file.stat().st_mtime > older_than_seconds:
                    try:
                        file.unlink()
                        deleted += 1
                    except Exception:
                        pass
        return deleted