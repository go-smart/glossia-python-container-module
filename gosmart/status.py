from __future__ import print_function

# This file is part of the Go-Smart Simulation Architecture (GSSA).
# Go-Smart is an EU-FP7 project, funded by the European Commission.
#
# Copyright (C) 2013-  NUMA Engineering Ltd. (see AUTHORS file)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import socket
import os


class StatusUpdater:
    """Pass back /short/ information to the client."""

    def __init__(self, update_socket_location=None):
        if update_socket_location is None:
            if 'GSSA_STATUS_SOCKET' in os.environ:
                update_socket_location = os.environ['GSSA_STATUS_SOCKET']
            elif os.path.exists('/shared/update.sock'):
                update_socket_location = '/shared/update.sock'

        self._update_socket = None
        self._update_socket_location = update_socket_location

    def connect(self):
        """Attempts to connect to the known update socket.

        This should be the only egress from the container, other
        than implied communication through the filesystem.

        """
        if self._update_socket_location is None or not os.path.exists(self._update_socket_location):
            return False

        self._update_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._update_socket.connect(self._update_socket_location)

    def status(self, message, percentage=None):
        """Pass a status message to the Glossia server (and on to any
        client) with an optional percentage (float: 0-100)."""
        percentage_string = b''

        if percentage is not None:
            try:
                percentage = float(percentage)
            except ValueError:
                pass
            else:
                percentage_string = b'%lf|' % percentage

        message = b'%s%s' % (percentage_string, message)
        if self._update_socket is None:
            print(message)
        else:
            self._update_socket.sendall(message)
