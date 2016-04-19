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

from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
import logging
import posixpath
import urllib
import os

logger = logging.getLogger(__name__)


class OurHttpRequestHandler(SimpleHTTPRequestHandler):

    def translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax.

        Stolen from SimpleHTTPSRequestHandler with a different base path

        Components that mean special things to the local file system
        (e.g. drive or directory names) are ignored.  (XXX They should
        probably be diagnosed.)

        """
        # abandon query parameters
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]
        # Don't forget explicit trailing slash when normalizing. Issue17324
        trailing_slash = path.rstrip().endswith('/')
        path = posixpath.normpath(urllib.unquote(path))
        words = path.split('/')
        words = filter(None, words)
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'www')
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir):
                continue
            path = os.path.join(path, word)
        if trailing_slash:
            path += '/'
        return path


def start_http_server():
    """Start the http server in a separate thread"""
    server_address = ('', 8001)

    OurHttpRequestHandler.protocol_version = "HTTP/1.1"
    httpd = HTTPServer(server_address, OurHttpRequestHandler)

    sa = httpd.socket.getsockname()
    logger.info("Serving static filesHTTP on {} port {}".format(sa[0], sa[1]))
    httpd.serve_forever()
