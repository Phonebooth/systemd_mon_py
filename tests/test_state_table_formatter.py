import unittest
from datetime import datetime

from systemd_mon.state import State
from systemd_mon.state_change import StateChange
from systemd_mon.unit_with_state import UnitWithState
from systemd_mon.formatters.state_table_formatter import StateTableFormatter


class FakeUnit(object):
    name = "nginx.service"


def _make_unit_with_states(*states):
    unit = FakeUnit()
    uws = UnitWithState(unit)
    for s in states:
        uws.append(s)
    return uws


def _ok():
    return State("active", "running", "loaded", "enabled")


def _fail():
    return State("failed", "failed", "loaded", "enabled")


class TestStateTableFormatter(unittest.TestCase):
    def test_produces_table_with_dividers(self):
        uws = _make_unit_with_states(_ok(), _fail())
        text = StateTableFormatter(uws).as_text()
        self.assertIn("---", text)
        self.assertIn("|", text)

    def test_table_has_time_column(self):
        uws = _make_unit_with_states(_ok(), _fail())
        text = StateTableFormatter(uws).as_text()
        self.assertIn("Time", text)

    def test_table_contains_changed_value(self):
        uws = _make_unit_with_states(_ok(), _fail())
        text = StateTableFormatter(uws).as_text()
        self.assertIn("failed", text)

    def test_millisecond_timestamp_format(self):
        from systemd_mon.formatters.state_table_formatter import StateTableFormatter
        ts = datetime(2024, 1, 15, 10, 30, 45, 123456)
        result = StateTableFormatter._format_time(ts)
        self.assertIn("10:30:45.", result)
        self.assertIn("123", result)
