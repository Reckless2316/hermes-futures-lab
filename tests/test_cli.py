import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class CliTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, '-m', 'futures_lab', *map(str, args)],
                              capture_output=True, text=True, check=False, timeout=10)

    def test_status_is_stable_and_does_not_claim_financial_evaluation(self):
        first, second = self.run_cli('status'), self.run_cli('status')
        self.assertEqual(first.returncode, 0)
        self.assertEqual(first.stderr, '')
        self.assertEqual(first.stdout, second.stdout)
        report = json.loads(first.stdout)
        self.assertFalse(report['evaluation_available'])
        self.assertEqual(report['implementation'], 'specification_only')
        self.assertEqual(report['acceptance'], 'pending_external_review_and_human_scope_approval')

    def test_fingerprint_hashes_exact_bytes(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'artifact with spaces.bin'
            for content in (b'', b'\x00\xff\r\nnot a manifest\n', b'x' * 1000000):
                with self.subTest(size=len(content)):
                    path.write_bytes(content)
                    result = self.run_cli('fingerprint', path)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(json.loads(result.stdout)['sha256'], hashlib.sha256(content).hexdigest())

    def test_invalid_command_missing_path_and_directory_fail_without_json(self):
        with tempfile.TemporaryDirectory() as folder:
            for args in [(), ('evaluate',), ('fingerprint', Path(folder) / 'missing'),
                         ('fingerprint', folder)]:
                with self.subTest(args=args):
                    result = self.run_cli(*args)
                    self.assertEqual(result.returncode, 2)
                    self.assertEqual(result.stdout, '')
                    self.assertNotIn('Traceback', result.stderr)

    def test_help_and_version(self):
        self.assertEqual(self.run_cli('--version').stdout.strip(), '0.0.1')
        self.assertEqual(self.run_cli('--help').returncode, 0)


if __name__ == '__main__':
    unittest.main()
