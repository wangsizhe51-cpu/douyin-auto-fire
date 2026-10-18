# 抖音续火花 · Mac 本地版

在 Mac 上双击启动，核对好友和文字后点击「发送」。第一次扫码登录，以后复用本机登录资料；电脑只需在运行期间保持唤醒和联网。

这是 [unmev/douyin-auto-fire](https://github.com/unmev/douyin-auto-fire) 的派生版本。好友定位、消息发送和发送状态检查沿用上游，本仓库增加 Mac 本地使用流程。源码按 **PolyForm Noncommercial 1.0.0（非商业用途）** 公开，详见 [LICENSE](LICENSE) 和 [NOTICE](NOTICE)。

## 本地版增加了什么

- 可见的 Chrome / Chromium 窗口，扫码登录资料保存在项目内的独立目录。
- 中文菜单：登录、设置好友和文字、只检查好友、正式发送。
- 快捷入口：双击 → 核对弹窗 → 点击发送，结束后程序退出。
- 桌面快捷方式，以及项目专用 Python 环境的安装脚本。
- 本地发送历史：当天已成功或结果不确定的同一条消息不自动重发。

## 安装

需要 macOS、Python 3.11 或更新版本。建议装好 Google Chrome；未找到 Chrome 时安装脚本会下载 Chromium。Python 可从 [Python 官方网站](https://www.python.org/downloads/macos/) 安装。

1. 点击仓库页面的 **Code → Download ZIP**，解压到准备长期保留的位置；或者执行：

   ```bash
   git clone https://github.com/wangsizhe51-cpu/douyin-auto-fire.git
   cd douyin-auto-fire
   ```

2. 双击 `安装Mac版.command`，等待依赖安装完成。
3. 双击 `本地续火花.command`，按下一节完成首次设置。
4. 可选：双击 `创建桌面入口.command`，把快捷发送入口放到桌面。

如果下载 ZIP 后提示文件不可执行，在项目文件夹打开终端执行：

```bash
chmod u+x *.command
zsh 安装Mac版.command
```

这些是可阅读的本地脚本，没有签名或公证的 App 安装包。若 macOS 要求确认来源，请先查看脚本，再按系统提供的确认方式打开；无需关闭系统安全功能。

## 首次使用

在 `本地续火花.command` 的菜单中依次选择：

1. **登录**：在弹出的浏览器中扫码，看到私信列表后回终端按回车。
2. **设置好友和文字**：好友昵称一行一个，空行结束，再输入要发送的文字并保存。建议先用一位好友验证。
3. **只检查好友**：验证登录和定位，不发送消息。
4. **正式发送**：核对名单及文字，输入「发送」执行。

第一次设置结束后输入 `0` 关闭菜单。

## 每天怎么用

双击 `快捷续火花.command`（或桌面同名入口），核对好友和文字后点击「发送」。自动使用已保存的配置，完成后程序退出；终端窗口是否自动关闭取决于 Terminal 设置。

修改好友或文字、更新过期登录时，仍使用 `本地续火花.command`。旧菜单和快捷入口不能同时运行；旧菜单还开着时先输入 `0` 退出。

## 使用边界

- 本地版需要 Mac 唤醒并联网；不是手机独立运行方案，也没有启用自动定时。
- 抖音页面变化、登录验证或消息限制可能造成失败。检查模式通过只代表定位通过，实际送达应查看聊天记录。
- 本地版本已在维护者的 Mac 上验证运行，其他系统版本和账号仍需自行测试；不保证自动发送必然维持火花。
- 本地菜单保存的配置会在遇到错误时停止处理后续好友。发送失败或结果不确定时，应先检查聊天记录，不要删除历史后反复重试。

## 隐私与数据

本地模式不要求 GitHub Secrets，也不会调用上游的通知 Webhook。登录资料、好友配置、日志和发送历史保存在 `local-mac/`；该目录已同时排除在 Git 和 Docker 打包范围之外。

不要上传 `local-mac/`、`.env`、Cookie、登录二维码、聊天截图或包含私人信息的日志。报告问题时请先遮盖这些内容。GitHub 的源码 ZIP 不包含你的本地配置。

## 开发与上游功能

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m playwright install chromium
.venv/bin/python -m pytest -q
```

Mac 菜单入口：`local_mac.py`。可通过 `python local_mac.py --quick` 打开发送确认窗口。

浏览器集成测试默认使用 Playwright 的 Chromium；已有 Chrome 的开发者也可设置 `TEST_BROWSER_PATH` 为浏览器可执行文件路径，使用该浏览器运行同一套测试。

上游的 [Windows](docs/windows.md)、[Docker](docs/docker.md)、[服务器](docs/server.md)、[GitHub Actions](docs/github-actions.md) 说明仍保留，作为其他部署方式的参考；本仓库主要维护 Mac 本地流程。上游专用的 Docker 发布和 CNB 镜像同步工作流在本 fork 中不会执行。

## 许可证与致谢

感谢原作者 [unmev](https://github.com/unmev) 和上游贡献者。本项目为基于原作的修改版，并非独立重写。

沿用 [PolyForm Noncommercial 1.0.0](https://polyformproject.org/licenses/noncommercial/1.0.0)，保留原版权声明。可以在许可证允许的非商业用途下使用、修改和分发；商业用途请联系相关权利人获取授权。公开源码不等于允许自由商用。
