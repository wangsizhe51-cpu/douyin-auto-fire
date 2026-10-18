"""Mac 上按需启动的本地入口。登录状态和任务资料仅保存在 local-mac。"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import subprocess
from pathlib import Path

from app.browser import open_douyin, open_private_messages
from app.config import load_settings, load_task
from app.history import AlreadyRunningError, run_lock
from app.main import run
from app.selectors import DOUYIN_CHAT_URL


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "local-mac"
CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")

CONFIRM_SCRIPT = '''on run argv
    set answer to display dialog (item 1 of argv) with title "续火花" buttons {"取消", "发送"} default button "发送" cancel button "取消"
    return button returned of answer
end run'''


def confirm_quick_send(preview: str) -> bool:
    # 好友和消息作为参数传递，避免昵称中的引号等字符成为脚本代码。
    result = subprocess.run(
        ["/usr/bin/osascript", "-e", CONFIRM_SCRIPT, preview],
        capture_output=True, text=True, check=False,
    )
    if result.returncode == 0:
        return result.stdout.strip() == "发送"
    if "-128" in result.stderr:  # 用户点击取消或按 Esc。
        return False
    raise RuntimeError("无法显示发送确认窗口，请使用原来的「本地续火花.command」入口。")


def configure_environment() -> None:
    os.umask(0o077)
    DATA.mkdir(parents=True, exist_ok=True, mode=0o700)
    # 本地入口不继承云端 Cookie、通知服务或其他账号的配置。
    os.environ.update({
        "TASK_CONFIG": str(DATA / "config.json"),
        "ARTIFACTS_DIR": str(DATA / "artifacts"),
        "DOUYIN_PROFILE_DIR": str(DATA / "profile"),
        "HEADLESS": "false",
        "TRACE": "false",
        "BROWSER_PATH": str(CHROME) if CHROME.is_file() else "",
        "DOUYIN_COOKIE": "",
        "DOUYIN_STORAGE_STATE": "",
        "DINGTALK_WEBHOOK": "",
        "DINGTALK_SECRET": "",
        "WEBHOOK_URL": "",
        "WEBHOOK_HEADERS": "",
        "WEBHOOK_TEMPLATE": "",
    })


def settings():
    # 显式指定空文件，避免自动加载上级目录的 .env。
    return load_settings(os.devnull)


def edit_config() -> None:
    print("输入要发送的好友昵称，一行一个；全部填完后直接按回车。")
    print("请使用抖音私信里实际显示的昵称，建议第一次只填一个好友。")
    names: list[str] = []
    while True:
        name = input(f"好友 {len(names) + 1}：").strip()
        if not name:
            break
        if name not in names:
            names.append(name)
    if not names:
        print("未输入好友，原配置保留。")
        return
    content = input("给以上好友发送的文字：").strip()
    if not content:
        print("文字为空，原配置保留。")
        return
    print("\n好友：" + "、".join(names))
    print("文字：" + content)
    if input("保存这份名单和文字？输入 y 保存：").strip().lower() != "y":
        print("已取消，原配置保留。")
        return
    payload = {
        "task_id": "mac-local-streak",
        "timezone": "Asia/Shanghai",
        "targets": [{"name": name, "messages": [{"type": "text", "content": content}]} for name in names],
        "send_interval_seconds": {"min": 3, "max": 8},
        "prevent_duplicates": True,
        "continue_on_error": False,
        "target_open_timeout_seconds": 25,
    }
    path = DATA / "config.json"
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)
    print("已保存。可以选择 1 登录，或选择 3 检查好友。")


async def login() -> None:
    async with open_douyin(settings()) as session:
        await session.page.goto(DOUYIN_CHAT_URL, wait_until="domcontentloaded", timeout=60_000)
        print("\n请在新打开的浏览器中登录抖音；如有验证，请自行完成。")
        print("看到私信好友列表后，回到这个终端按回车。此步骤不会发送消息。")
        await asyncio.to_thread(input)
        await open_private_messages(session.page)
        print("私信页检查通过，登录资料已保存在本机。")


async def execute(*, dry_run: bool, quick: bool = False) -> int:
    task = load_task(settings())
    preview = ["本次名单和消息："]
    for target in task.targets:
        preview.append(f"  {target.name}")
        for message in target.messages:
            preview.append("    " + (message.content if message.type == "text" else f"[{message.type}]"))
    print("\n" + "\n".join(preview))
    if not dry_run:
        print("\n发送结果不确定或已成功的同一条消息，当天不会再次自动发送。")
        confirmed = (
            confirm_quick_send("\n".join(preview) + "\n\n确认后使用已保存的登录发送，完成后自动结束。")
            if quick else input("确认发送给以上好友？输入「发送」继续，其他输入取消：").strip() == "发送"
        )
        if not confirmed:
            print("已取消。")
            return 0
    result = await run(dry_run=dry_run, env_file=os.devnull)
    if dry_run and result == 0:
        print("\n好友检查通过。本次没有发送消息；可选择 4 进行发送。")
    elif result == 0:
        print("\n任务结束；请核对上方成功、跳过的数量，并在抖音确认聊天记录。")
    else:
        print("\n任务失败。请查看上方错误；页面截图和日志保存在 local-mac/artifacts。")
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Mac 本地续火花")
    parser.add_argument("--quick", action="store_true", help="显示发送确认窗口，执行一次后退出")
    args = parser.parse_args(argv)
    configure_environment()
    with run_lock(DATA / "session.lock"):
        if args.quick:
            if not (DATA / "config.json").is_file():
                print("请先打开「本地续火花.command」，选择 1 登录、选择 2 设置好友和消息。")
                return 2
            with run_lock(DATA / "artifacts" / "run.lock"):
                return asyncio.run(execute(dry_run=False, quick=True))
        while True:
            print("\n抖音本地续火花（运行时需保持 Mac 唤醒并联网）")
            print("首次使用：1 登录 → 2 设置好友和文字 → 3 检查 → 4 发送")
            print("1  登录 / 更新登录\n2  设置好友和文字\n3  只检查好友\n4  正式发送\n0  退出")
            choice = input("请选择编号：").strip()
            if choice == "0":
                return 0
            try:
                if choice == "1":
                    asyncio.run(login())
                elif choice == "2":
                    edit_config()
                elif choice in {"3", "4"}:
                    if not (DATA / "config.json").is_file():
                        print("请先选择 2，设置好友和消息。")
                        continue
                    with run_lock(DATA / "artifacts" / "run.lock"):
                        asyncio.run(execute(dry_run=choice == "3"))
                else:
                    print("请输入 0、1、2、3 或 4。")
            except Exception as exc:
                print(f"\n本次没有完成：{exc}")
                print("登录或验证失败时请选择 1，在浏览器里重新登录。")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (KeyboardInterrupt, EOFError):
        print("\n已退出。")
    except AlreadyRunningError:
        print("已有本地续火花窗口在运行。请先在旧菜单输入 0 退出；正在发送时请等待完成。")
        raise SystemExit(1)
    except Exception as exc:
        print(f"无法启动：{exc}")
        print("需要更新登录或配置时，打开「本地续火花.command」选择 1 或 2。")
        raise SystemExit(1)
