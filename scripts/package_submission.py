#!/usr/bin/env python3
"""Package sources and verified evidence, excluding virtual disks and credentials."""
import hashlib
import json
from pathlib import Path
import zipfile
ROOT=Path(__file__).resolve().parents[1]
ALLOWED=['README.md','Makefile','.gitignore','.gitattributes','src','scripts','missions','notes','docs','tests','vm','evidence','output/pdf/securelab-report.pdf']

def main():
    out=ROOT/'output';out.mkdir(exist_ok=True)
    archive=out/'securelab-submission.zip'
    files=[]
    for name in ALLOWED:
        p=ROOT/name
        if not p.exists():continue
        files.extend([p] if p.is_file() else [f for f in p.rglob('*') if f.is_file() and '__pycache__' not in f.parts and not f.name.startswith('._')])
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for f in sorted(files):
            assert not any(x in f.parts for x in ['.vm','.tools','.cache'])
            assert f.name not in ['id_ed25519','id_rsa','ssh.sock']
            z.write(f,f.relative_to(ROOT))
    digest=hashlib.sha256(archive.read_bytes()).hexdigest()
    (out/'securelab-submission.sha256').write_text(f'{digest}  {archive.name}\n')
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        names=z.namelist()
        assert 'src/identity.c' in names
        assert 'output/pdf/securelab-report.pdf' in names
        assert any(n.endswith('manifest.json') for n in names)
    print(f'{archive}: {len(files)} files, {archive.stat().st_size:,} bytes; SHA256 {digest}')
if __name__=='__main__':main()
