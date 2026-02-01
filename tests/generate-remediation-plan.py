#!/usr/bin/env python3
"""Generate remediation plan from failures database."""

import json
from pathlib import Path
from collections import defaultdict
from typing import List, Dict

class RemediationPlanGenerator:
    def __init__(self, failures_db_path: Path):
        with open(failures_db_path) as f:
            self.data = json.load(f)

        self.failures = self.data['failures']
        self.summary = self.data['summary']

    def group_by_category(self) -> Dict[str, List]:
        """Group failures by root cause category."""
        grouped = defaultdict(list)
        for failure in self.failures:
            grouped[failure['category']].append(failure)
        return grouped

    def generate_plan(self, output_file: Path):
        """Generate complete remediation plan."""
        grouped = self.group_by_category()

        # Sort categories by severity and count
        severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        sorted_categories = sorted(
            grouped.items(),
            key=lambda x: (severity_order.get(x[1][0]['severity'], 4), -len(x[1]))
        )

        with open(output_file, 'w') as f:
            self._write_header(f)
            self._write_executive_summary(f)

            fix_num = 1
            for severity_level in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
                fixes_in_level = [(cat, fails) for cat, fails in sorted_categories
                                 if fails[0]['severity'] == severity_level]

                if fixes_in_level:
                    f.write(f"\n## {severity_level} Fixes\n\n")

                    for category, failures in fixes_in_level:
                        fix_num = self._write_fix_section(f, fix_num, category, failures)

            self._write_validation_section(f)

        print(f"Generated remediation plan: {output_file}")

    def _write_header(self, f):
        f.write("# VDE Test Remediation Plan\n\n")
        f.write(f"Generated from failures database\n\n")

    def _write_executive_summary(self, f):
        total = self.summary['total_failures']
        total_tests = 562  # BDD scenarios estimate
        pass_rate = ((total_tests - total) / total_tests * 100) if total_tests > 0 else 100

        f.write("## Executive Summary\n\n")
        f.write(f"- **Total Failures**: {total}\n")
        f.write(f"- **Pass Rate**: {pass_rate:.1f}%\n")
        f.write(f"- **By Severity**: {self.summary.get('by_severity', {})}\n")
        f.write(f"- **By Category**: {self.summary.get('by_category', {})}\n")
        f.write("\n")

    def _write_fix_section(self, f, fix_num: int, category: str, failures: List) -> int:
        f.write(f"### Fix #{fix_num}: {category.replace('_', ' ').title()}\n\n")
        f.write(f"**Impact**: {len(failures)} failure(s) | ")
        f.write(f"**Severity**: {failures[0]['severity']}\n\n")

        # List affected tests
        f.write("**Affected Tests**:\n")
        for failure in failures[:5]:  # Show first 5
            if 'feature_file' in failure:
                f.write(f"- {failure['feature_file']}:{failure.get('scenario_line', '?')} - {failure['scenario']}\n")
            elif 'test_name' in failure:
                f.write(f"- {failure['test_name']}\n")

        if len(failures) > 5:
            f.write(f"- ... and {len(failures) - 5} more\n")

        f.write("\n**Error Examples**:\n")
        f.write(f"```\n{failures[0]['error_message'][:200]}\n```\n\n")

        # Category-specific recommendations
        self._write_category_fix(f, category, failures)

        f.write("**Verification**:\n")
        f.write("```bash\n")
        if failures[0]['phase'] == 'docker-free':
            f.write("./tests/run-docker-free-tests.sh\n")
        elif failures[0]['phase'] == 'docker-required':
            f.write("./tests/run-docker-required-tests.sh\n")
        else:
            f.write(f"make test-{failures[0]['phase']}\n")
        f.write("# Expect: 0 failures in this category\n```\n\n")

        f.write("---\n\n")
        return fix_num + 1

    def _write_category_fix(self, f, category: str, failures: List):
        """Write category-specific fix recommendations."""
        fixes = {
            'DEBUG_OUTPUT': {
                'root_cause': 'VM types config loader outputs DEBUG to stdout instead of stderr',
                'impact': 'Parser receives contaminated output, intent detection fails',
                'fix': [
                    'Redirect DEBUG output in `_load_vm_types_from_config` to stderr',
                    'Update parser script that loads `scripts/data/vm-types.conf`',
                    'Ensure all DEBUG/logging goes to stderr, not stdout'
                ],
                'files': ['Parser scripts that load VM types config'],
            },
            'SHELL_COMPAT': {
                'root_cause': 'Bash-specific tests run in zsh environment',
                'impact': '`_shell_supports_native_assoc` returns 1 in zsh, script path detection fails',
                'fix': [
                    'Update `shell-compatibility.feature` to detect actual shell',
                    'Skip bash-only tests when running in zsh',
                    'Add shell detection to test setup'
                ],
                'files': ['tests/features/docker-free/shell-compatibility.feature', 'shell compat scripts'],
            },
            'SSH_AGENT': {
                'root_cause': 'No SSH agent in test environment',
                'impact': 'SSH-dependent tests fail (vde-ssh-commands, ssh-agent-external-git-operations)',
                'fix': [
                    'Start ssh-agent in test setup (via @given or setUp)',
                    'Generate test SSH key and add to agent',
                    'OR mark tests as requiring ssh-agent and skip if not available'
                ],
                'files': ['tests/features/steps/ssh_agent_steps.py', 'test environment setup'],
            },
        }

        fix_info = fixes.get(category, {
            'root_cause': 'Unknown - investigation required',
            'impact': 'Test failures observed',
            'fix': ['Review test output logs', 'Identify root cause in source code', 'Implement fix'],
            'files': ['To be determined'],
        })

        f.write("**Root Cause**:\n")
        f.write(f"- {fix_info['root_cause']}\n\n")

        f.write("**Impact**:\n")
        f.write(f"- {fix_info['impact']}\n\n")

        f.write("**Fix Steps**:\n")
        for step in fix_info['fix']:
            f.write(f"- {step}\n")
        f.write("\n")

        f.write("**Files to Modify**:\n")
        for file in fix_info['files']:
            f.write(f"- {file}\n")
        f.write("\n")

    def _write_validation_section(self, f):
        f.write("## Final Validation\n\n")
        f.write("After implementing all fixes:\n\n")
        f.write("```bash\n")
        f.write("# Run full test suite\n")
        f.write("./tests/run-full-test-suite.sh\n\n")
        f.write("# Verify no failures\n")
        f.write("python tests/analyze-failures.py\n")
        f.write("cat tests/failures-database.json | jq '.summary.total_failures'\n")
        f.write("# Expected: 0\n")
        f.write("```\n")

def main():
    db_path = Path('tests/failures-database.json')
    output_path = Path('tests/REMEDIATION_PLAN.md')

    if not db_path.exists():
        print(f"Error: {db_path} not found. Run analyze-failures.py first.")
        return

    generator = RemediationPlanGenerator(db_path)
    generator.generate_plan(output_path)

if __name__ == '__main__':
    main()
