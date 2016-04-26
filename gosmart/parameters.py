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
import gosmart
import gosmart.dicts 
import gosmart.region 
import gosmart.status


class GoSmartParameterLoader:
    """Turn stored parameters (inc. regions) into usable Python objects."""

    def __init__(self, prefix):
        self._prefix = prefix
        self.initiated = False
        self._parameter_dict = None
        self._needle_parameter_dicts = {}
        self._region_dict = {}

    def get_parameters(self):
        """Return both global parameters and a dictionary of needle parameter
        dictionaries (tuple)."""
        if self.initiated is False:
            raise RuntimeError("Initiate first")

        return self.P, self.NP

    def get_regions(self):
        """Return the global region class."""
        if self.initiated is False:
            raise RuntimeError("Initiate first")

        return self.R

    def get_region_dict(self):
        """Return the region dict (mostly internal)."""
        if self.initiated is False:
            raise RuntimeError("Initiate first")

        return self._region_dict

    def _load_parameters(self):
        if gosmart._parameters is not False:
            with open(os.path.join(self._prefix, 'parameters.yml'), 'r') as f:
                self._parameter_dict = yaml.safe_load(f)

            with open(os.path.join(self._prefix, 'needle_parameters.yml'), 'r') as f:
                self._needle_parameter_dicts = dict({v['index']: v['parameters'] for v in yaml.safe_load_all(f)})

            with open(os.path.join(self._prefix, 'regions.yml'), 'r') as f:
                self._region_dict = yaml.safe_load(f)

    def initiate(self):
        """Load and process regions and parameters."""
        self._load_parameters()
        self._initiate_region_dict()
        self._initiate_parameter_dict()
        self.initiated = True

    def _initiate_region_dict(self):
        R = gosmart.dicts.AttributeDict({k: gosmart.region.Region(k, v) for k, v in self._region_dict.items()})
        R.group = gosmart.region.Region.group
        R.meshed_as = gosmart.region.Region.meshed_as
        R.zone = gosmart.region.Region.zone
        R.surface = gosmart.region.Region.surface
        self.R = R

    def _initiate_parameter_dict(self):
        P = gosmart.dicts.ParameterDict()
        if self._parameter_dict:
            P.update(self._parameter_dict)
        self.P = P
        self.NP = {k: gosmart.dicts.ParameterDict(v) for k, v in self._needle_parameter_dicts.items()}


R = None
P = None
NP = None
update = None
update_available = None
region_dict = None


def load():
    """Set up the objects that end-users may wish to use from this
    module directly - especially, R, P and NP."""

    global R, P, NP, update, update_available, region_dict

    loader = GoSmartParameterLoader(gosmart._prefix)
    loader.initiate()

    R = loader.get_regions()
    P, NP = loader.get_parameters()

    region_dict = loader.get_region_dict()

    update = gosmart.status.StatusUpdater()
    update_available = update.connect()


try:
    load()
except OSError as e:
    print("Could not load the parameters", e)
