#!/usr/bin/env python3
"""
Comprehensive Code Quality Analysis Script
Runs all quality checks: formatting, linting, type checking, complexity, duplicates, security
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class QualityChecker:
    """Orchestrates all code quality checks"""

    def __init__(self, fix: bool = False, verbose: bool = False):
        self.fix = fix
        self.verbose = verbose
        self.results: Dict[str, Tuple[int, str]] = {}
        self.root = Path(__file__).parent

    def run_command(self, name: str, cmd: List[str], allow_failure: bool = False) -> bool:
        """Run a command and store results"""
        print(f"\n{'='*80}")
        print(f"Running: {name}")
        print(f"{'='*80}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=not self.verbose,
                text=True,
                cwd=self.root,
            )

            if self.verbose or result.returncode != 0:
                if result.stdout:
                    print(result.stdout)
                if result.stderr:
                    print(result.stderr, file=sys.stderr)

            self.results[name] = (result.returncode, "✓ PASSED" if result.returncode == 0 else "✗ FAILED")

            if result.returncode != 0 and not allow_failure:
                return False
            return True

        except FileNotFoundError:
            self.results[name] = (-1, "✗ TOOL NOT FOUND")
            print(f"Error: Tool not found. Install with: pip install -r requirements_analysis.txt")
            return allow_failure

        except Exception as e:
            self.results[name] = (-1, f"✗ ERROR: {e}")
            return allow_failure

    def check_formatting(self) -> bool:
        """Check code formatting with Black"""
        cmd = ["black", "--check", "--diff", "."] if not self.fix else ["black", "."]
        return self.run_command("Black (Formatting)", cmd)

    def check_imports(self) -> bool:
        """Check import ordering with isort"""
        cmd = ["isort", "--check-only", "--diff", "."] if not self.fix else ["isort", "."]
        return self.run_command("isort (Import Sorting)", cmd)

    def check_linting_pylint(self) -> bool:
        """Run Pylint checks"""
        cmd = [
            "pylint",
            "--rcfile=.pylintrc",
            "--load-plugins=pylint_custom_checkers",
            "agents/", "core/", "mcp/",
        ]
        return self.run_command("Pylint (Custom Rules)", cmd, allow_failure=True)

    def check_linting_flake8(self) -> bool:
        """Run Flake8 checks"""
        cmd = ["flake8", "."]
        return self.run_command("Flake8 (Style + Bugs)", cmd, allow_failure=True)

    def check_types(self) -> bool:
        """Run MyPy type checking"""
        cmd = ["mypy", "agents/", "core/", "mcp/", "--config-file=pyproject.toml"]
        return self.run_command("MyPy (Type Checking)", cmd, allow_failure=True)

    def check_duplicates(self) -> bool:
        """Run JSCPD duplicate detection"""
        cmd = ["npm", "run", "check:duplicates"]
        return self.run_command("JSCPD (Duplicate Code)", cmd, allow_failure=True)

    def check_security(self) -> bool:
        """Run Bandit security checks"""
        cmd = ["bandit", "-c", ".bandit.yaml", "-r", "agents/", "core/", "mcp/"]
        return self.run_command("Bandit (Security)", cmd, allow_failure=True)

    def check_complexity(self) -> bool:
        """Run Radon complexity analysis"""
        cmd = ["radon", "cc", ".", "--min", "B", "--show-complexity"]
        return self.run_command("Radon CC (Complexity)", cmd, allow_failure=True)

    def check_maintainability(self) -> bool:
        """Run Radon maintainability index"""
        cmd = ["radon", "mi", ".", "--min", "B", "--show"]
        return self.run_command("Radon MI (Maintainability)", cmd, allow_failure=True)

    def check_dead_code(self) -> bool:
        """Run Vulture dead code detection"""
        cmd = ["vulture", ".", "--min-confidence", "80"]
        return self.run_command("Vulture (Dead Code)", cmd, allow_failure=True)

    def print_summary(self):
        """Print summary of all checks"""
        print(f"\n{'='*80}")
        print("SUMMARY")
        print(f"{'='*80}\n")

        passed = 0
        failed = 0

        for name, (code, status) in self.results.items():
            print(f"{status:20} {name}")
            if code == 0:
                passed += 1
            else:
                failed += 1

        print(f"\n{'='*80}")
        print(f"Total: {len(self.results)} checks | Passed: {passed} | Failed: {failed}")
        print(f"{'='*80}\n")

        return failed == 0

    def run_all(self) -> bool:
        """Run all quality checks"""
        print("\n🔍 Starting Comprehensive Code Quality Analysis...\n")

        # Order matters: fix formatting first
        checks = [
            ("Formatting", self.check_formatting),
            ("Import Sorting", self.check_imports),
            ("Linting (Pylint)", self.check_linting_pylint),
            ("Linting (Flake8)", self.check_linting_flake8),
            ("Type Checking", self.check_types),
            ("Duplicate Detection", self.check_duplicates),
            ("Security Analysis", self.check_security),
            ("Complexity Analysis", self.check_complexity),
            ("Maintainability Index", self.check_maintainability),
            ("Dead Code Detection", self.check_dead_code),
        ]

        for name, check_fn in checks:
            try:
                check_fn()
            except KeyboardInterrupt:
                print("\n\n⚠️  Analysis interrupted by user")
                return False
            except Exception as e:
                print(f"\n❌ Unexpected error in {name}: {e}")
                self.results[name] = (-1, f"✗ ERROR: {e}")

        return self.print_summary()


def main():
    parser = argparse.ArgumentParser(
        description="Run comprehensive code quality checks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_quality_checks.py              # Run all checks
  python run_quality_checks.py --fix        # Run checks and auto-fix issues
  python run_quality_checks.py --verbose    # Show detailed output
  python run_quality_checks.py --fix -v     # Fix issues with verbose output
        """
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Automatically fix issues where possible (formatting, imports)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed output from all tools"
    )

    args = parser.parse_args()

    checker = QualityChecker(fix=args.fix, verbose=args.verbose)
    success = checker.run_all()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
