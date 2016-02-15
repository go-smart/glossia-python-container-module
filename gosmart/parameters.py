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
import yaml
import os
from gosmart.dicts import AttributeDict, ParameterDict
from gosmart.region import Region
import gosmart.status


class GoSmartParameterLoader:
    def __init__(self, prefix):
        self._prefix = prefix
        self.initiated = False

    def get_parameters(self):
        if self.initiated is False:
            raise RuntimeError("Initiate first")

        return self.P, self.NP

    def get_regions(self):
        if self.initiated is False:
            raise RuntimeError("Initiate first")

        return self.R

    def get_region_dict(self):
        if self.initiated is False:
            raise RuntimeError("Initiate first")

        return self._region_dict

    def _load_parameters(self):
        with open(os.path.join(self._prefix, 'parameters.yml'), 'r') as f:
            self._parameter_dict = yaml.safe_load(f)

        with open(os.path.join(self._prefix, 'regions.yml'), 'r') as f:
            self._region_dict = yaml.safe_load(f)

        with open(os.path.join(self._prefix, 'needle_parameters.yml'), 'r') as f:
            self._needle_parameter_dicts = dict({v['index']: v['parameters'] for v in yaml.safe_load_all(f)})

    def initiate(self):
        self._load_parameters()
        self._initiate_region_dict()
        self._initiate_parameter_dict()
        self.initiated = True

    def _initiate_region_dict(self):
        R = AttributeDict({k: Region(v) for k, v in self._region_dict.items()})
        R.group = Region.group
        R.meshed_as = Region.meshed_as
        R.zone = Region.zone
        R.surface = Region.surface
        self.R = R

    def _initiate_parameter_dict(self):
        P = ParameterDict()
        P.update(self._parameter_dict)
        self.P = P
        self.NP = {k: ParameterDict(v) for k, v in self._needle_parameter_dicts.items()}


R = None
P = None
NP = None
update = None
update_available = None


def load():
    global R, P, NP, updatee, update_available

    loader = GoSmartParameterLoader('/shared/input')
    loader.initiate()

    R = loader.get_regions()
    P, NP = loader.get_parameters()

    update = gosmart.status.StatusUpdater()
    update_available = update.connect()

load()
