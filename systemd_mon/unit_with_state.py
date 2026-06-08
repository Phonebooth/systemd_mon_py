from systemd_mon.state_change import StateChange


class UnitWithState(object):
    """Pairs a unit with the rolling :class:`StateChange` accumulated for it."""

    def __init__(self, unit):
        self.unit = unit
        self.state_change = StateChange()

    @property
    def name(self):
        return self.unit.name

    def append(self, state):
        self.state_change.append(state)

    @property
    def current_state(self):
        return self.state_change.last()

    # Alias matching the Ruby ``state`` reader; used as ``unit.state.active``.
    @property
    def state(self):
        return self.state_change.last()

    def reset(self):
        self.state_change = StateChange(self.current_state)
