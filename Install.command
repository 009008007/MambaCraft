#!/bin/bash
# Install from bundled, hash-pinned wheels. No sudo, no remote installer scripts.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd -P)"
APP="$HOME/Applications/MambaCraft.app"
DATA="$HOME/Library/Application Support/MambaCraft1"
VENV="$DATA/python-1.3-rc22"
if [[ "$(uname -s)" != Darwin ]]; then echo '此安裝程式只支援 macOS。'; exit 1; fi
PYTHON_BIN=''
for candidate in "$HOME/Library/Application Support/MambaCraft/helper-venv/bin/python" /opt/homebrew/bin/python3 /usr/local/bin/python3 "$(command -v python3 || true)"; do
  if [[ -x "$candidate" ]] && "$candidate" -c 'import sys; assert sys.version_info >= (3,10)' >/dev/null 2>&1; then PYTHON_BIN="$candidate"; break; fi
done
if [[ -z "$PYTHON_BIN" ]]; then
  echo '需要 Python 3.10 或更新版本。請先從 https://www.python.org/downloads/macos/ 安裝 Python，再執行 Start.command。'
  exit 1
fi
mkdir -p "$DATA" "$HOME/Applications"
chmod 700 "$DATA"
echo '檢查並安全關閉舊版 Helper…'
"$PYTHON_BIN" "$ROOT/app/desktop.py" --data "$DATA" --stop-helper
# A second installer must not mutate a running helper or another installation.
exec 9>"$DATA/install.lock"
"$PYTHON_BIN" - "$DATA" <<'PY'
import fcntl,sys
from pathlib import Path
# Lock remains in the parent fd after this process exits.
try: fcntl.flock(9,fcntl.LOCK_EX|fcntl.LOCK_NB)
except BlockingIOError: raise SystemExit('另一個安裝器正在執行。')
root=Path(sys.argv[1]); f=(root/'server.lock').open('a')
try: fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
except BlockingIOError: raise SystemExit('請先在 MambaCraft 中按「結束啟動器」，再更新。')
PY
if [[ -e "$APP" ]]; then
  OLD_ID="$(/usr/libexec/PlistBuddy -c 'Print :CFBundleIdentifier' "$APP/Contents/Info.plist" 2>/dev/null || true)"
  if [[ "$OLD_ID" != 'org.mambacraft.launcher' ]]; then echo '目標位置有其他應用程式，停止覆蓋。'; exit 1; fi
fi
echo '[1/4] 驗證套件並準備 Python 環境…'
"$PYTHON_BIN" "$ROOT/verify_package.py"
if [[ ! -x "$VENV/bin/python" ]]; then "$PYTHON_BIN" -m venv "$VENV"; fi
"$VENV/bin/python" -m pip install --disable-pip-version-check --no-index --find-links "$ROOT/wheels" --require-hashes -r "$ROOT/requirements-lock.txt"
"$VENV/bin/python" -c 'import requests; print("依賴已準備完成。")'
STAGE="$(mktemp -d "$HOME/Applications/.MambaCraft-stage.XXXXXX")"
trap 'rm -rf -- "$STAGE"' EXIT
NEW_APP="$STAGE/MambaCraft.app"
echo '[2/4] 建立 macOS 啟動程式…'
osacompile -o "$NEW_APP" "$ROOT/mac.applescript"
RES="$NEW_APP/Contents/Resources"
cp -R "$ROOT/app" "$RES/app"
printf '%s\n' "$VENV/bin/python" > "$RES/python-path.txt"
printf '%s\n' '1.3-rc22' > "$RES/release.txt"
/usr/bin/shasum -a 256 "$ROOT/SHA256SUMS.json" | /usr/bin/awk '{print $1}' > "$RES/package-manifest.sha256"
"$VENV/bin/python" - "$NEW_APP/Contents/Info.plist" <<'PY'
import plistlib,sys
p=sys.argv[1]
with open(p,'rb') as f: d=plistlib.load(f)
d.update(CFBundleIdentifier='org.mambacraft.launcher',CFBundleName='MambaCraft',CFBundleDisplayName='MambaCraft',CFBundleShortVersionString='1.3',CFBundleVersion='34',NSHighResolutionCapable=True,CFBundleURLTypes=[{'CFBundleURLName':'org.mambacraft.launcher.open','CFBundleURLSchemes':['mambacraft'],'CFBundleTypeRole':'Viewer'}])
with open(p,'wb') as f: plistlib.dump(d,f)
PY
echo '[3/4] 本機簽署及檢查…'
/usr/bin/codesign --force --sign - "$NEW_APP"
/usr/bin/codesign --verify "$NEW_APP"
echo '[4/4] 安裝應用程式…'
if [[ -e "$APP" ]]; then mv "$APP" "$STAGE/previous.app"; fi
if ! mv "$NEW_APP" "$APP"; then
  if [[ -e "$STAGE/previous.app" ]]; then mv "$STAGE/previous.app" "$APP"; fi
  echo '安裝失敗，已嘗試還原舊版。'; exit 1
fi
LSREGISTER='/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister'
if [[ -x "$LSREGISTER" ]]; then "$LSREGISTER" -f "$APP" || echo 'LaunchServices 重新註冊未完成；可從 Applications 直接開啟 MambaCraft.app。'; fi
echo "完成：$APP"
echo '遊戲資料保存在 ~/Library/Application Support/MambaCraft1。'
"$VENV/bin/python" "$APP/Contents/Resources/app/cleanup_helpers.py" "$DATA" "$VENV"
echo '已清理舊版 MambaCraft App 與 Helper；Minecraft 遊戲、Java、世界、Mods 及備份均保留。'
