import traceback

from systemd_mon.logger import Logger
from systemd_mon.unit_with_state import UnitWithState


class CallbackManager(object):
    """Consumes ``(unit, state)`` items off the queue and drives callbacks.

    For each incoming state it appends to that unit's :class:`UnitWithState`,
    runs the per-state callback, then runs the change callback and resets the
    accumulated history once the change is deemed "important".
    """

    def __init__(self, queue):
        self.queue = queue
        self.states = {}

    def _unit_state(self, unit):
        if unit not in self.states:
            self.states[unit] = UnitWithState(unit)
        return self.states[unit]

    def start(self, change_callback, each_state_change_callback):
        while True:
            unit, state = self.queue.get()
            Logger.debug(lambda: "{0} new state: {1}".format(unit, state))
            unit_state = self._unit_state(unit)
            unit_state.append(state)

            if each_state_change_callback:
                self._with_error_handling(each_state_change_callback, unit_state)

            if change_callback and unit_state.state_change.important():
                self._with_error_handling(change_callback, unit_state)

            if unit_state.state_change.important():
                unit_state.reset()

    def _with_error_handling(self, callback, *args):
        try:
            callback(*args)
        except Exception as e:
            Logger.error("Uncaught exception ({0}) in callback: {1}".format(
                type(e).__name__, e))
            Logger.debug_error(lambda: "\n\t" + traceback.format_exc() + "\n")
