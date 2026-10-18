"""Local-mode boundaries; no Douyin traffic or real messages."""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import local_mac
from app.browser import open_douyin


class LocalModeTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        previous_umask = os.umask(0o077)
        self.addCleanup(os.umask, previous_umask)
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.data = Path(self.temporary.name)
        self.enterContext(patch.object(local_mac, "DATA", self.data))
        self.enterContext(patch.dict(os.environ, {}, clear=True))
        local_mac.configure_environment()

    async def test_persistent_session_uses_same_profile_without_cookie_import(self):
        settings = local_mac.settings()
        self.assertFalse(settings.headless)
        self.assertEqual(settings.profile_dir, self.data / "profile")
        context = MagicMock()
        page = MagicMock()
        context.pages = [page]
        context.close = AsyncMock()
        context.add_cookies = AsyncMock()
        context.new_page = AsyncMock()
        playwright = MagicMock()
        playwright.stop = AsyncMock()
        playwright.chromium.launch_persistent_context = AsyncMock(return_value=context)
        playwright.chromium.launch = AsyncMock()
        manager = MagicMock()
        manager.start = AsyncMock(return_value=playwright)
        with patch("app.browser.async_playwright", return_value=manager):
            with self.assertRaisesRegex(RuntimeError, "test failure"):
                async with open_douyin(settings) as session:
                    self.assertIs(session.page, page)
                    raise RuntimeError("test failure")
        self.assertEqual(playwright.chromium.launch_persistent_context.call_args.args[0], str(self.data / "profile"))
        playwright.chromium.launch.assert_not_awaited()
        context.add_cookies.assert_not_awaited()
        context.close.assert_awaited_once()
        playwright.stop.assert_awaited_once()

    def test_local_mode_does_not_inherit_cloud_credentials_or_notifications(self):
        for name in ("DOUYIN_COOKIE", "DOUYIN_STORAGE_STATE", "WEBHOOK_URL", "DINGTALK_WEBHOOK"):
            os.environ[name] = "cloud-secret"
        local_mac.configure_environment()
        settings = local_mac.settings()
        self.assertIsNone(settings.cookie)
        self.assertIsNone(settings.webhook_url)
        self.assertIsNone(settings.dingtalk_webhook)
        self.assertEqual(settings.task_config_path, self.data / "config.json")

    def test_config_saves_only_entered_friends_and_keeps_duplicate_protection(self):
        with patch("builtins.input", side_effect=["好友甲", "好友甲", "", "你好", "y"]):
            local_mac.edit_config()
        task = local_mac.load_task(local_mac.settings())
        self.assertEqual([target.name for target in task.targets], ["好友甲"])
        self.assertEqual(task.targets[0].messages[0].content, "你好")
        self.assertTrue(task.prevent_duplicates)
        self.assertFalse(task.continue_on_error)

    async def test_dry_run_passes_no_send_mode_and_cancelled_send_never_runs(self):
        with patch("builtins.input", side_effect=["好友甲", "", "你好", "y"]):
            local_mac.edit_config()
        runner = AsyncMock(return_value=0)
        with patch.object(local_mac, "run", runner):
            await local_mac.execute(dry_run=True)
            runner.assert_awaited_once_with(dry_run=True, env_file=os.devnull)
            runner.reset_mock()
            with patch("builtins.input", return_value=""):
                await local_mac.execute(dry_run=False)
            runner.assert_not_awaited()

    async def test_quick_cancel_never_runs_and_confirmation_runs_once(self):
        with patch("builtins.input", side_effect=["好友甲", "", "你好", "y"]):
            local_mac.edit_config()
        runner = AsyncMock(return_value=1)
        with patch.object(local_mac, "run", runner), patch.object(local_mac, "confirm_quick_send") as confirm:
            confirm.return_value = False
            self.assertEqual(await local_mac.execute(dry_run=False, quick=True), 0)
            runner.assert_not_awaited()
            confirm.return_value = True
            self.assertEqual(await local_mac.execute(dry_run=False, quick=True), 1)
            runner.assert_awaited_once_with(dry_run=False, env_file=os.devnull)

    def test_quick_mode_exits_without_menu_and_releases_locks(self):
        with patch("builtins.input", side_effect=["好友甲", "", "你好", "y"]):
            local_mac.edit_config()
        with patch.object(local_mac, "execute", AsyncMock(return_value=1)) as execute:
            with patch("builtins.input", side_effect=AssertionError("Quick mode must not show the menu")):
                self.assertEqual(local_mac.main(["--quick"]), 1)
            execute.assert_awaited_once_with(dry_run=False, quick=True)
        self.assertFalse((self.data / "session.lock").exists())
        self.assertFalse((self.data / "artifacts" / "run.lock").exists())

    def test_dialog_cancel_or_failure_does_not_authorize_sending(self):
        with patch.object(local_mac.subprocess, "run") as dialog:
            dialog.return_value = subprocess.CompletedProcess([], 1, "", "User canceled. (-128)")
            self.assertFalse(local_mac.confirm_quick_send('好友 "test" $(literal)'))
            self.assertEqual(dialog.call_args.args[0][-1], '好友 "test" $(literal)')
            dialog.return_value = subprocess.CompletedProcess([], 1, "", "GUI unavailable")
            with self.assertRaisesRegex(RuntimeError, "无法显示"):
                local_mac.confirm_quick_send("test")


if __name__ == "__main__":
    unittest.main()
