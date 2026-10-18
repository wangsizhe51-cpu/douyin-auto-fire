#!/bin/zsh
umask 077
TASK_ROOT="${0:A:h}"
TASK_PYTHON="$TASK_ROOT/.venv/bin/python"
if [[ ! -x "$TASK_PYTHON" ]]; then
  print '请先双击同目录里的「安装Mac版.command」，完成一次安装。'
  if [[ -t 0 ]]; then read '?按回车关闭。'; fi
  exit 1
fi
cd "$TASK_ROOT" || exit 1
"$TASK_PYTHON" local_mac.py "$@"
TASK_RESULT=$?
if [[ $TASK_RESULT -ne 0 && -t 0 ]]; then
  read '?本次未完成，请查看上方提示。按回车关闭。'
fi
exit "$TASK_RESULT"
