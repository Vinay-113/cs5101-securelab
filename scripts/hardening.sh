#!/usr/bin/env bash
set -euo pipefail
out=${1:?evidence directory}
[[ -f /etc/securelab-vm ]] || exit 2
mkdir -p "$out"
baseline() {
  date -u --iso-8601=seconds; uname -r
  if [[ -f /var/run/reboot-required ]]; then cat /var/run/reboot-required; else echo 'No reboot-required marker'; fi
  systemctl --type=service --state=running --no-pager
  sudo ss -lntup
  sudo ufw status verbose
  apt list --upgradable 2>/dev/null
  systemctl show securelab-worker -p User -p NoNewPrivileges -p ProtectSystem -p MemoryMax
}
# An isolated teaching service makes the privilege change measurable.
cat > "$out/worker-before.service" <<'UNIT'
[Unit]
Description=SECURELAB teaching worker
[Service]
Type=exec
ExecStart=/usr/bin/sleep infinity
UNIT
sudo install -m 0644 "$out/worker-before.service" /etc/systemd/system/securelab-worker.service
sudo systemctl daemon-reload
sudo systemctl restart securelab-worker
baseline > "$out/before.txt"; cat "$out/before.txt"
sudo install -d -m 0700 /var/lib/securelab/rollback
# Capture firewall state for an exact restore, even if UFW was already active.
if ! sudo test -d /var/lib/securelab/rollback/ufw; then
 sudo cp -a /etc/ufw /var/lib/securelab/rollback/ufw
 sudo cp -a /etc/default/ufw /var/lib/securelab/rollback/ufw-default
 sudo ufw status | sudo tee /var/lib/securelab/rollback/ufw-status >/dev/null
fi
# Change 1: default deny incoming; keep guest management SSH permitted.
sudo ufw allow 22/tcp comment 'SECURELAB guest management SSH'
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw --force enable
sudo ufw status verbose | tee "$out/firewall-after.txt"
grep -q 'deny (incoming)' "$out/firewall-after.txt"
# Change 2: service privilege separation plus a constrained filesystem/process view.
cat > "$out/worker-after.service" <<'UNIT'
[Unit]
Description=SECURELAB confined teaching worker
[Service]
Type=exec
ExecStart=/usr/bin/sleep infinity
User=nobody
Group=nogroup
NoNewPrivileges=yes
ProtectSystem=strict
ProtectHome=yes
PrivateTmp=yes
PrivateDevices=yes
ProtectKernelTunables=yes
ProtectControlGroups=yes
RestrictAddressFamilies=AF_UNIX
MemoryMax=64M
TasksMax=16
[Install]
WantedBy=multi-user.target
UNIT
sudo install -m 0644 "$out/worker-after.service" /etc/systemd/system/securelab-worker.service
sudo systemctl daemon-reload; sudo systemctl restart securelab-worker
pid=$(systemctl show -p MainPID --value securelab-worker)
ps -p "$pid" -o pid,uid,euid,args
sudo cat "/proc/$pid/status" | grep -E 'Uid|CapEff|NoNewPrivs|Seccomp'
[[ $(systemctl show -p User --value securelab-worker) == nobody ]]
[[ $(systemctl show -p NoNewPrivileges --value securelab-worker) == yes ]]
# Change 3: set secure defaults for future interactive lab files.
printf 'umask 077\n' | sudo tee /etc/profile.d/securelab-umask.sh >/dev/null
sudo chmod 0644 /etc/profile.d/securelab-umask.sh
bash -c 'source /etc/profile.d/securelab-umask.sh; umask; f=$(mktemp); touch "$f"; stat -c "%a %n" "$f"; test "$(stat -c %a "$f")" = 600; rm "$f"'
# Patch state is measured, not inferred from apt update alone.
sudo apt-get update
sudo env DEBIAN_FRONTEND=noninteractive apt-get upgrade --with-new-pkgs -y
baseline > "$out/after.txt"; cat "$out/after.txt"
printf 'Verified: incoming firewall policy, confined unprivileged service, restrictive umask.\n'
