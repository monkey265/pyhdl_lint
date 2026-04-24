import sys
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

class Reporter:
    def __init__(self, quiet=False):
        self.quiet = quiet

    def report(self, file_path, violations):
        if not violations:
            if not self.quiet:
                print(f"{Fore.GREEN}[OK] {Style.RESET_ALL}{file_path}: No violations found.")
            return

        print(f"{Fore.RED}[NOK] {Style.RESET_ALL}{file_path}: Found {len(violations)} violations")
        for v in violations:
            print(f"  {v}")
        
    def report_summary(self, total_files, total_violations):
        print(f"\n{Style.BRIGHT}Summary:")
        print(f"  Files checked: {total_files}")
        print(f"  Total violations: {total_violations}")
