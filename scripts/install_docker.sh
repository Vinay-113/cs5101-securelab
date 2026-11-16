#!/usr/bin/env bash
# Official apt repository procedure: docs.docker.com/engine/install/ubuntu/
set -euo pipefail
[[ $(uname -s) == Linux && -f /etc/securelab-vm ]] || exit 2
if command -v docker >/dev/null; then sudo docker version; exit; fi
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /tmp/securelab-docker.asc
sudo install -m 0644 /tmp/securelab-docker.asc /etc/apt/keyrings/docker.asc
source /etc/os-release
arch=$(dpkg --print-architecture)
printf 'Types: deb\nURIs: https://download.docker.com/linux/ubuntu\nSuites: %s\nComponents: stable\nArchitectures: %s\nSigned-By: /etc/apt/keyrings/docker.asc\n' "$VERSION_CODENAME" "$arch" | sudo tee /etc/apt/sources.list.d/docker.sources >/dev/null
sudo apt-get update
sudo env DEBIAN_FRONTEND=noninteractive apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
# Do not add the student to the root-equivalent docker group.
sudo docker version
