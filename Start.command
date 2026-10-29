#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd -P)"
APP="$HOME/Applications/MambaCraft.app"
if [[ "$(uname -s)" != Darwin ]]; then echo '此套件供 macOS 使用。'; exit 1; fi
EXPECTED_PACKAGE_HASH="$(/usr/bin/shasum -a 256 "$ROOT/SHA256SUMS.json" | /usr/bin/awk '{print $1}')"
INSTALLED_PACKAGE_HASH=''
if [[ -f "$APP/Contents/Resources/package-manifest.sha256" ]]; then
  INSTALLED_PACKAGE_HASH="$(cat "$APP/Contents/Resources/package-manifest.sha256")"
fi
if [[ ! -f "$APP/Contents/Resources/release.txt" ]] || [[ "$(cat "$APP/Contents/Resources/release.txt")" != '1.3-rc22' ]] || [[ "$INSTALLED_PACKAGE_HASH" != "$EXPECTED_PACKAGE_HASH" ]]; then
  bash "$ROOT/Install.command"
fi
open "$APP"
echo '已開啟 MambaCraft。日後可直接雙擊 ~/Applications/MambaCraft.app。'
