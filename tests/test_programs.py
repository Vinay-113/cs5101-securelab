#!/usr/bin/env python3
"""Behavioral checks for valid boundaries, IPC, and actual mutex correctness."""
import subprocess
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BIN=ROOT/'bin'

def run(name,*args,**kw):
    return subprocess.run([str(BIN/name),*args],text=True,capture_output=True,timeout=30,**kw)

class Programs(unittest.TestCase):
    def test_mutex_repeated(self):
        for _ in range(5):
            p=run('race_mutex'); self.assertEqual(p.returncode,0,p.stderr)
            self.assertIn('Actual  : 2000000',p.stdout)
    def test_bounded_copy_boundary(self):
        for s in ['', 'x'*15]:
            p=run('bounded_copy',s); self.assertEqual(p.returncode,0,p.stderr)
            self.assertEqual(p.stdout,f'Accepted: {s}\n')
        for s in ['x'*16,'x'*4096]:
            p=run('bounded_copy',s); self.assertEqual(p.returncode,1)
            self.assertIn('Rejected:',p.stderr)
        self.assertEqual(run('bounded_copy').returncode,2)
    def test_pipe_message(self):
        p=run('pipe_ipc'); self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual(p.stdout,'Child received: Hello from the parent\n')
    def test_shared_message(self):
        p=run('shared_ipc'); self.assertEqual(p.returncode,0,p.stderr)
        self.assertIn('synchronized shared mapping',p.stdout)
    def test_syscall_file_and_symlink(self):
        with tempfile.TemporaryDirectory() as d:
            p=run('syscall_demo',cwd=d); self.assertEqual(p.returncode,0,p.stderr)
            f=Path(d)/'hello.txt'; self.assertEqual(f.read_text(),'Hello from user space!\n')
            f.unlink(); target=Path(d)/'target'; target.write_text('keep')
            f.symlink_to(target)
            p=run('syscall_demo',cwd=d); self.assertNotEqual(p.returncode,0)
            self.assertEqual(target.read_text(),'keep')
    def test_inspector_rejects_invalid_pid(self):
        for pid in ['','../1','-1','abc','0']:
            p=subprocess.run(['bash',str(ROOT/'scripts/proc_inspector.sh'),pid],capture_output=True)
            self.assertEqual(p.returncode,2)
    def test_protected_short_input(self):
        p=run('memory_protected','short'); self.assertEqual(p.returncode,0,p.stderr)
    def test_asan_detects_overflow(self):
        p=run('memory_asan'); self.assertNotEqual(p.returncode,0)
        self.assertIn('stack-buffer-overflow',p.stderr)

if __name__=='__main__': unittest.main(verbosity=2)
