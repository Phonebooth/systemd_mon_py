import sys


class Error(Exception):
    """Base error that remembers the original exception (for verbose mode).

    Mirrors the Ruby ``SystemdMon::Error`` which captured ``$!`` (the current
    exception) at raise time so it can be reported in verbose output.
    """

    def __init__(self, message, original=None):
        super(Error, self).__init__(message)
        self.message = message
        if original is None:
            original = sys.exc_info()[1]
        # Don't treat ourselves as our own "original".
        if original is self:
            original = None
        self.original = original


class SystemdError(Error):
    pass


class MonitorError(Error):
    pass


class UnknownUnitError(Error):
    pass


class NotificationError(Error):
    pass


class NotifierDependencyError(Error):
    pass


class NotifierError(Error):
    pass
