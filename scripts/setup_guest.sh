#!/usr/bin/env bash
set -euo pipefail
[[ $(uname -s) == Linux ]] || { echo 'Linux VM required.' >&2; exit 2; }
virt=$(systemd-detect-virt --vm 2>/dev/null) || { echo 'A disposable VM is required.' >&2; exit 2; }
[[ -n $virt && $virt != none ]] || exit 2
source /etc/os-release
[[ $ID == ubuntu ]] || { echo 'Ubuntu guest required.' >&2; exit 2; }
sudo -n true
sudo apt-get update
sudo env DEBIAN_FRONTEND=noninteractive apt-get upgrade --with-new-pkgs -y
sudo env DEBIAN_FRONTEND=noninteractive apt-get install -y build-essential gcc gdb strace procps psmisc acl libcap2-bin openssh-server apparmor apparmor-utils net-tools iproute2 lsof file binutils checksec ufw python3 python3-reportlab curl ca-certificates auditd
# Refuse to repurpose pre-existing accounts. Our accounts have no passwords.
for user in alice bob; do
 if id "$user" &>/dev/null; then
   [[ $(getent passwd "$user" | cut -d: -f5) == 'SECURELAB test account' ]] || { echo "Existing non-lab account: $user" >&2; exit 1; }
 else
   sudo useradd -m -c 'SECURELAB test account' -s /bin/bash "$user"
 fi
done
sudo groupadd -f securelab
sudo usermod -aG securelab alice
sudo install -d -m 0755 -o root -g securelab /opt/securelab
sudo touch /etc/securelab-vm
sudo chmod 0644 /etc/securelab-vm
# No public exposure: only a loopback SSH listener. VZ console/limactl use
# their own managed SSH port; preserve their configuration during setup.
printf 'Prepared %s %s (%s)\n' "$PRETTY_NAME" "$(uname -r)" "$(uname -m)"
