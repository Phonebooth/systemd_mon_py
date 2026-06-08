import atexit
import queue
import signal
import socket
import threading

from systemd_mon.callback_manager import CallbackManager
from systemd_mon.errors import MonitorError
from systemd_mon.logger import Logger
from systemd_mon.notification import Notification
from systemd_mon.notification_centre import NotificationCentre


class Monitor(object):
    """Wires units, notifiers, and DBus events together and drives the event loop.

    The GLib main loop (which delivers DBus signals) runs in the *main* thread
    so that dbus-python's signal dispatch works correctly.  A single daemon
    thread consumes the state queue and runs callbacks.
    """

    def __init__(self, dbus_manager):
        self.hostname = socket.gethostname()
        self._dbus_manager = dbus_manager
        self._units = []
        self._notification_centre = NotificationCentre()
        self._loop = None

    def add_notifier(self, notifier):
        self._notification_centre.add_notifier(notifier)
        return self

    def register_unit(self, unit_name):
        self._units.append(self._dbus_manager.fetch_unit(unit_name))
        return self

    def register_units(self, unit_names):
        for name in unit_names:
            self._units.append(self._dbus_manager.fetch_unit(name))
        return self

    def start(self):
        self._startup_check()

        self._loop = self._dbus_manager.runner()

        def _stop_and_exit(signum, frame):
            Logger.debug("Received signal {0}, shutting down.".format(signum))
            if self._loop and self._loop.is_running():
                self._loop.quit()

        signal.signal(signal.SIGTERM, _stop_and_exit)
        signal.signal(signal.SIGINT, _stop_and_exit)

        atexit.register(self._notification_centre.notify_stop, self.hostname)

        self._notification_centre.notify_start(self.hostname)

        Logger.puts("Monitoring changes to {0} units".format(len(self._units)))
        Logger.debug(lambda: " - " + "\n - ".join(u.name for u in self._units) + "\n")
        Logger.debug(lambda: "Using notifiers: {0}".format(
            ", ".join(type(n).__name__ for n in self._notification_centre)))

        state_q = queue.Queue()
        for unit in self._units:
            unit.register_listener(state_q)

        consumer = threading.Thread(
            target=self._run_callback_thread,
            args=(state_q,),
            name="callback-manager",
        )
        consumer.daemon = True
        consumer.start()

        self._loop.run()

    def _run_callback_thread(self, state_q):
        manager = CallbackManager(state_q)
        manager.start(self._unit_change_callback, None)

    def _unit_change_callback(self, unit_state):
        unit = unit_state
        Logger.puts("{0} {1}: {2} ({3})".format(
            unit.name,
            unit.state_change.status_text(),
            unit.state.active,
            unit.state.sub,
        ))
        Logger.debug(str(unit.state_change))
        Logger.puts()
        self._notification_centre.notify(Notification(self.hostname, unit))

    def _startup_check(self):
        if not self._units:
            raise MonitorError(
                "At least one systemd unit should be registered before monitoring can start")
        if not self._notification_centre.any():
            raise MonitorError(
                "At least one notifier should be registered before monitoring can start")
