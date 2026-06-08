from systemd_mon.logger import Logger


class Base(object):
    def __init__(self, options):
        self.options = options or {}
        self.me = type(self).__name__

    def notify(self, notification):
        raise NotImplementedError(
            "Notifier {0} does not respond to notify!".format(type(self).__name__))

    def log(self, message):
        Logger.puts("{0}: {1}".format(self.me, message))

    def debug(self, message=None):
        if message is not None:
            message = "{0}: {1}".format(self.me, message)
        Logger.debug(message)
