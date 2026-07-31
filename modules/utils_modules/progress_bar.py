import sys
from typing import Optional, Any, Iterable, Callable

try:
    from tqdm import tqdm
except ImportError:
    class tqdm:
        def __init__(self, iterable=None, desc=None, total=None, unit=None, leave=True, **kwargs):
            self.iterable = iterable
            self.desc = desc
            self.total = total
            self.unit = unit or "it"
            self.leave = leave
            self._index = 0

        def __iter__(self):
            if self.iterable is None:
                return
            total = self.total if self.total is not None else len(self.iterable)
            for i, item in enumerate(self.iterable):
                self._index = i + 1
                self._print_progress(i + 1, total)
                yield item

        def __enter__(self):
            return self

        def __exit__(self, *args):
            if self.leave:
                print()

        def _print_progress(self, current: int, total: int):
            bar_len = 40
            filled_len = int(bar_len * current / total)
            bar = "█" * filled_len + "░" * (bar_len - filled_len)
            percent = 100 * current / total
            desc = f"{self.desc}: " if self.desc else ""
            sys.stdout.write(f"\r{desc}[{bar}] {percent:.1f}% {current}/{total} {self.unit}")
            sys.stdout.flush()

        def update(self, n: int = 1):
            self._index += n

        def close(self):
            pass


class ProgressBar:
    def __init__(self, desc: str = "Progress", total: int = 100, unit: str = "it", leave: bool = True):
        self.desc = desc
        self.total = total
        self.unit = unit
        self.leave = leave
        self._bar = None

    def __enter__(self):
        self._bar = tqdm(total=self.total, desc=self.desc, unit=self.unit, leave=self.leave)
        return self._bar

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._bar:
            self._bar.close()
            if not self.leave:
                sys.stdout.write("\r" + " " * 80 + "\r")
                sys.stdout.flush()

    def iterate(self, iterable: Iterable[Any]) -> Iterable[Any]:
        return tqdm(iterable, desc=self.desc, unit=self.unit, leave=self.leave)

    def wrap_function(self, func: Callable, *args, **kwargs) -> Any:
        with tqdm(total=100, desc=self.desc, unit="%", leave=self.leave) as pbar:
            try:
                result = func(*args, **kwargs, progress_callback=lambda p: pbar.update(p - pbar.n))
                return result
            except Exception as e:
                pbar.close()
                raise e

    @staticmethod
    def simple_progress(iterable: Iterable[Any], desc: str = "Progress", unit: str = "it") -> Iterable[Any]:
        return tqdm(iterable, desc=desc, unit=unit, leave=True)