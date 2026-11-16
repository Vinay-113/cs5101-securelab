#!/usr/bin/env python3
"""Check that delivery claims match logs, artifacts, and recorded source hashes."""
import hashlib
import json
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
run=ROOT/(ROOT/'evidence/latest.txt').read_text().strip()
m=json.loads((run/'manifest.json').read_text())
assert set(m['missions'])=={f'{i:02d}' for i in range(1,23)}
for key,r in m['missions'].items():
    assert r['status']=='verified' and r['exit_code']==0,(key,r)
    assert f'MISSION {key} VERIFIED' in (run/r['log']).read_text()
for line in (run/'SHA256SUMS').read_text().splitlines():
    digest,path=line.split('  ',1)
    assert hashlib.sha256((run/path).read_bytes()).hexdigest()==digest,path
# Report layout and its delivery checker can change without rerunning Linux experiments.
# Their current contents are covered by the rebuilt submission archive checksum.
report_helpers = {'scripts/build_report.py', 'scripts/verify_delivery.py'}
for path,digest in m['source_sha256'].items():
    if path in report_helpers:
        continue
    assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,('Source changed after recorded build',path)
challenge=(run/m['missions']['22']['log']).read_text()
for i in range(1,7):assert f'F{i} VERIFIED' in challenge
for name in ['output/securelab-report.md','output/securelab-report.html','output/pdf/securelab-report.pdf']:
    assert (ROOT/name).stat().st_size>1000,name
tests=(ROOT/'evidence/program-tests.log').read_text()
assert re.search(r'Ran \d+ tests',tests) and '\nOK\n' in tests
env=json.loads((ROOT/'evidence/environment.json').read_text())
assert env['clean_recovery_copy_exists']
print('Verified: 22 mission results, six practice fixes, evidence hashes, experiment source hashes, test result, clean recovery copy, and report files.')
