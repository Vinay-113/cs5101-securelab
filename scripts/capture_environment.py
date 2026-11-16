#!/usr/bin/env python3
"""Record non-secret host/VM configuration metadata for reproducibility."""
import datetime as dt
import hashlib
import json
import platform
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]
ctl=ROOT/'.tools/lima/bin/limactl'
backup=ROOT/'.vm-recovery/SECURELAB-CLEAN.img'
info={
 'captured_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
 'host_system':platform.system(), 'host_release':platform.release(),
 'host_architecture':platform.machine(),
 'vm_manager':subprocess.check_output([str(ctl),'--version'],text=True).strip(),
 'requested_guest':'Ubuntu 26.04 LTS ARM64 headless server cloud image',
 'vm_config':'vm/securelab.yaml',
 'vm_config_sha256':hashlib.sha256((ROOT/'vm/securelab.yaml').read_bytes()).hexdigest(),
 'clean_recovery_copy_exists':backup.is_file(),
 'clean_recovery_copy_logical_bytes':backup.stat().st_size if backup.is_file() else None,
 'recovery_mechanism':'APFS clone of the stopped VZ guest disk; not Lima QEMU snapshot API',
 'host_mounts':[], 'container_published_ports':[],
 'extra_guest_port_forwarding':'disabled; managed SSH uses Lima loopback transport',
}
(ROOT/'evidence').mkdir(exist_ok=True)
(ROOT/'evidence/environment.json').write_text(json.dumps(info,indent=2)+'\n')
print(json.dumps(info,indent=2))
