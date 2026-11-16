#!/usr/bin/env bash
set -euo pipefail
[[ -f /etc/securelab-vm ]] || exit 2
work=$(mktemp -d)
trap 'sudo systemctl stop securelab-local-ssh 2>/dev/null || true; rm -rf "$work"' EXIT
user=$(id -un)
ssh-keygen -q -t ed25519 -N '' -C 'SECURELAB ephemeral local-only key' -f "$work/id_ed25519"
sudo install -d -m 0755 /opt/securelab/ssh /run/sshd
sudo install -m 0644 "$work/id_ed25519.pub" "/opt/securelab/ssh/$user.pub"
cat > "$work/sshd_config" <<CONFIG
Port 2222
ListenAddress 127.0.0.1
HostKey /etc/ssh/ssh_host_ed25519_key
PidFile /run/securelab-local-ssh.pid
AuthorizedKeysFile /opt/securelab/ssh/%u.pub
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitRootLogin no
PubkeyAuthentication yes
AllowUsers $user
UsePAM yes
StrictModes yes
LogLevel VERBOSE
Subsystem sftp internal-sftp
CONFIG
sudo install -m 0600 "$work/sshd_config" /etc/ssh/securelab_local_config
sudo /usr/sbin/sshd -t -f /etc/ssh/securelab_local_config
sudo systemctl stop securelab-local-ssh 2>/dev/null || true
sudo systemd-run --collect --unit=securelab-local-ssh /usr/sbin/sshd -D -e -f /etc/ssh/securelab_local_config
sleep 1
ss -lnt | grep '127.0.0.1:2222'
# Trust the key read from the locally provisioned host, not a network keyscan.
printf '[127.0.0.1]:2222 ' > "$work/known_hosts"
sudo cat /etc/ssh/ssh_host_ed25519_key.pub >> "$work/known_hosts"
ssh -F /dev/null -o BatchMode=yes -o IdentitiesOnly=yes -o StrictHostKeyChecking=yes -o UserKnownHostsFile="$work/known_hosts" -i "$work/id_ed25519" -p 2222 "$user@127.0.0.1" 'echo LOCAL_SSH_SUCCESS; id; test "$(id -u)" -ne 0'
sudo journalctl -u securelab-local-ssh --no-pager -n 30
# Verify credentials without reading or logging private key content.
sudo /usr/sbin/sshd -T -f /etc/ssh/securelab_local_config | grep -E 'listenaddress|passwordauthentication|permitrootlogin|pubkeyauthentication'
