from pathlib import Path
from typing import List

from colorama import Fore, Style, init
from pyhdl_lint.core.rule_base import Severity, Violation

# Initialize colorama
init(autoreset=True)

class Reporter:
    def __init__(self, quiet: bool = False) -> None:
        self.quiet = quiet

    def report(self, file_path: Path, violations: List[Violation]) -> None:
        if not violations:
            if not self.quiet:
                print(f"{Fore.GREEN}[OK] {Style.RESET_ALL}{file_path}: No violations found.")
            return

        has_error = any(v.severity == Severity.ERROR for v in violations)
        status_color = Fore.RED if has_error else Fore.YELLOW
        status_text = "[NOK]" if has_error else "[WARN]"

        print(f"{status_color}{status_text} {Style.RESET_ALL}{file_path}: Found {len(violations)} violations")
        for v in violations:
            color = Fore.YELLOW if v.severity == Severity.WARNING else Fore.RED
            print(f"  {color}{v}{Style.RESET_ALL}")
        
    def report_summary(self, total_files: int, total_violations: int) -> None:
        print(f"\n{Style.BRIGHT}Summary:")
        print(f"  Files checked: {total_files}")
        print(f"  Total violations: {total_violations}")
