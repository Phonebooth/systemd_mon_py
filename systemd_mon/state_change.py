class StateChange(object):
    """A sequence of :class:`State` snapshots for one unit, with analysis helpers.

    The first state is the baseline; subsequent states are "changes". The class
    decides whether a sequence is worth notifying about (``important``) and
    summarises it (``status_text``).
    """

    def __init__(self, original_state=None):
        self.states = []
        if original_state is not None:
            self.states.append(original_state)

    def first(self):
        return self.states[0]

    def last(self):
        return self.states[-1]

    def length(self):
        return len(self.states)

    def append(self, state):
        self.states.append(state)

    def __iter__(self):
        return iter(self.states)

    def changes(self):
        return self.states[1:]

    def is_recovery(self):
        return self.first().is_fail() and self.last().is_ok()

    def is_ok(self):
        return self.last().is_ok()

    def is_fail(self):
        return self.last().is_fail()

    # NOTE: the comparisons below mirror the Ruby source, which compares a
    # StateValue to a plain string (e.g. ``s.active == "deactivating"``).
    # StateValue equality only matches other StateValues, so these predicates
    # behave exactly as they do upstream.
    def is_restart(self):
        return (self.first().is_ok() and self.last().is_ok() and
                any(s.active == "deactivating" for s in self.changes()))

    def is_auto_restart(self):
        return (self.first().is_ok() and self.last().is_ok() and
                any(s.sub == "auto-restart" for s in self.changes()))

    def is_reload(self):
        return (self.first().is_ok() and self.last().is_ok() and
                any(s.active == "reloading" for s in self.changes()))

    def is_still_fail(self):
        return self.length() > 1 and self.first().is_fail() and self.last().is_fail()

    def status_text(self):
        if self.is_recovery():
            return "recovered"
        elif self.is_auto_restart():
            return "automatically restarted"
        elif self.is_restart():
            return "restarted"
        elif self.is_reload():
            return "reloaded"
        elif self.is_still_fail():
            return "still failed"
        elif self.is_fail():
            return "failed"
        else:
            return "started"

    def important(self):
        if self.length() == 1:
            return self.first().is_fail()
        return any(row[-1].important() for row in self.diff())

    def zipped(self):
        if self.length() == 1:
            # A single state has no cross-time rows; wrap each value so that
            # diff/to_s/the formatter can treat rows uniformly as lists.
            return [[sv] for sv in self.first().all_states]
        changes_states = [c.all_states for c in self.changes()]
        return [list(row) for row in zip(self.first().all_states, *changes_states)]

    def diff(self):
        result = []
        for row in self.zipped():
            match = row[0].value
            if not all(sv.value == match for sv in row):
                result.append(row)
        return result

    def __str__(self):
        out = ""
        for row in self.diff():
            head = row[0]
            rest = row[1:]
            out += "{0} state changed from {1} to ".format(head.name, head.value)
            out += " then ".join(sv.value for sv in rest)
            out += "\n"
        return out
