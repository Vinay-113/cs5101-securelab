#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
: "${MISSION_DIR:?runner must set MISSION_DIR}"
mkdir -p "$MISSION_DIR"
cd "$MISSION_DIR"
BIN=/opt/securelab/bin
LAB=/opt/securelab
need_vm() {
  [[ $(uname -s) == Linux && -f /etc/securelab-vm ]] || { echo 'Use the prepared disposable Linux VM.' >&2; exit 2; }
  sudo -n true
}
allow() { "$@"; printf 'VERIFIED ALLOWED: '; printf '%q ' "$@"; printf '\n'; }
deny() {
  local rc=0
  "$@" || rc=$?
  [[ $rc -ne 0 ]] || { echo 'FAIL: expected denial' >&2; return 1; }
  printf 'VERIFIED DENIED (exit %s): ' "$rc"; printf '%q ' "$@"; printf '\n'
}
need_vm
ulimit -c 0
