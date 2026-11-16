#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
export LIMA_HOME="${SECURELAB_LIMA_HOME:-$ROOT/.vm}"
export XDG_CACHE_HOME="$ROOT/.cache"
mkdir -p "$LIMA_HOME"
chmod 0700 "$LIMA_HOME"
mkdir -p "$ROOT/tmp"
ctl="$ROOT/.tools/lima/bin/limactl"
[[ -x $ctl ]] || ctl=$(command -v limactl)
case "${1:-status}" in
 start)
   if [[ -f "$LIMA_HOME/securelab/lima.yaml" ]]; then
     "$ctl" start --tty=false securelab
   else
     "$ctl" start --tty=false --name=securelab "$ROOT/vm/securelab.yaml"
   fi
   ;;
 stop) "$ctl" stop securelab ;;
 status) "$ctl" list ;;
 shell) shift; "$ctl" shell securelab "$@" ;;
 sync)
   # Archive only sources; no host home mounts or generated secrets.
   COPYFILE_DISABLE=1 tar --no-xattrs --no-acls --no-fflags -C "$ROOT" --exclude=.git --exclude=.tools --exclude=.vm --exclude=.vm-recovery --exclude=.cache --exclude=tmp --exclude=bin --exclude=__pycache__ --exclude=output --exclude=evidence -czf "$ROOT/tmp/project.tar.gz" .
   "$ctl" copy "$ROOT/tmp/project.tar.gz" securelab:/tmp/securelab-project.tar.gz
   "$ctl" shell securelab bash -c 'mkdir -p "$HOME/securelab"; tar -xzf /tmp/securelab-project.tar.gz -C "$HOME/securelab"'
   ;;
 setup) "$ctl" shell securelab bash -ec 'cd "$HOME/securelab"; bash scripts/setup_guest.sh; bash scripts/install_docker.sh' ;;
 run) shift; "$ctl" shell securelab bash -c 'cd "$HOME/securelab"; python3 scripts/run_lab.py "$@"' bash "$@" ;;
 test) "$ctl" shell securelab bash -c 'set -o pipefail; cd "$HOME/securelab"; mkdir -p evidence; make test 2>&1 | tee evidence/program-tests.log' ;;
 fetch)
   "$ctl" shell securelab bash -c 'cd "$HOME/securelab"; tar -czf /tmp/securelab-evidence.tar.gz evidence'
   "$ctl" copy securelab:/tmp/securelab-evidence.tar.gz "$ROOT/tmp/evidence.tar.gz"
   tar -xzf "$ROOT/tmp/evidence.tar.gz" -C "$ROOT"
   ;;
 snapshot)
   name=${2:-SECURELAB-CLEAN}
   "$ctl" stop securelab
   [[ $name =~ ^[A-Za-z0-9_-]+$ ]] || exit 2
   mkdir -p "$ROOT/.vm-recovery"
   # VZ has no Lima snapshot API. A stopped APFS disk clone is the recovery point.
   [[ ! -e "$ROOT/.vm-recovery/$name.img" ]] || { echo 'Backup already exists.' >&2; exit 1; }
   cp -c "$LIMA_HOME/securelab/disk" "$ROOT/.vm-recovery/$name.img"
   cp "$LIMA_HOME/securelab/lima.yaml" "$ROOT/.vm-recovery/$name.yaml"
   if [[ -f "$LIMA_HOME/securelab/vz-efi" ]]; then cp -c "$LIMA_HOME/securelab/vz-efi" "$ROOT/.vm-recovery/$name.efi"; fi
   echo "Stopped-disk recovery copy: $ROOT/.vm-recovery/$name.img"
   "$ctl" start securelab
   ;;
 restore)
   name=${2:-SECURELAB-CLEAN}
   [[ $name =~ ^[A-Za-z0-9_-]+$ && -f "$ROOT/.vm-recovery/$name.img" ]] || exit 2
   "$ctl" stop securelab
   # Preserve current state so restoring the clean disk is itself reversible.
   mv "$LIMA_HOME/securelab/disk" "$LIMA_HOME/securelab/disk.before-restore-$(date +%s)"
   cp -c "$ROOT/.vm-recovery/$name.img" "$LIMA_HOME/securelab/disk"
   if [[ -f "$ROOT/.vm-recovery/$name.efi" ]]; then
     cp -c "$LIMA_HOME/securelab/vz-efi" "$LIMA_HOME/securelab/vz-efi.before-restore-$(date +%s)"
     rm "$LIMA_HOME/securelab/vz-efi"
     cp -c "$ROOT/.vm-recovery/$name.efi" "$LIMA_HOME/securelab/vz-efi"
   fi
   "$ctl" start securelab
   ;;
 *) echo 'Usage: vm.sh start|stop|status|shell|sync|setup|run|test|fetch|snapshot|restore [name]'  >&2; exit 2;;
esac
