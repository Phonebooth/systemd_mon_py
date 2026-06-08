import unittest

from systemd_mon.notifier_loader import NotifierLoader


class TestCamelCase(unittest.TestCase):
    def _cc(self, name):
        return NotifierLoader._camel_case(name)

    def test_single_word(self):
        self.assertEqual(self._cc("slack"), "Slack")

    def test_snake_case(self):
        self.assertEqual(self._cc("my_notifier"), "MyNotifier")

    def test_already_camel(self):
        self.assertEqual(self._cc("Slack"), "Slack")

    def test_email(self):
        self.assertEqual(self._cc("email"), "Email")


class TestGetClass(unittest.TestCase):
    def test_loads_slack(self):
        from systemd_mon.notifiers.slack import Slack
        klass = NotifierLoader().get_class("slack")
        self.assertIs(klass, Slack)

    def test_loads_email(self):
        from systemd_mon.notifiers.email import Email
        klass = NotifierLoader().get_class("email")
        self.assertIs(klass, Email)
