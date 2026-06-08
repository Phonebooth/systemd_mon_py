from systemd_mon.state import State

IFACE_UNIT = "org.freedesktop.systemd1.Unit"
IFACE_SERVICE = "org.freedesktop.systemd1.Service"
IFACE_PROPS = "org.freedesktop.DBus.Properties"


class DBusUnit(object):
    """Wraps a single systemd unit DBus object, registers a signal listener,
    and pushes :class:`~systemd_mon.state.State` snapshots onto the queue."""

    def __init__(self, name, path, dbus_object):
        import dbus
        self.name = name
        self.path = path
        self._dbus_object = dbus_object
        self._props_iface = dbus.Interface(dbus_object, IFACE_PROPS)
        self.maybe_service_type = self._service_type()

    def register_listener(self, queue):
        queue.put((self, self._build_state()))

        def on_properties_changed(interface_name, changed, invalidated):
            if interface_name == IFACE_UNIT:
                queue.put((self, self._build_state()))

        self._dbus_object.connect_to_signal(
            "PropertiesChanged",
            on_properties_changed,
            dbus_interface=IFACE_PROPS,
        )

    def property(self, prop_name):
        return self._props_iface.Get(IFACE_UNIT, prop_name)

    def __str__(self):
        if self.maybe_service_type:
            return "{0} ({1})".format(self.name, self.maybe_service_type)
        return self.name

    def _build_state(self):
        return State(
            str(self.property("ActiveState")),
            str(self.property("SubState")),
            str(self.property("LoadState")),
            str(self.property("UnitFileState")),
            self.maybe_service_type,
        )

    def _service_type(self):
        import dbus
        try:
            return str(self._props_iface.Get(IFACE_SERVICE, "Type"))
        except dbus.exceptions.DBusException:
            return None
