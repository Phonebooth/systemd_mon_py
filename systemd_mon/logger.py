from __future__ import print_function

import sys


class Logger(object):
    """Tiny stdout/stderr logger mirroring the Ruby ``SystemdMon::Logger``.

    ``verbose`` is a class-level flag. ``debug``/``debug_error`` accept either a
    message or a zero-arg callable (the Python equivalent of Ruby's block) so
    that expensive debug strings are only built when verbose is on.
    """

    verbose = False

    @classmethod
    def debug(cls, message=None, stream=None):
        if not cls.verbose:
            return
        if stream is None:
            stream = sys.stdout
        if callable(message):
            message = message()
        print(message if message is not None else "", file=stream)

    @classmethod
    def error(cls, message=None):
        print(message if message is not None else "", file=sys.stderr)

    @classmethod
    def debug_error(cls, message=None):
        cls.debug(message, sys.stderr)

    @classmethod
    def puts(cls, message=None):
        print(message if message is not None else "", file=sys.stdout)
