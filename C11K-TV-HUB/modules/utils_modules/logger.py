import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


class Logger:
    def __init__(self, name: str = "C11K-TV-HUB", log_file: Optional[Path] = None, level: str = "INFO"):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        self.logger.handlers.clear()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        if log_file:
            log_file = Path(log_file)
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def set_level(self, level: str) -> None:
        self.logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    def debug(self, message: str) -> None:
        self.logger.debug(message)

    def info(self, message: str) -> None:
        self.logger.info(message)

    def warning(self, message: str) -> None:
        self.logger.warning(message)

    def error(self, message: str) -> None:
        self.logger.error(message)

    def critical(self, message: str) -> None:
        self.logger.critical(message)

    def success(self, message: str) -> None:
        self.logger.info(f"[SUCCESS] {message}")

    def log_exception(self, e: Exception, context: str = "") -> None:
        import traceback
        msg = f"{context}: {str(e)}" if context else str(e)
        self.error(msg)
        self.error(traceback.format_exc())

    def get_logger(self) -> logging.Logger:
        return self.logger