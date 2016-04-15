# -*- coding: utf-8 -*-
# Copyright (C) 2016 Canonical
#
# Authors:
#  Didier Roche
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; version 3.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

from gi.repository import GLib
import signal
import sys


class MainLoop(object):
    """Mainloop simple wrapper"""

    def __init__(self):
        self.mainloop = GLib.MainLoop()
        # Glib steals the SIGINT handler and so, causes issue in the callback
        # https://bugzilla.gnome.org/show_bug.cgi?id=622084
        signal.signal(signal.SIGINT, signal.SIG_DFL)

    def run(self):
        self.mainloop.run()

    def quit(self, status_code=0, raise_exception=True):
        GLib.timeout_add(80, self._clean_up, status_code)
        # only raises exception if not turned down (like in tests, where we are not in the mainloop for sure)
        if raise_exception:
            raise self.ReturnMainLoop()

    def _clean_up(self, exit_code):
        self.mainloop.quit()
        sys.exit(exit_code)

    @staticmethod
    def in_mainloop_thread(function):
        """Decorator to run a function in a mainloop thread"""

        # GLib.idle_add doesn't propagate try: except in the mainloop, so we handle it there for all functions
        def wrapper(*args, **kwargs):
            try:
                function(*args, **kwargs)
            except MainLoop.ReturnMainLoop:
                pass
            except BaseException:
                logger.exception("Unhandled exception")
                GLib.idle_add(MainLoop().quit, 1, False)

        def inner(*args, **kwargs):
            return GLib.idle_add(wrapper, *args, **kwargs)
        return inner

    class ReturnMainLoop(BaseException):
        """Exception raised only to return to MainLoop without finishing the function"""
