#!/usr/bin/env python3
"""Analyze test failures from logs and JSON outputs."""

import json
import re
from pathlib import Path
from typing import List, Dict
from collections import defaultdict

class FailureAnalyzer:
    def __init__(self, results_dir: Path, log_dir: Path):
        self.results_dir = results_dir
        self.log_dir = log_dir
        self.failures = []
        self.failure_id = 0

        # Root cause categorization patterns
        self.category_patterns = {
            'DEBUG_OUTPUT': [
                r'DEBUG:.*_load_vm_types_from_config',
                r'Expected.*intent.*got.*DEBUG:',
            ],
            'SSH_AGENT': [
                r'SSH agent is not running',
                r'SSH agent.*no keys',
                r'[Ss][Ss][Hh][\s-]agent.*should be running',
                r'SSH agent should be running',
            ],
            'SHELL_COMPAT': [
                r'_shell_supports_native_assoc.*got 1',
                r'Script path should not be empty',
                r'bash.*version.*compatibility',
                r'zsh.*syntax',
                r'bash.*compatibility',
            ],
            'DOCKER_DAEMON': [r'Docker daemon.*not running', r'Cannot connect to.*Docker'],
            'PARSER': [r'Intent.*not detected', r'parse.*failed', r'regex.*match'],
            'CACHE': [r'cache.*not found', r'cache.*invalid', r'cache.*corrupt'],
            'SSH': [r'SSH.*failed', r'ssh-agent', r'authorized_keys'],
            'CONFIG': [r'configuration.*invalid', r'config.*not found'],
            'PERMISSIONS': [r'Permission denied', r'not permitted'],
            'FILE_NOT_FOUND': [r'No such file', r'file.*not found'],
            'ENV': [r'environment variable', r'PATH.*not set'],
        }

    def analyze_bdd_json(self, json_file: Path, phase: str):
        """Extract failures from Behave JSON output."""
        if not json_file.exists():
            return

        with open(json_file) as f:
            data = json.load(f)

        for feature in data:
            feature_file = feature.get('location', 'unknown')

            for element in feature.get('elements', []):
                scenario_name = element.get('name', 'unknown')
                scenario_location = element.get('location', 'unknown:0')

                for step in element.get('steps', []):
                    result = step.get('result', {})

                    if result.get('status') == 'failed':
                        error_msg = result.get('error_message', '')

                        failure = {
                            'id': f'{phase[:2]}-{self.failure_id:03d}',
                            'phase': phase,
                            'feature_file': feature_file.split(':')[0],
                            'scenario': scenario_name,
                            'scenario_line': scenario_location.split(':')[1],
                            'step': step.get('name', ''),
                            'step_line': step.get('location', ':0').split(':')[1],
                            'error_type': self._extract_error_type(error_msg),
                            'error_message': error_msg[:200],
                            'category': self._categorize(error_msg),
                            'severity': 'UNKNOWN'
                        }

                        self.failures.append(failure)
                        self.failure_id += 1

    def analyze_shell_logs(self, log_file: Path, phase: str):
        """Extract failures from shell test logs."""
        if not log_file.exists():
            return

        with open(log_file) as f:
            content = f.read()

        # Extract failed test assertions (✗ pattern)
        failed_pattern = re.compile(r'^✗\s+(.+?)$', re.MULTILINE)
        for match in failed_pattern.finditer(content):
            test_name = match.group(1)

            failure = {
                'id': f'{phase[:2]}-{self.failure_id:03d}',
                'phase': phase,
                'test_name': test_name,
                'error_type': 'AssertionError',
                'error_message': test_name,
                'category': self._categorize(test_name),
                'severity': 'UNKNOWN'
            }

            self.failures.append(failure)
            self.failure_id += 1

    def _extract_error_type(self, error_msg: str) -> str:
        """Extract error type from error message."""
        if 'AssertionError' in error_msg:
            return 'AssertionError'
        elif 'KeyError' in error_msg:
            return 'KeyError'
        elif 'FileNotFoundError' in error_msg:
            return 'FileNotFoundError'
        else:
            return 'Unknown'

    def _categorize(self, error_msg) -> str:
        """Categorize failure by root cause."""
        if not error_msg:
            return 'UNKNOWN'

        # Convert lists to strings for matching
        if isinstance(error_msg, list):
            error_text = '\n'.join(str(item) for item in error_msg)
        elif isinstance(error_msg, str):
            error_text = error_msg
        else:
            return 'UNKNOWN'

        for category, patterns in self.category_patterns.items():
            for pattern in patterns:
                try:
                    if re.search(pattern, error_text, re.IGNORECASE):
                        return category
                except (TypeError, re.error):
                    continue
        return 'UNKNOWN'

    def assign_severity(self):
        """Assign severity based on failure count per category."""
        category_counts = defaultdict(int)
        for failure in self.failures:
            category_counts[failure['category']] += 1

        for failure in self.failures:
            count = category_counts[failure['category']]
            if count > 20:
                failure['severity'] = 'CRITICAL'
            elif count >= 5:
                failure['severity'] = 'HIGH'
            elif count >= 2:
                failure['severity'] = 'MEDIUM'
            else:
                failure['severity'] = 'LOW'

    def generate_summary(self) -> Dict:
        """Generate failure summary statistics."""
        by_phase = defaultdict(int)
        by_category = defaultdict(int)
        by_severity = defaultdict(int)

        for failure in self.failures:
            by_phase[failure['phase']] += 1
            by_category[failure['category']] += 1
            by_severity[failure['severity']] += 1

        return {
            'total_failures': len(self.failures),
            'by_phase': dict(by_phase),
            'by_category': dict(by_category),
            'by_severity': dict(by_severity)
        }

    def save_database(self, output_file: Path):
        """Save failures database to JSON."""
        self.assign_severity()

        database = {
            'failures': self.failures,
            'summary': self.generate_summary()
        }

        with open(output_file, 'w') as f:
            json.dump(database, f, indent=2)

        print(f"Saved {len(self.failures)} failures to {output_file}")

def main():
    results_dir = Path('tests')
    log_dir = Path('test-logs')

    analyzer = FailureAnalyzer(results_dir, log_dir)

    # Load test results summary to find latest logs
    summary_file = results_dir / 'TEST_RESULTS_SUMMARY.json'
    if summary_file.exists():
        with open(summary_file) as f:
            summary = json.load(f)

        # Analyze BDD JSON outputs
        analyzer.analyze_bdd_json(results_dir / 'behave-results-docker-free.json', 'docker-free')
        analyzer.analyze_bdd_json(results_dir / 'behave-results-docker-required.json', 'docker-required')

        # Analyze shell test logs
        for phase, log_path in summary.get('logs', {}).items():
            analyzer.analyze_shell_logs(Path(log_path), phase)

    # Save database
    analyzer.save_database(results_dir / 'failures-database.json')

    # Print summary
    summary = analyzer.generate_summary()
    print(f"\nFailure Summary:")
    print(f"  Total: {summary['total_failures']}")
    print(f"  By Severity: {summary['by_severity']}")
    print(f"  By Category: {summary['by_category']}")

if __name__ == '__main__':
    main()
