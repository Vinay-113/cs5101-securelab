#!/usr/bin/env bash
# Local portable Lima install, pinned to a verified official release.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
[[ $(uname -s) == Darwin && $(uname -m) == arm64 ]] || { echo 'Use your existing Ubuntu VM or adapt vm/securelab.yaml for this host.' >&2; exit 2; }
mkdir -p "$ROOT/.tools/downloads" "$ROOT/.tools/lima" "$ROOT/tmp"
archive="$ROOT/.tools/downloads/lima.tar.gz"
url=https://github.com/lima-vm/lima/releases/download/v2.3.0/lima-2.3.0-Darwin-arm64.tar.gz
if [[ ! -f $archive ]]; then curl -fL --retry 3 "$url" -o "$archive"; fi
python3 - "$archive" <<'PY'
import hashlib,sys
p=sys.argv[1]
actual=hashlib.sha256(open(p,'rb').read()).hexdigest()
assert actual == 'b7af444bd8f91d3c307477e562f2cf3bd7595d62b9429185e4fa841563578cfc', 'Archive checksum mismatch; remove and download again'
print('Lima archive checksum verified')
PY
tar -xzf "$archive" -C "$ROOT/.tools/lima"
"$ROOT/.tools/lima/bin/limactl" --version
