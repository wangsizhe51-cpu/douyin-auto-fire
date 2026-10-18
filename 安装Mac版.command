#!/bin/zsh
set -eu
umask 077
TASK_ROOT="${0:A:h}"
cd "$TASK_ROOT"

finish() {
  TASK_STATUS=$?
  if [[ $TASK_STATUS -ne 0 ]]; then print '\n安装未完成，请查看上面的错误。'; fi
  if [[ -t 0 ]]; then read '?按回车关闭。'; fi
  return "$TASK_STATUS"
}
trap finish EXIT
if [[ "$(uname -s)" != Darwin ]]; then
  print '这个安装入口用于 macOS。其他平台请参阅 README。'
  exit 1
fi
TASK_PYTHON=""
for TASK_CANDIDATE in "${DY_LOCAL_PYTHON:-}" "$TASK_ROOT/.venv/bin/python" python3.13 python3.12 python3.11 python3 /opt/homebrew/bin/python3 /usr/local/bin/python3; do
  [[ -n "$TASK_CANDIDATE" ]] || continue
  if command -v "$TASK_CANDIDATE" >/dev/null 2>&1 && "$TASK_CANDIDATE" -c 'import sys; raise SystemExit(sys.version_info < (3, 11))' 2>/dev/null; then
    TASK_PYTHON="$TASK_CANDIDATE"
    break
  fi
done
if [[ -z "$TASK_PYTHON" ]]; then
  print '需要 Python 3.11 或更新版本。请先从 https://www.python.org/downloads/macos/ 安装，再重新双击此文件。'
  exit 1
fi
print '正在准备项目专用 Python 环境…'
if [[ ! -x "$TASK_ROOT/.venv/bin/python" ]]; then
  "$TASK_PYTHON" -m venv "$TASK_ROOT/.venv"
fi
if ! "$TASK_ROOT/.venv/bin/python" -c 'import sys; raise SystemExit(sys.version_info < (3, 11))'; then
  print '项目现有 .venv 版本过旧。请将该目录改名备份后重新安装；local-mac 里的个人配置无需移动。'
  exit 1
fi
"$TASK_ROOT/.venv/bin/python" -m pip install -r "$TASK_ROOT/requirements.txt"
if [[ ! -x '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' ]]; then
  print '未找到 Google Chrome，正在下载项目所需的 Chromium…'
  "$TASK_ROOT/.venv/bin/python" -m playwright install chromium
fi
chmod u+x "$TASK_ROOT/本地续火花.command" "$TASK_ROOT/快捷续火花.command" "$TASK_ROOT/创建桌面入口.command"
print '\n安装完成！双击「本地续火花.command」登录并设置好友。'
print '日常使用「快捷续火花.command」；需要桌面图标时运行「创建桌面入口.command」。'
