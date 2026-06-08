class Notification(object):
    """Describes a unit state change to be delivered by notifiers."""

    def __init__(self, hostname, unit):
        self.hostname = hostname
        self.unit = unit
        self.type = self._determine_type()

    @staticmethod
    def types():
        return ["alert", "warning", "info", "ok"]

    def type_text(self):
        return self.type.capitalize()

    def _determine_type(self):
        state_change = self.unit.state_change
        if state_change.is_ok():
            if state_change.first().is_fail():
                return "ok"
            return "info"
        return "alert"
