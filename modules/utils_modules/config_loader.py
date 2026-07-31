import json
from pathlib import Path
from typing import Dict, Any, Optional

from core.utils import Utils

class ConfigLoader:
    def __init__(self, base_dir: Optional[Path] = None):
        if base_dir is None:
            base_dir = Path.cwd()
        self.config_dir = base_dir / "config"
        self.default_file = self.config_dir / "default_config.json"
        self.network_file = self.config_dir / "network_config.json"
        self.user_file = self.config_dir / "user_config.json"
        self._config_cache: Optional[Dict[str, Any]] = None

    def load_default(self) -> Dict[str, Any]:
        data = Utils.load_json(self.default_file)
        if data is None:
            return {}
        return data

    def load_network(self) -> Dict[str, Any]:
        data = Utils.load_json(self.network_file)
        if data is None:
            return {}
        return data

    def load_user(self) -> Dict[str, Any]:
        data = Utils.load_json(self.user_file)
        if data is None:
            return {}
        return data

    def load_all(self) -> Dict[str, Any]:
        if self._config_cache is not None:
            return self._config_cache
        default = self.load_default()
        network = self.load_network()
        user = self.load_user()
        merged = Utils.merge_configs(default, network)
        merged = Utils.merge_configs(merged, user)
        self._config_cache = merged
        return merged

    def get(self, key: str, default: Any = None) -> Any:
        config = self.load_all()
        keys = key.split(".")
        current = config
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default
        return current

    def set_user_config(self, key: str, value: Any) -> bool:
        config = self.load_user()
        keys = key.split(".")
        current = config
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value
        return Utils.save_json(self.user_file, config)

    def reload(self) -> Dict[str, Any]:
        self._config_cache = None
        return self.load_all()

    def validate(self) -> bool:
        try:
            config = self.load_all()
            if not config:
                return False
            if "general" not in config:
                return False
            if "network" not in config:
                return False
            return True
        except Exception:
            return False