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

import logging
import os
import sys
from tools import suppress, Singleton
import yaml

_home = None
logger = logging.getLogger(__name__)


class Home(object):
    """The home owner of all rooms and directions of a house"""
    __metaclass__ = Singleton

    def __init__(self):
        """Build the house

        room is a map indexed by name to the room objects composing the house
        start_room is where sphero is at startup"""
        self.rooms = {}
        self.start_room = None
        self.facedetectdest_room = None

        logger.debug("Build home map")
        with open("home.map", 'r') as f:
            home_map = yaml.load(f)

        self._populate_room_basic_infos(home_map)
        self._build_direct_paths()
        self._build_other_paths()

    def _populate_room_basic_infos(self, home_map):
        """build room to room basic info"""
        import events
        for room_name in home_map:
            logger.debug("Processing {}".format(room_name))

            # set events if any
            event = lambda sphero: None
            with suppress(KeyError):
                try:
                    event_name = home_map[room_name]["event"]
                    event = getattr(events, event_name)
                except AttributeError as e:
                    logger.error("{} listed in {} isn't a valid event".format(event_name, room_name))
                    sys.exit(1)

            # set if sphero can stay in this room or not
            stay = home_map[room_name].get("stay", False)

            # fetch the raw path data, transforming list of string in tuples
            raw_paths = {}
            for connected_room in home_map[room_name].get("paths", {}):
                raw_paths[connected_room] = []
                for path in home_map[room_name]["paths"][connected_room]:
                    dist, angle = path.split(",")
                    dist = int(dist)
                    angle = int(angle)
                    raw_paths[connected_room].append((dist, angle))

            room = Room(room_name, event, stay, raw_paths)
            self.rooms[room_name] = room

            # set if home rest position
            with suppress(KeyError):
                if home_map[room_name]["start"]:
                    if self.start_room:
                        logger.error("{} is defined as starting position but {} is already one. Please only define one."
                                     "".format(room_name, self.start_room.name))
                        sys.exit(1)
                    self.start_room = room

            # set if home face detection position
            with suppress(KeyError):
                if home_map[room_name]["facedetectiondest"]:
                    if self.facedetectdest_room:
                        logger.error("{} is defined as a face detect position but {} is already one. Please only define"
                                     " one.".format(room_name, self.facedetectdest_room.name))
                        sys.exit(1)
                    self.facedetectdest_room = room

        if not self.facedetectdest_room or not self.start_room:
            logger.error("We need at least having one facedetectiondest and a start room in the home map.")
            sys.exit(1)

    def _build_direct_paths(self):
        """Build direct room to room connection and reproducity"""
        for room_name in self.rooms:
            logger.debug("Build direct connections for {}".format(room_name))
            room = self.rooms[room_name]
            for connected_room_name in room._raw_paths:
                if connected_room_name not in self.rooms:
                    logger.error("{} is listed as connected to {}, but there is no such room declared. Please "
                                 "declare it".format(connected_room_name, room_name))
                    sys.exit(1)

                # direct path
                path = room._raw_paths[connected_room_name]
                room.paths[connected_room_name] = path

                # other direction
                temp_path = path[:]
                temp_path.reverse()
                path = []
                for seg in temp_path:
                    dist, angle = seg
                    path.append((dist, (angle + 180) % 360))
                self.rooms[connected_room_name].paths[room_name] = path

    def _build_other_paths(self):
        """Build all possible paths between all rooms"""
        for room_name in self.rooms:
            logger.debug("Build other paths for {}".format(room_name))
            room = self.rooms[room_name]
            self._add_connected_room(room, room)

    def _add_connected_room(self, room, current_room):
        """Add connected room to current room as a path to room"""
        for next_room_name in current_room.paths.copy():
            if room.name == next_room_name:
                continue
            next_room = self.rooms[next_room_name]

            # if already existing, only add it if shorter
            new_path = room.paths.get(current_room.name, []) + current_room.paths[next_room_name]
            with suppress(KeyError):
                if len(new_path) > len(room.paths[next_room_name]):
                    continue

            logger.debug("Adding {} new path".format(next_room_name))
            room.paths[next_room_name] = new_path
            self._add_connected_room(room, next_room)


class Room(object):
    """A room in the house"""

    def __init__(self, name, event, stay, raw_paths):
        """Build a room with positional parameter

        name is the name of the room
        event is the function to execute when sphero entered the room
        stay defines if sphero should go back to previous room after executing the action
        raw_paths is the uncomputed path data"""
        self.name = name
        self.event = event
        self.stay = stay
        self._raw_paths = raw_paths

        # path is the computed real path
        self.paths = {}
