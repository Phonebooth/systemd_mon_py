import unittest

from systemd_mon.state import State
from systemd_mon.state_change import StateChange


def ok(**kw):
    kw.setdefault("active", "active")
    kw.setdefault("sub", "running")
    kw.setdefault("loaded", "loaded")
    kw.setdefault("unit_file", "enabled")
    return State(**kw)


def fail(**kw):
    kw.setdefault("active", "failed")
    kw.setdefault("sub", "failed")
    kw.setdefault("loaded", "loaded")
    kw.setdefault("unit_file", "enabled")
    return State(**kw)


def _chain(*states):
    sc = StateChange()
    for s in states:
        sc.append(s)
    return sc


class TestStatusText(unittest.TestCase):
    def test_recovered(self):
        sc = _chain(fail(), ok())
        self.assertEqual(sc.status_text(), "recovered")

    def test_failed(self):
        sc = _chain(ok(), fail())
        self.assertEqual(sc.status_text(), "failed")

    def test_still_failed(self):
        sc = _chain(fail(), fail())
        self.assertEqual(sc.status_text(), "still failed")

    def test_started(self):
        sc = _chain(ok())
        self.assertEqual(sc.status_text(), "started")

    def test_restarted_via_deactivating(self):
        deactivating = State("deactivating", "deactivating", "loaded", "enabled")
        sc = _chain(ok(), deactivating, ok())
        self.assertEqual(sc.status_text(), "restarted")

    def test_auto_restarted_via_auto_restart_sub(self):
        auto = State("activating", "auto-restart", "loaded", "enabled")
        sc = _chain(ok(), auto, ok())
        self.assertEqual(sc.status_text(), "automatically restarted")

    def test_reloaded_via_reloading(self):
        reloading = State("reloading", "reload", "loaded", "enabled")
        sc = _chain(ok(), reloading, ok())
        self.assertEqual(sc.status_text(), "reloaded")


class TestImportant(unittest.TestCase):
    def test_single_fail_is_important(self):
        sc = _chain(fail())
        self.assertTrue(sc.important())

    def test_single_ok_is_not_important(self):
        sc = _chain(ok())
        self.assertFalse(sc.important())

    def test_ok_to_fail_is_important(self):
        sc = _chain(ok(), fail())
        self.assertTrue(sc.important())

    def test_fail_to_ok_is_important(self):
        sc = _chain(fail(), ok())
        self.assertTrue(sc.important())


class TestDiff(unittest.TestCase):
    def test_diff_excludes_unchanged_fields(self):
        s1 = ok(sub="running")
        s2 = State("active", "dead", "loaded", "enabled")
        sc = _chain(s1, s2)
        diff = sc.diff()
        names = [row[0].name for row in diff]
        self.assertIn("status", names)
        self.assertNotIn("active", names)

    def test_diff_empty_when_no_change(self):
        sc = _chain(ok(), ok())
        self.assertEqual(sc.diff(), [])
