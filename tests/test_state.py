import unittest

from systemd_mon.state import State


def _state(active="active", sub="running", loaded="loaded",
           unit_file="enabled", stype=None):
    return State(active, sub, loaded, unit_file, stype)


class TestStateNormal(unittest.TestCase):
    def test_ok_when_active(self):
        s = _state(active="active")
        self.assertTrue(s.is_ok())
        self.assertFalse(s.is_fail())

    def test_fail_when_failed(self):
        s = _state(active="failed")
        self.assertTrue(s.is_fail())
        self.assertFalse(s.is_ok())

    def test_fail_when_inactive(self):
        s = _state(active="inactive")
        self.assertTrue(s.is_fail())

    def test_fail_when_disabled(self):
        s = _state(unit_file="disabled")
        self.assertTrue(s.is_fail())

    def test_str(self):
        s = _state()
        self.assertIn("active", str(s))
        self.assertIn("running", str(s))

    def test_equality(self):
        a = _state()
        b = _state()
        self.assertEqual(a, b)


class TestStateOneshot(unittest.TestCase):
    def test_inactive_is_ok_for_oneshot(self):
        s = _state(active="inactive", stype="oneshot")
        self.assertTrue(s.is_ok())

    def test_active_is_not_ok_for_oneshot(self):
        s = _state(active="active", stype="oneshot")
        self.assertFalse(s.is_ok())

    def test_no_file_states_for_oneshot(self):
        s = _state(unit_file="disabled", stype="oneshot")
        self.assertTrue(s.unit_file.is_ok())
        self.assertFalse(s.unit_file.is_fail())
