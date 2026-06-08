from __future__ import print_function

import os
import sys
import traceback

import yaml

from systemd_mon.errors import Error
from systemd_mon.logger import Logger
from systemd_mon.notifier_loader import NotifierLoader


def main():
    me = "systemd_mon"

    try:
        options = _load_and_validate(me)
        Logger.verbose = options.get("verbose", False)
        _start_monitor(options)

    except Error as e:
        err = e.message
        if Logger.verbose:
            if e.original:
                err += " - {0} ({1})".format(e.original, type(e.original).__name__)
                err += "\n\t" + "".join(traceback.format_tb(
                    e.original.__traceback__)).replace("\n", "\n\t")
            else:
                err += " ({0})".format(type(e).__name__)
                err += "\n\t" + "".join(traceback.format_tb(
                    e.__traceback__)).replace("\n", "\n\t")
        _fatal(me, err)

    except Exception as e:
        err = str(e)
        if Logger.verbose:
            err += " ({0})".format(type(e).__name__)
            err += "\n\t" + "".join(traceback.format_tb(
                e.__traceback__)).replace("\n", "\n\t")
        _fatal(me, err)


def _load_and_validate(me):
    if len(sys.argv) < 2:
        _fatal(me, "First argument must be a path to a YAML configuration file")
    path = sys.argv[1]
    if not os.path.exists(path):
        _fatal(me, "First argument must be a path to a YAML configuration file")

    with open(path) as fh:
        options = yaml.safe_load(fh)

    if not options or not options.get("notifiers") or not any(options["notifiers"]):
        _fatal(me, "no notifiers have been defined, there is no reason to continue")
    if not options.get("units") or not any(options["units"]):
        _fatal(me, "no units have been added for watching, there is no reason to continue")

    return options


def _start_monitor(options):
    from systemd_mon.dbus_manager import DBusManager
    from systemd_mon.monitor import Monitor

    monitor = Monitor(DBusManager())
    monitor.register_units(options["units"])

    loader = NotifierLoader()
    for name, notifier_options in options["notifiers"].items():
        klass = loader.get_class(name)
        monitor.add_notifier(klass(notifier_options or {}))

    monitor.start()


def _fatal(me, message, code=255):
    print(" {0} error: {1}".format(me, message), file=sys.stderr)
    sys.exit(code)
