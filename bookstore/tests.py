import hashlib
import hmac
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

from django.conf import settings
from django.test import Client, SimpleTestCase, override_settings

from .deployment import update_checkout_and_reload, schedule_deployment


@override_settings(GITHUB_WEBHOOK_SECRET="test-only-webhook-secret")
class WebhookTests(SimpleTestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.payload = {"ref": "refs/heads/main", "repository": {"full_name": "guiga-dev/ebac-bookstore"}}

    def send(self, payload=None, event="push", signature=None):
        body = json.dumps(self.payload if payload is None else payload).encode()
        signature = signature or "sha256=" + hmac.new(b"test-only-webhook-secret", body, hashlib.sha256).hexdigest()
        return self.client.post("/update_server/", body, content_type="application/json", HTTP_X_GITHUB_EVENT=event, HTTP_X_HUB_SIGNATURE_256=signature)

    @patch("bookstore.views.schedule_deployment")
    def test_invalid_signature_and_get_do_not_update(self, schedule):
        self.assertEqual(self.send(signature="sha256=" + "0" * 64).status_code, 403)
        self.assertEqual(self.client.get("/update_server/").status_code, 405)
        schedule.assert_not_called()

    @override_settings(GITHUB_WEBHOOK_SECRET="")
    @patch("bookstore.views.schedule_deployment")
    def test_missing_secret_fails_closed(self, schedule):
        self.assertEqual(self.send(event="ping").status_code, 503)
        schedule.assert_not_called()

    @patch("bookstore.views.schedule_deployment")
    def test_signed_ping_does_not_deploy(self, schedule):
        self.assertEqual(self.send(event="ping").status_code, 200)
        schedule.assert_not_called()

    @patch("bookstore.views.schedule_deployment")
    def test_wrong_ref_repository_or_deleted_push_cannot_update(self, schedule):
        for payload in [
            {**self.payload, "ref": "refs/heads/other; touch /tmp/unwanted"},
            {**self.payload, "repository": {"full_name": "other/repo"}},
            {**self.payload, "deleted": True},
        ]:
            self.assertEqual(self.send(payload).status_code, 403)
        self.assertEqual(self.send(event="issues").status_code, 400)
        schedule.assert_not_called()

    @patch("bookstore.views.schedule_deployment")
    def test_authorized_push_schedules_mocked_update(self, schedule):
        with TemporaryDirectory(dir=settings.BASE_DIR) as directory:
            path = Path(directory) / "site_wsgi.py"
            path.write_text("# test only", encoding="utf-8")
            with override_settings(PYTHONANYWHERE_WSGI_FILE=str(path)):
                self.assertEqual(self.send().status_code, 202)
        schedule.assert_called_once_with()

    def test_hello_template(self):
        response = self.client.get("/hello/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hello_world.html")
        self.assertContains(response, "Guilherme Rodrigues")


class DeploymentTests(SimpleTestCase):
    @patch("bookstore.deployment.os.utime")
    @patch("bookstore.deployment.subprocess.run")
    def test_fixed_git_commands_then_wsgi_touch(self, run, touch):
        run.return_value = SimpleNamespace(stdout="main\n")
        with TemporaryDirectory(dir=settings.BASE_DIR) as directory:
            path = Path(directory) / "site_wsgi.py"
            path.write_text("# test only", encoding="utf-8")
            with override_settings(PYTHONANYWHERE_WSGI_FILE=str(path)):
                update_checkout_and_reload()
            commands = [call.args[0] for call in run.call_args_list]
            root = str(Path(settings.BASE_DIR).resolve())
            self.assertEqual(commands, [
                ["git", "-C", root, "symbolic-ref", "--short", "HEAD"],
                ["git", "-C", root, "diff", "--quiet", "HEAD", "--"],
                ["git", "-C", root, "fetch", "--no-tags", "https://github.com/guiga-dev/ebac-bookstore.git", "main"],
                ["git", "-C", root, "merge", "--ff-only", "FETCH_HEAD"],
            ])
            self.assertTrue(all(call.kwargs["shell"] is False for call in run.call_args_list))
            touch.assert_called_once_with(path.resolve(), None)

    @patch("bookstore.deployment.os.utime")
    @patch("bookstore.deployment.subprocess.run", return_value=SimpleNamespace(stdout="wrong-branch\n"))
    def test_wrong_local_branch_never_touches_wsgi(self, run, touch):
        with TemporaryDirectory(dir=settings.BASE_DIR) as directory:
            path = Path(directory) / "site_wsgi.py"
            path.write_text("# test only", encoding="utf-8")
            with override_settings(PYTHONANYWHERE_WSGI_FILE=str(path)):
                with self.assertRaises(RuntimeError):
                    update_checkout_and_reload()
        self.assertEqual(run.call_count, 1)
        touch.assert_not_called()

    @patch("bookstore.deployment.threading.Timer")
    def test_reload_work_starts_after_response_delay(self, timer):
        schedule_deployment()
        self.assertEqual(timer.call_args.args[0], 1.0)
        timer.return_value.start.assert_called_once_with()
