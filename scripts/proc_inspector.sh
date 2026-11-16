#!/usr/bin/env bash
set -euo pipefail
pid=${1:-}
if [[ ! $pid =~ ^[1-9][0-9]*$ ]]; then echo "Usage: $0 <positive PID>" >&2; exit 2; fi
if [[ ! -r /proc/$pid/status ]]; then echo "Process unavailable or access denied: $pid" >&2; exit 1; fi
printf 'PID: %s\nCommand: ' "$pid"
tr '\0' ' ' < "/proc/$pid/cmdline"
printf '\n'
sed -n -E '/^(Name|State|PPid|Uid|Gid|Threads|VmSize|VmRSS|CapEff|NoNewPrivs|Seccomp|TracerPid):/p' "/proc/$pid/status"
# Globbing counts entries, not ls lines; failure is distinguished from zero.
if [[ -r /proc/$pid/fd && -x /proc/$pid/fd ]]; then
  shopt -s nullglob
  fds=(/proc/"$pid"/fd/*)
  printf 'Open file descriptors: %s\n' "${#fds[@]}"
else
  echo 'Open file descriptors: unavailable (permissions or process exit)'
fi
ps -p "$pid" -o lstart=,etime=,pcpu=,pmem= || true
# A live process can exit or reuse a PID while inspected; this is a best-effort
# snapshot, not an atomic forensic acquisition.
