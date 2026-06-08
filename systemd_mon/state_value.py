class StateValue(object):
    """A single named state value (e.g. active=running) with ok/failure sets."""

    def __init__(self, name, value, timestamp, ok_states=None, failure_states=None):
        self.name = name
        self.value = value
        self.ok_states = ok_states or []
        self.failure_states = failure_states or []
        self.timestamp = timestamp

    @property
    def display_name(self):
        return self.name.capitalize()

    def important(self):
        return self.value in self.ok_states or self.value in self.failure_states

    def is_ok(self):
        if self.ok_states:
            return self.value in self.ok_states
        return True

    def is_fail(self):
        if self.failure_states:
            return self.value in self.failure_states
        return False

    def __str__(self):
        return self.value

    def __eq__(self, other):
        if isinstance(other, str):
            return self.value == other
        return isinstance(other, StateValue) and self.value == other.value

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.value)

    def __repr__(self):
        return "StateValue({0!r}, {1!r})".format(self.name, self.value)
