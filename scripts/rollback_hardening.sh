#!/usr/bin/env bash
set -euo pipefail
[[ -f /etc/securelab-vm && -d /var/lib/securelab/rollback/ufw ]] || exit 2
# Prefer restoring SECURELAB-CLEAN; this reverts only this project's changes.
sudo systemctl disable --now securelab-worker || true
sudo rm -f /etc/systemd/system/securelab-worker.service /etc/profile.d/securelab-umask.sh
sudo systemctl daemon-reload
sudo cp -a /var/lib/securelab/rollback/ufw/. /etc/ufw/
sudo cp -a /var/lib/securelab/rollback/ufw-default /etc/default/ufw
if sudo grep -q 'Status: active' /var/lib/securelab/rollback/ufw-status; then
 sudo ufw --force enable; sudo ufw reload
else
 sudo ufw --force disable
fi
