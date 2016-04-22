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

from time import sleep


def aircondition(sphero):
    print("Air condition simulate")

def garagedoor(sphero):
    logger.info("Open gare door")
    current_angle = 0
    num_steps = 40
    # make 2 loops
    rotate_by = 360*2 / num_steps
    for _ in range(num_steps+1):
        current_angle = (current_angle + rotate_by) % 360
        print(current_angle)
        _make_a_step(sphero, current_angle, 0, 0.3)

def switchlight(sphero):
    """simulate light switch on"""
    for i in range(255):
        sphero.set_rgb(i, i, i)
        sleep(0.005)
    sleep(3)
    sphero._reset_default_color()


def _make_a_step(sphero, current_angle, speed, step_time):
    sphero.roll(speed, current_angle)
    sleep(step_time)
    sphero.roll(0, current_angle)
