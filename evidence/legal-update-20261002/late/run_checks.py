"""Offline README gate inventory, lossless logs and frozen relevant inputs."""
import gzip
import hashlib
import json
import platform
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent


def fingerprint():
    paths = set()
    for folder in ('scripts', 'docs', 'assets', 'templates', 'import'):
        paths.update(p for p in (ROOT / folder).rglob('*')
                     if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'
                     and p.name != 'CURRENT_HANDOFF.md')
    paths.update(ROOT.rglob('index.html'))
    paths.update(ROOT / name for name in ('sitemap.xml', 'robots.txt', 'CNAME'))
    # Derived release-map reporting is excluded: it is not an executable/source/artifact input.
    paths = {p for p in paths if '.lane-work' not in p.parts and 'evidence' not in p.parts}
    return {'python': platform.python_version(),
            'executable': shutil.which('python3'),
            'executableSha256': hashlib.sha256(Path(shutil.which('python3')).read_bytes()).hexdigest(),
            'verificationRunners': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                    for p in (OUT / 'run_tests.py', OUT / 'run_checks.py')},
            'files': {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in sorted(paths)}}


if __name__ == '__main__':
    before = fingerprint()
    (OUT / 'final-inputs.json').write_text(json.dumps(before, indent=2) + '\n')
    commands = [
        ['python3', str(OUT / 'run_tests.py'), str(ROOT), str(OUT / 'full-green')],
        ['python3', 'scripts/render_home.py', '--check'],
        ['python3', 'scripts/render_ios.py', '--check'],
        ['python3', 'scripts/render_android.py', '--check'],
        ['python3', 'scripts/render_import.py', '--check', '--require-all-locales'],
        ['python3', 'scripts/render_terms.py', '--check'],
        ['python3', 'scripts/render_us_health.py', '--check'],
        ['python3', 'scripts/render_sitemap.py', '--check'],
        ['python3', 'scripts/check_site.py'],
        ['python3', 'scripts/account_sync_candidate.py'],
        ['python3', 'scripts/render_account_sync.py', '--check'],
        ['python3', 'scripts/korean_tone.py'],
        ['python3', 'scripts/check_site.py', '--release'],
        ['git', 'diff', '--check'],
    ]
    receipts = []
    for number, cmd in enumerate(commands):
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True)
        log = proc.stdout + proc.stderr
        path = OUT / f'check-{number:02}.log.gz'
        path.write_bytes(gzip.compress(log, mtime=0))
        expected_release_block = (cmd == ['python3', 'scripts/check_site.py', '--release']
                                  and proc.returncode == 1
                                  and b'NEXT_RELEASE_EFFECTIVE_DATE is not filled' in log)
        result = ('BLOCKED_EFFECTIVE_DATE' if expected_release_block else
                  'PASS' if proc.returncode == 0 else 'FAIL')
        item = {'cmd': cmd, 'exit': proc.returncode, 'result': result,
                'log': str(path.relative_to(ROOT)),
                'logSha256': hashlib.sha256(path.read_bytes()).hexdigest()}
        receipts.append(item)
        print(json.dumps(item), flush=True)
    (OUT / 'checks.json').write_text(json.dumps(receipts, indent=2) + '\n')
    after = fingerprint()
    match = before == after
    (OUT / 'frozen-input-comparison.json').write_text(json.dumps({
        'match': match, 'files': len(before['files']),
        'changed': [p for p in set(before['files']) | set(after['files'])
                    if before['files'].get(p) != after['files'].get(p)],
        'runtimeMatch': {k: before[k] == after[k] for k in before if k != 'files'},
    }, indent=2) + '\n')
    assert match, 'verification inputs changed during checks'
    assert all(r['result'] in ('PASS', 'BLOCKED_EFFECTIVE_DATE') for r in receipts), receipts
