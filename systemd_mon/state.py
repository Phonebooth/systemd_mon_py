from datetime import datetime

from systemd_mon.state_value import StateValue


class State(object):
    """Snapshot of a unit's active/sub/loaded/unit-file state at a point in time."""

    def __init__(self, active, sub, loaded, unit_file, type=None):
        timestamp = datetime.now()
        active_ok, active_fail = self.active_states(type)
        file_ok, file_fail = self.file_states(type)
        self.active = StateValue("active", active, timestamp, active_ok, active_fail)
        self.sub = StateValue("status", sub, timestamp)
        self.loaded = StateValue("loaded", loaded, timestamp, ["loaded"])
        self.unit_file = StateValue("file", unit_file, timestamp, file_ok, file_fail)
        self.all_states = [self.active, self.sub, self.loaded, self.unit_file]

    def active_states(self, type):
        if type == "oneshot":
            return (["inactive"], ["failed"])
        return (["active"], ["inactive", "failed"])

    def file_states(self, type):
        if type == "oneshot":
            return ([], [])
        return (["enabled", "linked-runtime", "static"], ["disabled"])

    def __iter__(self):
        return iter(self.all_states)

    def is_ok(self):
        return all(s.is_ok() for s in self.all_states)

    def is_fail(self):
        return any(s.is_fail() for s in self.all_states)

    def __str__(self):
        return ", ".join(str(s) for s in self.all_states)

    def __eq__(self, other):
        return isinstance(other, State) and self.all_states == other.all_states

    def __ne__(self, other):
        return not self.__eq__(other)
