from systemd_mon.state import State

IFACE_UNIT = "org.freedesktop.systemd1.Unit"
IFACE_SERVICE = "org.freedesktop.systemd1.Service"
IFACE_PROPS = "org.freedesktop.DBus.Properties"


class DBusUnit(object):
    """Wraps a single systemd unit DBus object, registers a signal listener,
    and pushes :class:`~systemd_mon.state.State` snapshots onto the queue."""

    def __init__(self, name, path, dbus_object):
        self.name = name
        self.path = path
        self._dbus_object = dbus_object
        self._dbus_object.IntrospectionInterface.Introspect()
        self._props = dbus_object.GetAll
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
        import dbus
        obj = self._dbus_object
        props_iface = dbus.Interface(obj, IFACE_PROPS)
        return props_iface.Get(IFACE_UNIT, prop_name)

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
            iface = dbus.Interface(self._dbus_object, IFACE_PROPS)
            return str(iface.Get(IFACE_SERVICE, "Type"))
        except dbus.exceptions.DBusException:
            return None
