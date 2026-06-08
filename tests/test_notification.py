import unittest

from systemd_mon.state import State
from systemd_mon.state_change import StateChange
from systemd_mon.notification import Notification
from systemd_mon.unit_with_state import UnitWithState


class FakeUnit(object):
    name = "test.service"


def _notification(*states):
    unit = FakeUnit()
    uws = UnitWithState(unit)
    for s in states:
        uws.append(s)
    return Notification("myhost", uws)


def ok():
    return State("active", "running", "loaded", "enabled")


def fail():
    return State("failed", "failed", "loaded", "enabled")


class TestNotificationType(unittest.TestCase):
    def test_alert_when_currently_failed(self):
        n = _notification(ok(), fail())
        self.assertEqual(n.type, "alert")

    def test_ok_when_recovered(self):
        n = _notification(fail(), ok())
        self.assertEqual(n.type, "ok")

    def test_info_when_ok_throughout(self):
        n = _notification(ok(), ok())
        self.assertEqual(n.type, "info")

    def test_type_text_capitalised(self):
        n = _notification(ok(), fail())
        self.assertEqual(n.type_text(), "Alert")
