#!/bin/zsh
set -eu
TASK_ROOT="${0:A:h}"
TASK_SHORTCUT="$HOME/Desktop/快捷续火花.command"
TASK_SOURCE="$TASK_ROOT/快捷续火花.command"
if [[ -e "$TASK_SHORTCUT" || -L "$TASK_SHORTCUT" ]]; then
  if [[ "${TASK_SHORTCUT:A}" == "${TASK_SOURCE:A}" ]]; then
    print '桌面入口已经存在。'
  else
    print '桌面已有同名文件，未覆盖。请将旧文件改名后再运行此入口。'
    if [[ -t 0 ]]; then read '?按回车关闭。'; fi
    exit 1
  fi
else
  ln -s "$TASK_SOURCE" "$TASK_SHORTCUT"
  print '桌面入口已创建。项目文件夹请保留在原位置。'
fi
if [[ -t 0 ]]; then read '?按回车关闭。'; fi
