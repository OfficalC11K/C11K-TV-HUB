import sys
from typing import Optional

try:
    from colorama import Fore, Back, Style, init
    init(autoreset=True)
except ImportError:
    class Fore:
        RED = ""
        GREEN = ""
        YELLOW = ""
        BLUE = ""
        MAGENTA = ""
        CYAN = ""
        WHITE = ""
        RESET = ""
    class Back:
        RED = ""
        GREEN = ""
        YELLOW = ""
        BLUE = ""
        MAGENTA = ""
        CYAN = ""
        WHITE = ""
        RESET = ""
    class Style:
        BRIGHT = ""
        DIM = ""
        NORMAL = ""
        RESET_ALL = ""


class ColorOutput:
    @staticmethod
    def print_success(message: str, end: str = "\n") -> None:
        print(f"{Fore.GREEN}[+] {message}{Style.RESET_ALL}", end=end)

    @staticmethod
    def print_error(message: str, end: str = "\n") -> None:
        print(f"{Fore.RED}[-] {message}{Style.RESET_ALL}", end=end, file=sys.stderr)

    @staticmethod
    def print_warning(message: str, end: str = "\n") -> None:
        print(f"{Fore.YELLOW}[!] {message}{Style.RESET_ALL}", end=end)

    @staticmethod
    def print_info(message: str, end: str = "\n") -> None:
        print(f"{Fore.CYAN}[*] {message}{Style.RESET_ALL}", end=end)

    @staticmethod
    def print_debug(message: str, end: str = "\n") -> None:
        print(f"{Fore.MAGENTA}[DEBUG] {message}{Style.RESET_ALL}", end=end)

    @staticmethod
    def print_header(message: str, end: str = "\n") -> None:
        width = 60
        border = "=" * width
        print(f"{Fore.BLUE}{Style.BRIGHT}{border}")
        print(f"{Fore.BLUE}{Style.BRIGHT}{message.center(width)}")
        print(f"{Fore.BLUE}{Style.BRIGHT}{border}{Style.RESET_ALL}", end=end)

    @staticmethod
    def print_table(rows: list, headers: list = None, padding: int = 2) -> None:
        if not rows:
            return
        if headers is None:
            headers = [str(i) for i in range(len(rows[0]))]
        col_widths = [len(str(h)) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(str(cell)))
        total_width = sum(col_widths) + (padding * 2 * len(col_widths)) + (len(col_widths) - 1)
        print(f"{Fore.CYAN}{'=' * total_width}{Style.RESET_ALL}")
        header_line = ""
        for i, h in enumerate(headers):
            header_line += f" {str(h).ljust(col_widths[i] + padding * 2)}"
        print(f"{Fore.WHITE}{Style.BRIGHT}{header_line}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'-' * total_width}{Style.RESET_ALL}")
        for row in rows:
            line = ""
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    line += f" {str(cell).ljust(col_widths[i] + padding * 2)}"
            print(line)
        print(f"{Fore.CYAN}{'=' * total_width}{Style.RESET_ALL}")

    @staticmethod
    def input_prompt(prompt: str, color: str = "yellow") -> str:
        color_map = {
            "red": Fore.RED,
            "green": Fore.GREEN,
            "yellow": Fore.YELLOW,
            "blue": Fore.BLUE,
            "cyan": Fore.CYAN,
            "white": Fore.WHITE,
            "magenta": Fore.MAGENTA
        }
        c = color_map.get(color.lower(), Fore.YELLOW)
        return input(f"{c}{prompt}{Style.RESET_ALL}")

    @staticmethod
    def clear_screen() -> None:
        import os
        os.system("cls" if os.name == "nt" else "clear")