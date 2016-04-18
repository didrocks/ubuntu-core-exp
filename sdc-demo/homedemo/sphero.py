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

import kulka

sphero = None


class Sphero:

    default_sphero_color = (0, 0, 255)

    def __init__(self):
        self.sphero = kulka.Kulka("68:86:E7:07:C6:73")
        self.sphero.set_inactivity_timeout(3600)
        self.sphero.set_rgb(*self.default_sphero_color)

    def start_calibration(self):
        self.sphero.set_back_led(255)
        self.sphero.set_rgb(0, 0, 0)

    def recenter(self, angle):
        self.sphero.setheading(1)
        self.sphero.move(0, angle)
        self.sphero.setheading(0)

    def end_calibration(self):
        self.sphero.set_rgb(*default_sphero_color)
        self.sphero.set_back_led(0)

    def sleep(self):
        self.sphero.sleep()


def get_sphero():
    """Get sphero singleton"""
    global sphero
    if not sphero:
        sphero = Sphero()
    return sphero
