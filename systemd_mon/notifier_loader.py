import importlib
import re


class NotifierLoader(object):
    """Resolves a notifier name (e.g. ``slack``) to its class by importing
    ``systemd_mon.notifiers.<name>`` and looking up the CamelCase class."""

    def get_class(self, name):
        class_name = self._camel_case(name)
        module = importlib.import_module("systemd_mon.notifiers." + name)
        return getattr(module, class_name)

    @staticmethod
    def _camel_case(name):
        if "_" not in name and re.match(r"[A-Z]+.*", name):
            return name
        return "".join(part.capitalize() for part in name.split("_"))
