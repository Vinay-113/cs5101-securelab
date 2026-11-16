#!/usr/bin/env bash
# PRACTICE ONLY: controlled fixtures, not the instructor's absent Mission 22.
set -euo pipefail
out=${1:?evidence directory}
[[ -f /etc/securelab-vm ]] || exit 2
base=/opt/securelab/practice
sudo install -d -o root -g securelab -m 0755 "$base"
sudo install -d -o root -g securelab -m 0777 "$base/dropbox"
printf 'Synthetic incident record\n' | sudo tee "$base/secret.txt" >/dev/null
printf 'approved=true\n' | sudo tee "$base/config.txt" >/dev/null
sudo chown root:securelab "$base/secret.txt" "$base/config.txt"
sudo chmod 0644 "$base/secret.txt"; sudo chmod 0666 "$base/config.txt"
# Explicitly seed the missing-monitoring condition on every practice run.
sudo rm -f /var/lib/securelab/integrity/practice.sha256
sudo test ! -e /var/lib/securelab/integrity/practice.sha256
echo 'F6 baseline before remediation: absent'
sudo systemctl stop securelab-practice-listener securelab-practice-worker securelab-practice-worker-fixed 2>/dev/null || true
sudo systemd-run --collect --unit=securelab-practice-listener --property=WorkingDirectory="$base" /usr/bin/python3 -m http.server 8088 --bind 127.0.0.1
sudo systemd-run --collect --unit=securelab-practice-worker /usr/bin/sleep infinity
# Cleanup exposed fixture even if verification fails.
trap 'sudo systemctl stop securelab-practice-listener securelab-practice-worker securelab-practice-worker-fixed 2>/dev/null || true; sudo chmod 0640 "$base/secret.txt" "$base/config.txt"; sudo chmod 0750 "$base/dropbox"' EXIT
sleep 1
snapshot() {
 date -u --iso-8601=seconds; getent passwd alice bob; id alice; id bob
 ps -eo pid,ppid,uid,euid,nlwp,pcpu,pmem,args
 stat -c '%a %U:%G %n' "$base" "$base/secret.txt" "$base/config.txt" "$base/dropbox"
 sudo getfacl -p "$base/secret.txt" "$base/config.txt"
 systemctl --type=service --state=running --no-pager
 sudo ss -lntup
 sudo aa-status
}
snapshot > "$out/baseline.txt"; cat "$out/baseline.txt"
# F1 confidentiality: Bob reads a secret.
sudo -u bob cat "$base/secret.txt"
sudo chmod 0640 "$base/secret.txt"
if sudo -u bob cat "$base/secret.txt"; then exit 1; fi
sudo -u alice cat "$base/secret.txt"
echo 'F1 VERIFIED: unauthorized read denied; authorized read retained'
# F2 integrity/authorization: Bob can modify configuration.
sudo -u bob sh -c 'printf "unauthorized=true\n" >> /opt/securelab/practice/config.txt'
grep -q '^unauthorized=true$' "$base/config.txt"
printf 'approved=true\n' | sudo tee "$base/config.txt" >/dev/null
sudo chmod 0640 "$base/config.txt"
if sudo -u bob sh -c 'printf "blocked=true\n" >> /opt/securelab/practice/config.txt'; then exit 1; fi
echo 'F2 VERIFIED: unauthorized configuration write denied'
# F3 directory integrity: Bob can introduce entries.
sudo -u bob touch "$base/dropbox/bob-before"
sudo rm "$base/dropbox/bob-before"; sudo chmod 0750 "$base/dropbox"
if sudo -u bob touch "$base/dropbox/bob-after"; then exit 1; fi
echo 'F3 VERIFIED: unauthorized directory creation denied'
# F4 attack surface: unnecessary loopback listener (never public).
curl --fail --silent http://127.0.0.1:8088/ >/dev/null
sudo systemctl stop securelab-practice-listener
if curl --fail --silent --max-time 2 http://127.0.0.1:8088/ >/dev/null; then exit 1; fi
if ss -lntH | awk '{print $4}' | grep -q ':8088$'; then exit 1; fi
echo 'F4 VERIFIED: unnecessary listener absent'
# F5 privilege separation: worker started as root, requires no root operations.
pid=$(systemctl show -p MainPID --value securelab-practice-worker)
[[ $(stat -c %u "/proc/$pid") == 0 ]]
sudo systemctl stop securelab-practice-worker
sudo systemd-run --collect --unit=securelab-practice-worker-fixed --property=Type=exec --property=User=nobody --property=NoNewPrivileges=yes --property=ProtectSystem=strict --property=MemoryMax=64M /usr/bin/sleep infinity
pid=$(systemctl show -p MainPID --value securelab-practice-worker-fixed)
ps -p "$pid" -o pid,uid,euid,args
[[ $(stat -c %u "/proc/$pid") == "$(id -u nobody)" ]]
grep -q '^NoNewPrivs:[[:space:]]*1' "/proc/$pid/status"
sudo systemctl stop securelab-practice-worker-fixed
echo 'F5 VERIFIED: worker runs unprivileged with no new privileges'
# F6 integrity monitoring: create a protected baseline, then detect drift.
sudo install -d -m 0700 /var/lib/securelab/integrity
sudo sha256sum "$base/config.txt" | sudo tee /var/lib/securelab/integrity/practice.sha256 >/dev/null
sudo chmod 0600 /var/lib/securelab/integrity/practice.sha256
sudo sha256sum -c /var/lib/securelab/integrity/practice.sha256
printf 'drift=true\n' | sudo tee -a "$base/config.txt" >/dev/null
if sudo sha256sum -c /var/lib/securelab/integrity/practice.sha256; then exit 1; fi
printf 'approved=true\n' | sudo tee "$base/config.txt" >/dev/null
sudo sha256sum -c /var/lib/securelab/integrity/practice.sha256
echo 'F6 VERIFIED: protected integrity baseline detects drift and passes after restoration'
snapshot > "$out/after.txt"; cat "$out/after.txt"
