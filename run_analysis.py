#!/usr/bin/env python3
"""
OMA Code Analysis Runner
Runs all code quality and duplicate detection tools
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
import json
from datetime import datetime


class CodeAnalyzer:
    """Orchestrates all code analysis tools"""

    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.reports_dir = self.root_dir / "reports"
        self.reports_dir.mkdir(exist_ok=True)
        self.results: Dict[str, dict] = {}

    def run_jscpd(self) -> Tuple[bool, str]:
        """Run duplicate code detection"""
        print("\n🔍 Running duplicate code detection (jscpd)...")

        try:
            result = subprocess.run(
                ["npm", "run", "check:duplicates"],
                cwd=self.root_dir,
                capture_output=True,
                text=True,
                timeout=120
            )

            success = result.returncode == 0
            output = result.stdout + result.stderr

            # Parse jscpd report if available
            jscpd_report = self.reports_dir / "jscpd" / "jscpd-report.json"
            if jscpd_report.exists():
                with open(jscpd_report, 'r', encoding='utf-8') as f:
                    self.results['jscpd'] = json.load(f)

            return success, output

        except subprocess.TimeoutExpired:
            return False, "jscpd analysis timed out"
        except Exception as e:
            return False, f"Error running jscpd: {str(e)}"

    def run_pylint(self) -> Tuple[bool, str]:
        """Run Pylint with custom checkers"""
        print("\n🔍 Running Pylint with custom checkers...")

        try:
            # Find all Python files
            python_files = list(self.root_dir.glob("**/*.py"))
            python_files = [
                f for f in python_files
                if not any(exclude in str(f) for exclude in
                          ['venv', 'env', '.venv', '__pycache__', 'node_modules', 'outputs'])
            ]

            if not python_files:
                return True, "No Python files to analyze"

            result = subprocess.run(
                [
                    sys.executable, "-m", "pylint",
                    "--rcfile=.pylintrc",
                    "--load-plugins=pylint_custom_checkers",
                    "--output-format=json",
                ] + [str(f) for f in python_files],
                cwd=self.root_dir,
                capture_output=True,
                text=True,
                timeout=300
            )

            # Pylint returns non-zero for warnings, so we don't fail on that
            output = result.stdout

            # Parse JSON output
            try:
                if output.strip():
                    self.results['pylint'] = json.loads(output)
                else:
                    self.results['pylint'] = []
            except json.JSONDecodeError:
                self.results['pylint'] = {'raw_output': output}

            # Save report
            pylint_report = self.reports_dir / "pylint_report.json"
            with open(pylint_report, 'w', encoding='utf-8') as f:
                json.dump(self.results.get('pylint', {}), f, indent=2)

            return True, output

        except subprocess.TimeoutExpired:
            return False, "Pylint analysis timed out"
        except Exception as e:
            return False, f"Error running Pylint: {str(e)}"

    def run_bandit(self) -> Tuple[bool, str]:
        """Run security analysis with Bandit"""
        print("\n🔒 Running security analysis (Bandit)...")

        try:
            result = subprocess.run(
                [
                    sys.executable, "-m", "bandit",
                    "-r", ".",
                    "-c", ".bandit.yaml",
                    "-f", "json",
                    "-o", str(self.reports_dir / "bandit_report.json")
                ],
                cwd=self.root_dir,
                capture_output=True,
                text=True,
                timeout=120
            )

            # Load report
            bandit_report = self.reports_dir / "bandit_report.json"
            if bandit_report.exists():
                with open(bandit_report, 'r', encoding='utf-8') as f:
                    self.results['bandit'] = json.load(f)

            return True, result.stdout

        except subprocess.TimeoutExpired:
            return False, "Bandit analysis timed out"
        except Exception as e:
            return False, f"Error running Bandit: {str(e)}"

    def generate_summary_report(self) -> str:
        """Generate a summary report of all analyses"""
        print("\n📊 Generating summary report...")

        summary = {
            'timestamp': datetime.now().isoformat(),
            'analyses': {},
            'summary': {
                'total_issues': 0,
                'critical_issues': 0,
                'warnings': 0,
                'duplicates_found': False
            }
        }

        # Process jscpd results
        if 'jscpd' in self.results:
            jscpd_data = self.results['jscpd']
            if 'statistics' in jscpd_data:
                stats = jscpd_data['statistics']
                summary['analyses']['jscpd'] = {
                    'total_duplicates': stats.get('total', {}).get('duplications', 0),
                    'percentage': stats.get('total', {}).get('percentage', 0),
                }
                summary['summary']['duplicates_found'] = stats.get('total', {}).get('duplications', 0) > 0

        # Process pylint results
        if 'pylint' in self.results and isinstance(self.results['pylint'], list):
            pylint_issues = self.results['pylint']
            summary['analyses']['pylint'] = {
                'total_issues': len(pylint_issues),
                'by_type': {}
            }

            for issue in pylint_issues:
                issue_type = issue.get('type', 'unknown')
                summary['analyses']['pylint']['by_type'][issue_type] = \
                    summary['analyses']['pylint']['by_type'].get(issue_type, 0) + 1

                if issue_type in ['error', 'fatal']:
                    summary['summary']['critical_issues'] += 1
                elif issue_type == 'warning':
                    summary['summary']['warnings'] += 1

            summary['summary']['total_issues'] += len(pylint_issues)

        # Process bandit results
        if 'bandit' in self.results:
            bandit_data = self.results['bandit']
            if 'results' in bandit_data:
                issues = bandit_data['results']
                summary['analyses']['bandit'] = {
                    'total_issues': len(issues),
                    'by_severity': {}
                }

                for issue in issues:
                    severity = issue.get('issue_severity', 'UNKNOWN')
                    summary['analyses']['bandit']['by_severity'][severity] = \
                        summary['analyses']['bandit']['by_severity'].get(severity, 0) + 1

                    if severity in ['HIGH', 'CRITICAL']:
                        summary['summary']['critical_issues'] += 1

                summary['summary']['total_issues'] += len(issues)

        # Save summary
        summary_file = self.reports_dir / "analysis_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)

        return self._format_summary(summary)

    def _format_summary(self, summary: dict) -> str:
        """Format summary for console output"""
        lines = [
            "\n" + "="*60,
            "  CODE ANALYSIS SUMMARY",
            "="*60,
            f"\n📅 Timestamp: {summary['timestamp']}",
            f"\n📊 Total Issues: {summary['summary']['total_issues']}",
            f"⚠️  Critical Issues: {summary['summary']['critical_issues']}",
            f"⚡ Warnings: {summary['summary']['warnings']}",
            f"🔄 Duplicates Found: {'Yes' if summary['summary']['duplicates_found'] else 'No'}",
        ]

        if 'jscpd' in summary['analyses']:
            jscpd = summary['analyses']['jscpd']
            lines.extend([
                f"\n\n🔍 Duplicate Code Detection:",
                f"  - Total duplicates: {jscpd['total_duplicates']}",
                f"  - Duplication percentage: {jscpd['percentage']:.2f}%",
            ])

        if 'pylint' in summary['analyses']:
            pylint = summary['analyses']['pylint']
            lines.extend([
                f"\n\n🐍 Pylint Analysis:",
                f"  - Total issues: {pylint['total_issues']}",
            ])
            if pylint['by_type']:
                lines.append("  - By type:")
                for issue_type, count in pylint['by_type'].items():
                    lines.append(f"    • {issue_type}: {count}")

        if 'bandit' in summary['analyses']:
            bandit = summary['analyses']['bandit']
            lines.extend([
                f"\n\n🔒 Security Analysis:",
                f"  - Total issues: {bandit['total_issues']}",
            ])
            if bandit['by_severity']:
                lines.append("  - By severity:")
                for severity, count in bandit['by_severity'].items():
                    lines.append(f"    • {severity}: {count}")

        lines.extend([
            "\n" + "="*60,
            f"📁 Reports saved to: {self.reports_dir}",
            "="*60 + "\n",
        ])

        return "\n".join(lines)

    def run_all(self) -> bool:
        """Run all analyses"""
        print("🚀 Starting code analysis...")

        all_success = True

        # Run jscpd
        success, output = self.run_jscpd()
        if not success:
            print(f"⚠️  jscpd had issues: {output}")
            all_success = False

        # Run Pylint
        success, output = self.run_pylint()
        if not success:
            print(f"⚠️  Pylint had issues: {output}")
            all_success = False

        # Run Bandit
        success, output = self.run_bandit()
        if not success:
            print(f"⚠️  Bandit had issues: {output}")
            all_success = False

        # Generate summary
        summary = self.generate_summary_report()
        print(summary)

        return all_success


def main():
    """Main entry point"""
    analyzer = CodeAnalyzer()

    try:
        success = analyzer.run_all()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Analysis interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
