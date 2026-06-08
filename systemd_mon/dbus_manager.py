from systemd_mon.errors import SystemdError, UnknownUnitError
from systemd_mon.dbus_unit import DBusUnit

# dbus and GLib imports deferred here so that unit tests can import the rest of
# the package without a system DBus installation present.
import dbus
import dbus.exceptions
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

# Must be set before any SystemBus connection is made so that signals are
# delivered via the GLib main loop.
DBusGMainLoop(set_as_default=True)

SYSTEMD_BUS_NAME = "org.freedesktop.systemd1"
SYSTEMD_OBJ_PATH = "/org/freedesktop/systemd1"
SYSTEMD_MANAGER_IFACE = "org.freedesktop.systemd1.Manager"


class DBusManager(object):
    """Connects to systemd on the system DBus and subscribes to unit events."""

    def __init__(self):
        self._bus = dbus.SystemBus()
        obj = self._bus.get_object(SYSTEMD_BUS_NAME, SYSTEMD_OBJ_PATH)
        self._manager = dbus.Interface(obj, SYSTEMD_MANAGER_IFACE)
        try:
            self._manager.Subscribe()
        except dbus.exceptions.DBusException as e:
            raise SystemdError(
                "Systemd is not installed, or is an incompatible version. "
                "It must provide the Subscribe dbus method: "
                "version 204 is the minimum recommended version.", e)

    def fetch_unit(self, unit_name):
        try:
            path = self._manager.GetUnit(unit_name)
        except dbus.exceptions.DBusException as e:
            raise UnknownUnitError(
                "Unknown or unloaded systemd unit '{0}'".format(unit_name), e)
        obj = self._bus.get_object(SYSTEMD_BUS_NAME, path)
        return DBusUnit(unit_name, path, obj)

    def runner(self):
        return GLib.MainLoop()
