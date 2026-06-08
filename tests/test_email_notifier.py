import smtplib
import unittest

try:
    from unittest.mock import patch, MagicMock
except ImportError:
    from mock import patch, MagicMock

from systemd_mon.errors import NotifierError
from systemd_mon.notifiers.email import Email
from systemd_mon.notification import Notification
from systemd_mon.state import State
from systemd_mon.unit_with_state import UnitWithState


class FakeUnit(object):
    name = "nginx.service"


def _make_notification(states, hostname="testhost"):
    from systemd_mon.unit_with_state import UnitWithState
    unit = FakeUnit()
    uws = UnitWithState(unit)
    for s in states:
        uws.append(s)
    return Notification(hostname, uws)


def _ok():
    return State("active", "running", "loaded", "enabled")


def _fail():
    return State("failed", "failed", "loaded", "enabled")


class TestEmailNotifier(unittest.TestCase):
    def _notifier(self):
        return Email({"to": "ops@example.com", "from": "mon@example.com"})

    def test_requires_to_address(self):
        with self.assertRaises(NotifierError):
            Email({})

    @patch("smtplib.SMTP")
    def test_sends_alert_email(self, mock_smtp_cls):
        smtp_instance = MagicMock()
        mock_smtp_cls.return_value.__enter__ = lambda s: smtp_instance
        mock_smtp_cls.return_value.__exit__ = MagicMock(return_value=False)

        n = _make_notification([_ok(), _fail()])
        self._notifier().notify(n)

        self.assertTrue(smtp_instance.send_message.called)
        msg = smtp_instance.send_message.call_args[0][0]
        self.assertIn("Alert", msg["Subject"])
        self.assertIn("nginx.service", msg["Subject"])
        self.assertEqual(msg["To"], "ops@example.com")

    @patch("smtplib.SMTP")
    def test_subject_contains_status_text(self, mock_smtp_cls):
        smtp_instance = MagicMock()
        mock_smtp_cls.return_value.__enter__ = lambda s: smtp_instance
        mock_smtp_cls.return_value.__exit__ = MagicMock(return_value=False)

        n = _make_notification([_fail(), _ok()])
        self._notifier().notify(n)

        msg = smtp_instance.send_message.call_args[0][0]
        self.assertIn("recovered", msg["Subject"])

    @patch("smtplib.SMTP")
    def test_body_ends_with_regards(self, mock_smtp_cls):
        smtp_instance = MagicMock()
        mock_smtp_cls.return_value.__enter__ = lambda s: smtp_instance
        mock_smtp_cls.return_value.__exit__ = MagicMock(return_value=False)

        n = _make_notification([_ok(), _fail()])
        self._notifier().notify(n)

        msg = smtp_instance.send_message.call_args[0][0]
        self.assertIn("Regards, SystemdMon", msg.get_payload())
