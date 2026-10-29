#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd -P)"
if [[ "$(uname -s)" != Darwin ]]; then echo '此卸載程式只適用於 macOS。'; exit 1; fi
PYTHON_BIN=''
for candidate in "$(command -v python3 || true)" /opt/homebrew/bin/python3 /usr/local/bin/python3; do
  if [[ -x "$candidate" ]] && "$candidate" -c 'import sys; assert sys.version_info >= (3,10)' >/dev/null 2>&1; then PYTHON_BIN="$candidate"; break; fi
done
if [[ -z "$PYTHON_BIN" ]]; then echo '需要 Python 3.10 或更新版本才能安全列出與移除檔案。'; exit 1; fi
exec "$PYTHON_BIN" "$ROOT/app/uninstall.py" "$@"
