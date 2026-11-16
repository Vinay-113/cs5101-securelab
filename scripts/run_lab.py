#!/usr/bin/env python3
"""Run real guest experiments; failed/omitted runs are never marked complete."""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--missions', default='all', help='all or comma-separated numbers; 18 depends on 12,17')
    p.add_argument('--resume', type=Path, help='reuse a run directory, preserving logs from previous attempts')
    a = p.parse_args()
    if platform.system() != 'Linux' or not Path('/etc/securelab-vm').is_file():
        p.error('Run inside the disposable Linux VM after scripts/setup_guest.sh')
    subprocess.run(['sudo', '-n', 'true'], check=True)
    ids = list(range(1,23)) if a.missions == 'all' else [int(x) for x in a.missions.split(',')]
    if not ids or any(x not in range(1,23) for x in ids):
        p.error('Missions must be 1..22')
    stamp = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    run = a.resume.resolve() if a.resume else ROOT / 'evidence' / 'runs' / stamp
    run.mkdir(parents=True, exist_ok=True)
    manifest_path = run / 'manifest.json'
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {
        'run_id': stamp, 'started_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
        'platform': platform.platform(), 'python': sys.version, 'missions': {},
        'scope': 'Ubuntu ARM64 headless VM; M22 is a locally supplied practice challenge',
    }
    env = dict(os.environ, SECURELAB_RUN_ID=manifest['run_id'], LC_ALL='C',
               PS4='+ ${BASH_SOURCE##*/}:${LINENO}: ')
    # Capture compiler diagnostics as evidence, including deliberately unsafe builds.
    with (run / 'build.log').open('a') as f:
        rc = subprocess.run(['make','clean','all','unsafe'], cwd=ROOT, stdout=f, stderr=subprocess.STDOUT).returncode
    if rc:
        print(f'Build failed; see {run / "build.log"}', file=sys.stderr)
        return 1
    subprocess.run(['sudo','install','-d','-m','0755','/opt/securelab/bin'],check=True)
    for binary in sorted((ROOT/'bin').iterdir()):
        if binary.is_file():
            subprocess.run(['sudo','install','-m','0755',str(binary),'/opt/securelab/bin/'],check=True)
    source_files = [ROOT/'Makefile']
    for folder in ['src','scripts','missions','tests','vm']:
        source_files.extend(f for f in (ROOT/folder).rglob('*') if f.is_file() and '__pycache__' not in f.parts and not f.name.startswith('._'))
    source_hashes = {str(f.relative_to(ROOT)): hashlib.sha256(f.read_bytes()).hexdigest() for f in source_files}
    manifest['source_sha256'] = source_hashes
    failures = 0
    for n in ids:
        key = f'{n:02d}'
        work = run / f'mission-{key}'
        work.mkdir(exist_ok=True)
        old = manifest['missions'].get(key)
        attempt = (old or {}).get('attempt',0)+1
        log = work / f'attempt-{attempt}.log'
        start = dt.datetime.now(dt.timezone.utc).isoformat()
        print(f'Mission {key}: running (attempt {attempt})', flush=True)
        with log.open('w') as f:
            f.write(f'UTC: {start}\nMission: {key}\n'); f.flush()
            try:
                proc = subprocess.run(['bash','-x',str(ROOT/'missions/run.sh'),key],
                    cwd=work, env=dict(env, MISSION_DIR=str(work)),
                    stdout=f, stderr=subprocess.STDOUT, timeout=600)
                rc = proc.returncode
            except subprocess.TimeoutExpired:
                rc = 124
                f.write('\nERROR: mission timeout\n')
        # A success sentinel is required in addition to the process exit code.
        verified = rc == 0 and f'MISSION {key} VERIFIED' in log.read_text(errors='replace')
        manifest['missions'][key] = {
            'status': 'verified' if verified else 'failed', 'exit_code': rc,
            'started_utc': start, 'ended_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
            'log': str(log.relative_to(run)), 'attempt': attempt,
            'source_set_sha256': hashlib.sha256(json.dumps(source_hashes,sort_keys=True).encode()).hexdigest(),
        }
        manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
        failures += not verified
        print(f'Mission {key}: {manifest["missions"][key]["status"]} -> {log}', flush=True)
    manifest['finished_utc'] = dt.datetime.now(dt.timezone.utc).isoformat()
    manifest['verified_count'] = sum(x['status']=='verified' for x in manifest['missions'].values())
    manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
    # Portable paths, deterministic sort; exclude the checksum list itself.
    hashes = []
    for f in sorted(run.rglob('*')):
        if f.is_file() and f.name != 'SHA256SUMS':
            hashes.append(f'{hashlib.sha256(f.read_bytes()).hexdigest()}  {f.relative_to(run)}')
    (run/'SHA256SUMS').write_text('\n'.join(hashes)+'\n')
    (ROOT/'evidence/latest.txt').write_text(str(run.relative_to(ROOT))+'\n')
    print(f'Verified {manifest["verified_count"]}/22. Evidence: {run}')
    return 1 if failures else 0

if __name__ == '__main__':
    raise SystemExit(main())
