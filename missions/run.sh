#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/../scripts/common.sh"
mission=${1:?mission number}
case "$mission" in
01)
 id; groups; "$BIN/identity"; sudo -u alice "$BIN/identity"
 ;;
02)
 strace -o trace.txt -e trace=open,openat,write,close "$BIN/syscall_demo"
 cat trace.txt; cat hello.txt
 test "$(cat hello.txt)" = 'Hello from user space!'
 ;;
03)
 sleep 30 & pid=$!
 trap 'kill "$pid" 2>/dev/null || true' EXIT
 bash "$ROOT/scripts/proc_inspector.sh" "$pid"
 ;;
04)
 "$BIN/address_space" > addresses.txt & pid=$!
 trap 'kill "$pid" 2>/dev/null || true' EXIT
 sleep 1
 cat addresses.txt; cat "/proc/$pid/maps" > maps.txt; cat maps.txt
 # ASLR comparison across separate executions.
 "$BIN/address_space" > addresses-second.txt & pid2=$!
 sleep 1; cat addresses-second.txt; kill "$pid2"; wait "$pid2" || true
 ;;
05)
 for i in 1 2 3 4 5; do echo "Unsynchronized run $i"; "$BIN/race_unsafe"; done
 for i in 1 2 3; do echo "Mutex run $i"; "$BIN/race_mutex"; done
 ;;
06)
 "$BIN/pipe_ipc"; "$BIN/shared_ipc"
 ;;
07)
 sudo install -d -m 0755 "$LAB/dac"
 printf 'Alice secret\n' | sudo tee "$LAB/dac/secret.txt" >/dev/null
 sudo chown alice:alice "$LAB/dac/secret.txt"; sudo setfacl -b "$LAB/dac/secret.txt"
 sudo chmod 0644 "$LAB/dac/secret.txt"
 stat -c '%A %a %U:%G %n' "$LAB/dac/secret.txt"
 allow sudo -u bob cat "$LAB/dac/secret.txt"
 sudo chmod 0600 "$LAB/dac/secret.txt"
 stat -c '%A %a %U:%G %n' "$LAB/dac/secret.txt"
 deny sudo -u bob cat "$LAB/dac/secret.txt"
 allow sudo -u alice cat "$LAB/dac/secret.txt"
 ;;
08)
 sudo install -d -m 0755 "$LAB/acl"
 printf 'ACL test\n' | sudo tee "$LAB/acl/secret.txt" >/dev/null
 sudo chown alice:alice "$LAB/acl/secret.txt"; sudo setfacl -b "$LAB/acl/secret.txt"; sudo chmod 0600 "$LAB/acl/secret.txt"
 getfacl -p "$LAB/acl/secret.txt"
 deny sudo -u bob cat "$LAB/acl/secret.txt"
 sudo setfacl -m u:bob:r "$LAB/acl/secret.txt"; getfacl -p "$LAB/acl/secret.txt"
 allow sudo -u bob cat "$LAB/acl/secret.txt"
 deny sudo -u bob sh -c 'echo unauthorized >> /opt/securelab/acl/secret.txt'
 # Remove the named grant and re-test; leave a secure state.
 sudo setfacl -x u:bob "$LAB/acl/secret.txt"
 deny sudo -u bob cat "$LAB/acl/secret.txt"
 ;;
09)
 id; sudo -n -l; capsh --print; getcap -r /usr/bin 2>/dev/null
 ;;
10)
 "$BIN/memory_protected" short
 set +e
 "$BIN/memory_protected" > protected-overflow.txt 2>&1; rc=$?
 cat protected-overflow.txt; echo "Protected overflow exit: $rc"
 set -e
 [[ $rc -ne 0 ]]
 set +e
 ASAN_OPTIONS=detect_leaks=0 "$BIN/memory_asan" > asan-overflow.txt 2>&1; rc=$?
 set -e
 cat asan-overflow.txt; echo "ASan overflow exit: $rc"
 [[ $rc -ne 0 ]]; grep -q 'stack-buffer-overflow' asan-overflow.txt
 allow "$BIN/bounded_copy" short
 allow "$BIN/bounded_copy" 123456789012345
 deny "$BIN/bounded_copy" 1234567890123456
 ;;
11)
 checksec --file="$BIN/memory_protected"
 checksec --file="$BIN/memory_unprotected"
 cat /proc/sys/kernel/randomize_va_space
 readelf -W -l "$BIN/memory_protected" > protected-headers.txt
 cat protected-headers.txt
 readelf -Ws "$BIN/memory_protected" | grep __stack_chk_fail
 ;;
12)
 sudo install -d -o root -g securelab -m 0755 "$LAB/public"
 sudo install -d -o root -g securelab -m 0750 "$LAB/employees" "$LAB/secrets"
 printf 'Incident: synthetic lab record\n' | sudo tee "$LAB/secrets/incident.txt" >/dev/null
 sudo chown root:securelab "$LAB/secrets/incident.txt"; sudo chmod 0640 "$LAB/secrets/incident.txt"
 sudo namei -l "$LAB/secrets/incident.txt"
 allow sudo -u alice cat "$LAB/secrets/incident.txt"
 deny sudo -u bob cat "$LAB/secrets/incident.txt"
 deny sudo -u alice sh -c 'echo changed >> /opt/securelab/secrets/incident.txt'
 allow sudo -u bob ls "$LAB/public"
 ;;
13)
 printf 'Approved configuration\n' > config.txt
 sha256sum config.txt > config.sha256; cat config.sha256
 allow sha256sum -c config.sha256
 printf 'Unexpected change\n' >> config.txt; sha256sum config.txt
 deny sha256sum -c config.sha256
 ;;
14)
 start=$(date --iso-8601=seconds)
 tag="securelab-${SECURELAB_RUN_ID}"
 logger -t "$tag" -- 'synthetic lab session started'
 id > timeline-identity.txt
 logger -t "$tag" -- 'identity baseline captured'
 printf 'Approved configuration\n' > timeline-demo.txt
 logger -t "$tag" -- 'synthetic file created'
 chmod 0600 timeline-demo.txt; stat -c '%a %n' timeline-demo.txt
 logger -t "$tag" -- 'file permissions restricted to 0600'
 sha256sum timeline-demo.txt > timeline-demo.sha256
 logger -t "$tag" -- 'SHA256 baseline captured'
 printf 'Controlled drift\n' >> timeline-demo.txt
 logger -t "$tag" -- 'controlled content change applied'
 deny sha256sum -c timeline-demo.sha256
 logger -t "$tag" -- 'hash mismatch detected'
 printf 'Approved configuration\n' > timeline-demo.txt
 allow sha256sum -c timeline-demo.sha256
 logger -t "$tag" -- 'approved bytes restored and verification passed'
 sudo journalctl --sync
 sudo journalctl -t "$tag" --since "$start" --no-pager -o short-iso-precise | tee timeline.txt
 [[ $(grep -c "$tag" timeline.txt) -eq 8 ]]
 sudo journalctl -u ssh -n 15 --no-pager
 last -n 10 || true
 ;;
15)
 "$BIN/address_space" > app-output.txt & pid=$!
 trap 'kill "$pid" 2>/dev/null || true' EXIT
 ps -p "$pid" -o pid,ppid,uid,euid,nlwp,%cpu,%mem,args
 ls -l "/proc/$pid/fd"; cat "/proc/$pid/status"; lsof -a -p "$pid" -i || [[ $? == 1 ]]
 ss -lntup
 ;;
16)
 sudo docker run --rm hello-world
 sudo docker run --rm ubuntu:26.04 uname -a
 sudo docker run --rm ubuntu:26.04 cat /etc/os-release
 sudo docker build -t securelab/ubuntu:26.04 -f "$ROOT/vm/Dockerfile" "$ROOT/vm"
 sudo docker run --rm securelab/ubuntu:26.04 ps -ef
 echo 'Guest PID namespace:'; readlink /proc/self/ns/pid
 sudo docker run --rm --read-only --cap-drop=ALL --security-opt=no-new-privileges --network=none --memory=64m --cpus=0.5 --pids-limit=32 ubuntu:26.04 sh -c '
   echo "Container PID namespace:"; readlink /proc/self/ns/pid
   echo "PID 1:"; cat /proc/1/comm
   echo "Cgroup controls:"; cat /sys/fs/cgroup/memory.max /sys/fs/cgroup/pids.max /sys/fs/cgroup/cpu.max
   grep -E "CapEff|NoNewPrivs" /proc/self/status
   if touch /should-not-write; then exit 1; fi
   test "$(cat /sys/fs/cgroup/memory.max)" = 67108864
   test "$(cat /sys/fs/cgroup/pids.max)" = 32
   grep -q "^CapEff:[[:space:]]*0000000000000000$" /proc/self/status
   grep -q "^NoNewPrivs:[[:space:]]*1$" /proc/self/status
   test "$(cat /sys/fs/cgroup/cpu.max)" = "50000 100000"
 '
 ;;
17)
 sudo aa-status
 sudo install -d -m 0755 "$LAB/apparmor"
 printf 'Public lab text\n' | sudo tee "$LAB/apparmor/allowed.txt" >/dev/null
 printf 'Restricted lab text\n' | sudo tee "$LAB/apparmor/denied.txt" >/dev/null
 sudo chmod 0644 "$LAB/apparmor/"*.txt
 sudo install -m 0755 "$BIN/confinement_probe" "$LAB/apparmor/probe"
 # A repeated lesson must re-establish the unconfined baseline explicitly.
 if sudo grep -q '^securelab-probe ' /sys/kernel/security/apparmor/profiles; then
   sudo apparmor_parser -R /etc/apparmor.d/securelab-probe
 fi
 # First prove ordinary DAC permits both resources.
 "$LAB/apparmor/probe" unconfined
 cat > profile <<'PROFILE'
#include <tunables/global>
profile securelab-probe /opt/securelab/apparmor/probe {
  #include <abstractions/base>
  /opt/securelab/apparmor/probe mr,
  /opt/securelab/apparmor/allowed.txt r,
  audit deny /opt/securelab/apparmor/denied.txt r,
}
PROFILE
 sudo install -m 0644 profile /etc/apparmor.d/securelab-probe
 sudo apparmor_parser -r /etc/apparmor.d/securelab-probe
 "$LAB/apparmor/probe" confined
 sudo aa-status
 sudo journalctl -k --since '5 minutes ago' --no-pager | grep -E 'securelab-probe|apparmor=' || true
 ;;
18)
 echo 'Access-control comparison: notes/mission-18.md'
 # Re-test observations used in the conceptual comparison.
 allow sudo -u alice cat "$LAB/secrets/incident.txt"
 deny sudo -u bob cat "$LAB/secrets/incident.txt"
 "$LAB/apparmor/probe" confined
 capsh --print
 ;;
19)
 bash "$ROOT/scripts/hardening.sh" "$MISSION_DIR"
 ;;
20)
 bash "$ROOT/scripts/local_ssh.sh"
 ;;
21)
 uname -a; uname -m; cat /etc/os-release
 systemd-detect-virt --vm
 lscpu
 cat /sys/class/dmi/id/product_name 2>/dev/null || true
 echo 'Trust-boundary diagrams: docs/diagrams.md'
 ;;
22)
 bash "$ROOT/scripts/practice_challenge.sh" "$MISSION_DIR"
 ;;
*) echo "Unknown mission: $mission" >&2; exit 2;;
esac
echo "MISSION $mission VERIFIED"
