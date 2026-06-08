import json
import unittest

try:
    from unittest.mock import patch, MagicMock
except ImportError:
    from mock import patch, MagicMock

from systemd_mon.notifiers.slack import Slack
from systemd_mon.notification import Notification
from systemd_mon.state import State
from systemd_mon.state_change import StateChange
from systemd_mon.unit_with_state import UnitWithState


class FakeUnit(object):
    name = "nginx.service"


def _make_notification(states, hostname="testhost"):
    unit = FakeUnit()
    uws = UnitWithState(unit)
    for s in states:
        uws.append(s)
    return Notification(hostname, uws)


def _ok():
    return State("active", "running", "loaded", "enabled")


def _fail():
    return State("failed", "failed", "loaded", "enabled")


class TestSlackNotifier(unittest.TestCase):
    def _notifier(self):
        return Slack({"webhook_url": "https://hooks.slack.com/test"})

    @patch("systemd_mon.notifiers.slack.urlopen")
    def test_notify_start(self, mock_urlopen):
        mock_urlopen.return_value.__enter__ = lambda s: s
        mock_urlopen.return_value.__exit__ = MagicMock(return_value=False)
        self._notifier().notify_start("myhost")
        self.assertTrue(mock_urlopen.called)
        req = mock_urlopen.call_args[0][0]
        body = json.loads(req.data.decode("utf-8"))
        self.assertIn("starting", body["attachments"][0]["text"])
        self.assertEqual(body["attachments"][0]["color"], "good")

    @patch("systemd_mon.notifiers.slack.urlopen")
    def test_notify_stop(self, mock_urlopen):
        mock_urlopen.return_value.__enter__ = lambda s: s
        mock_urlopen.return_value.__exit__ = MagicMock(return_value=False)
        self._notifier().notify_stop("myhost")
        req = mock_urlopen.call_args[0][0]
        body = json.loads(req.data.decode("utf-8"))
        self.assertEqual(body["attachments"][0]["color"], "danger")

    @patch("systemd_mon.notifiers.slack.urlopen")
    def test_notify_alert(self, mock_urlopen):
        mock_urlopen.return_value.__enter__ = lambda s: s
        mock_urlopen.return_value.__exit__ = MagicMock(return_value=False)
        n = _make_notification([_ok(), _fail()])
        self._notifier().notify(n)
        req = mock_urlopen.call_args[0][0]
        body = json.loads(req.data.decode("utf-8"))
        self.assertEqual(body["attachments"][0]["color"], "danger")
        self.assertIn("Alert", body["text"])

    @patch("systemd_mon.notifiers.slack.urlopen")
    def test_notify_recovery(self, mock_urlopen):
        mock_urlopen.return_value.__enter__ = lambda s: s
        mock_urlopen.return_value.__exit__ = MagicMock(return_value=False)
        n = _make_notification([_fail(), _ok()])
        self._notifier().notify(n)
        req = mock_urlopen.call_args[0][0]
        body = json.loads(req.data.decode("utf-8"))
        self.assertEqual(body["attachments"][0]["color"], "good")

    @patch("systemd_mon.notifiers.slack.urlopen")
    def test_fields_contain_hostname_and_unit(self, mock_urlopen):
        mock_urlopen.return_value.__enter__ = lambda s: s
        mock_urlopen.return_value.__exit__ = MagicMock(return_value=False)
        n = _make_notification([_ok(), _fail()])
        self._notifier().notify(n)
        req = mock_urlopen.call_args[0][0]
        body = json.loads(req.data.decode("utf-8"))
        titles = [f["title"] for f in body["attachments"][0]["fields"]]
        self.assertIn("Hostname", titles)
        self.assertIn("Unit", titles)

    def test_requires_webhook_url(self):
        with self.assertRaises(Exception):
            Slack({})
