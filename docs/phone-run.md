# 手机快速运行入口

这套方式由 GitHub Actions 在云端运行，不需要 Mac 开机或自己租服务器。手机作为启动入口；运行前仍由 GitHub 登录权限保护。

## 一次性设置

1. 将本项目 Fork 到自己的 GitHub 账号，并在 Fork 仓库的 **Actions** 页面启用工作流。
2. 在仓库的 **Settings → Secrets and variables → Actions** 中添加：
   - `DOUYIN_COOKIE`：抖音 Cookie JSON。它是登录凭证，不要发给别人或提交到代码。
   - `DOUYIN_CONFIG`：好友名单和消息配置 JSON。建议先只放 1 位好友和 1 条文字消息。
3. 首次运行时保留默认的 `dry_run=true`，点击 **Run workflow**。这只检查登录与好友定位，不发送消息。

## 添加到 iPhone 主屏幕

Fork 完成后，在 Safari 打开下面地址，把 `你的GitHub用户名` 换成自己的用户名：

```text
https://github.com/你的GitHub用户名/douyin-auto-fire/actions/workflows/send.yml
```

Safari 中点分享按钮，再选 **添加到主屏幕**。以后从主屏幕打开这个入口，在工作流页面点 **Run workflow** 即可运行检查。

若 Dry Run 成功并确认好友名单正确，正式发送时需要主动关闭 `dry_run`，并在 `confirm_send` 中输入大写 `SEND`。缺少这个确认文本，工作流会停止，不会发送。

## 安全与限制

- 不要把 GitHub Token 放在网页链接或公开快捷指令里。主屏幕入口只打开 GitHub 的登录页面，由 GitHub 校验你的权限。
- GitHub Actions 会在云端使用你配置的 Cookie；云端网络也可能触发抖音安全验证。
- 本项目使用配置文件维护好友名单，没有网页勾选好友的界面。
- 这不是完全无确认的一键发送：入口打开后仍需在 GitHub 页面确认运行，正式发送还需额外输入 `SEND`。
