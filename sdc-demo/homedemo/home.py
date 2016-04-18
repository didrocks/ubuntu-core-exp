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
from tools import suppress
import yaml

import events

logger = logging.getLogger(__name__)

class Home:
    def __init__(self):
        """Build the house

        room is a map indexed by name to the room objects composing the house
        start_room is where sphero is at startup"""
        self.rooms = {}
        self.start_room = None

        logger.debug("Build home map")
        with open("home.map", 'r') as f:
            home_map = yaml.load(f)

        self._populate_room_basic_infos(home_map)
        self._build_direct_paths()

    def _populate_room_basic_infos(self, home_map):
        """build room to room basic info"""
        for room_name in home_map:
            logger.debug("Processing {}".format(room_name))

            # set events if any
            event = None
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

    def _build_direct_paths(self):
        """Build direct room to room connection and reproducity"""
        for room_name in self.rooms:
            room = self.rooms[room_name]
            for connected_room_name in room._raw_paths:
                if not connected_room_name in self.rooms:
                    logger.error("{} is listed as connected to {}, but there is no such room declared. Please "
                                 "declare it".format(connected_room_name, room_name))
                    sys.exit(1)

                # direct path
                path = room._raw_paths[connected_room_name]
                room.paths[connected_room_name] = path

                # other direction
                print(path)
                temp_path = path[:]
                temp_path.reverse()
                path = []
                for seg in temp_path:
                    print(seg)
                    dist, angle = seg
                    path.append((dist, (angle+180)%360))
                self.rooms[connected_room_name].paths[room_name] = path

class Room:
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
