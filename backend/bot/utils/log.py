from datetime import datetime
import os
from colorama import Fore, Style, init

init(autoreset=True)

DEBUG_ENABLED = (os.getenv("BACKEND_DEBUG") or os.getenv("DEBUG") or "false").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}

def log(msg: str, level: str = "info"):
    if level == "debug" and not DEBUG_ENABLED:
        return

    time = datetime.now().strftime("%H:%M:%S")
    levels = {
        "info": Fore.CYAN + "[INFO]",
        "debug": Fore.BLUE + "[DEBUG]",
        "success": Fore.GREEN + "[SUCCESS]",
        "warn": Fore.YELLOW + "[WARN]",
        "error": Fore.RED + "[ERROR]",
        "critical": Fore.MAGENTA + "[CRITICAL]",
    }
    tag = levels.get(level, Fore.WHITE + "[LOG]")
    print(f"{Fore.BLACK}[{time}]{Style.RESET_ALL} {tag} {Fore.WHITE}{msg}{Style.RESET_ALL}")