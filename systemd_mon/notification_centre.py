import threading
import traceback

from systemd_mon.errors import NotifierError
from systemd_mon.logger import Logger


class NotificationCentre(object):
    """Holds the registered notifiers and fans messages out to each in its own
    thread, joining them all before returning (mirrors the Ruby version)."""

    def __init__(self):
        self.notifiers = []

    def classes(self):
        return [type(n) for n in self.notifiers]

    def __iter__(self):
        return iter(self.notifiers)

    def any(self):
        return bool(self.notifiers)

    def add_notifier(self, notifier):
        if not hasattr(notifier, "notify"):
            raise NotifierError(
                "Notifier {0} must respond to 'notify'".format(type(notifier).__name__))
        self.notifiers.append(notifier)
        return self

    def notify_start(self, hostname):
        def run(notifier):
            if hasattr(notifier, "notify_start"):
                Logger.puts("Notifying SystemdMon start via {0}".format(type(notifier).__name__))
                notifier.notify_start(hostname)
            else:
                Logger.debug(lambda: "{0} doesn't respond to 'notify_start', not sending notification".format(type(notifier).__name__))
        self._each_notifier(run)

    def notify_stop(self, hostname):
        def run(notifier):
            if hasattr(notifier, "notify_stop"):
                Logger.puts("Notifying SystemdMon stop via {0}".format(type(notifier).__name__))
                notifier.notify_stop(hostname)
            else:
                Logger.debug(lambda: "{0} doesn't respond to 'notify_stop', not sending notification".format(type(notifier).__name__))
        self._each_notifier(run)

    def notify(self, notification):
        def run(notifier):
            Logger.puts("Notifying state change of {0} via {1}".format(
                notification.unit.name, type(notifier).__name__))
            notifier.notify(notification)
        self._each_notifier(run)

    def _each_notifier(self, func):
        threads = []
        for notifier in self.notifiers:
            t = threading.Thread(target=self._guarded, args=(func, notifier))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()

    @staticmethod
    def _guarded(func, notifier):
        try:
            func(notifier)
        except Exception as e:
            Logger.error("Failed to send notification via {0}:\n".format(type(notifier).__name__))
            Logger.error("  {0}: {1}\n".format(type(e).__name__, e))
            Logger.debug_error(lambda: "\n\t" + traceback.format_exc() + "\n")
