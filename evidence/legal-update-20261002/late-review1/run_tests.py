"""Offline exact-identity unittest receipt. No native or network actions."""
import ast
import gzip
import hashlib
import io
import json
import platform
import sys
import unittest
from pathlib import Path

root = Path(sys.argv[1]).resolve()
output = Path(sys.argv[2]).resolve()
sys.path.insert(0, str(root / 'scripts'))
modules = sys.argv[3:]
for path in sorted((root / 'scripts').glob('*.py')):
    ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
loader = unittest.TestLoader()
suite = (loader.loadTestsFromNames(modules) if modules else
         loader.discover(str(root / 'scripts'), pattern='test_*.py'))


def identities(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from identities(item)
        else:
            yield item.id()


requested = list(identities(suite))
assert not loader.errors, loader.errors
assert requested and len(set(requested)) == len(requested)


class Result(unittest.TextTestResult):
    executed = []
    failed_methods = set()

    def startTest(self, test):
        self.executed.append(test.id())
        super().startTest(test)

    def addFailure(self, test, err):
        self.failed_methods.add(test.id())
        super().addFailure(test, err)

    def addSubTest(self, test, subtest, err):
        if err is not None:
            self.failed_methods.add(test.id())
        super().addSubTest(test, subtest, err)


stream = io.StringIO()
result = unittest.TextTestRunner(stream=stream, verbosity=2, resultclass=Result).run(suite)
log = stream.getvalue().encode('utf-8')
output.parent.mkdir(parents=True, exist_ok=True)
output.with_suffix('.log.gz').write_bytes(gzip.compress(log, mtime=0))
receipt = {
    'root': str(root), 'python': platform.python_version(), 'compile': 'PASS',
    'requested': requested, 'executed': result.executed,
    'omitted': sorted(set(requested) - set(result.executed)), 'testsRun': result.testsRun,
    'failedMethods': sorted(result.failed_methods), 'assertionFailures': len(result.failures),
    'errors': [test.id() for test, _ in result.errors],
    'skipped': [test.id() for test, _ in result.skipped],
    'logSha256': hashlib.sha256(output.with_suffix('.log.gz').read_bytes()).hexdigest(),
    'scriptHashes': {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in sorted((root / 'scripts').glob('*.py'))},
    'exit': 0 if result.wasSuccessful() else 1,
}
output.with_suffix('.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({k: receipt[k] for k in ('compile', 'testsRun', 'failedMethods',
                                        'assertionFailures', 'errors', 'skipped', 'omitted', 'exit')}))
sys.exit(receipt['exit'])
