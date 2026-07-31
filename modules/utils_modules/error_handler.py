import sys
import traceback
from typing import Callable, Any, Optional, Type, Tuple

from .logger import Logger
from .color_output import ColorOutput


class ErrorHandler:
    def __init__(self, logger: Optional[Logger] = None):
        self.logger = logger
        self.color = ColorOutput()

    def handle_exception(self, e: Exception, context: str = "") -> None:
        error_msg = f"{context}: {str(e)}" if context else str(e)
        if self.logger:
            self.logger.error(error_msg)
            self.logger.error(traceback.format_exc())
        self.color.print_error(error_msg)

    def safe_execute(self, func: Callable, *args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self.handle_exception(e, f"Error in {func.__name__}")
            return None

    def safe_execute_with_fallback(self, func: Callable, fallback: Any, *args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self.handle_exception(e, f"Error in {func.__name__}")
            return fallback

    def retry_on_exception(self, func: Callable, retries: int = 3, delay_seconds: float = 1.0, *args, **kwargs) -> Any:
        import time
        last_exception = None
        for attempt in range(retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < retries:
                    time.sleep(delay_seconds)
                    if self.logger:
                        self.logger.warning(f"Retry {attempt + 1}/{retries} for {func.__name__}")
                else:
                    self.handle_exception(e, f"All {retries} retries failed for {func.__name__}")
                    raise last_exception
        return None

    def ignore_exception(self, func: Callable, *args, **kwargs) -> None:
        try:
            func(*args, **kwargs)
        except Exception:
            pass

    def set_global_exception_handler(self) -> None:
        def global_handler(exc_type: Type[BaseException], exc_value: BaseException, exc_traceback: Any) -> None:
            self.color.print_error(f"Unhandled {exc_type.__name__}: {exc_value}")
            if self.logger:
                self.logger.error(f"Unhandled {exc_type.__name__}: {exc_value}")
                self.logger.error("".join(traceback.format_tb(exc_traceback)))
            sys.__excepthook__(exc_type, exc_value, exc_traceback)

        sys.excepthook = global_handler