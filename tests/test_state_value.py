import unittest
from datetime import datetime

from systemd_mon.state_value import StateValue


class TestStateValue(unittest.TestCase):
    def _sv(self, value, ok=None, fail=None):
        return StateValue("active", value, datetime.now(),
                          ok_states=ok or [], failure_states=fail or [])

    def test_ok_with_ok_states(self):
        sv = self._sv("active", ok=["active"], fail=["failed"])
        self.assertTrue(sv.is_ok())
        self.assertFalse(sv.is_fail())

    def test_fail_with_fail_states(self):
        sv = self._sv("failed", ok=["active"], fail=["failed"])
        self.assertFalse(sv.is_ok())
        self.assertTrue(sv.is_fail())

    def test_ok_defaults_to_true_with_no_states(self):
        sv = self._sv("anything")
        self.assertTrue(sv.is_ok())
        self.assertFalse(sv.is_fail())

    def test_important_when_in_ok_or_fail_list(self):
        sv = self._sv("active", ok=["active"], fail=["failed"])
        self.assertTrue(sv.important())

    def test_not_important_when_in_neither_list(self):
        sv = self._sv("activating", ok=["active"], fail=["failed"])
        self.assertFalse(sv.important())

    def test_equality(self):
        ts = datetime.now()
        a = StateValue("active", "running", ts)
        b = StateValue("sub", "running", ts)
        self.assertEqual(a, b)

    def test_display_name(self):
        sv = StateValue("active", "running", datetime.now())
        self.assertEqual(sv.display_name, "Active")
