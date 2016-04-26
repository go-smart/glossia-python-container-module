import os


class Region:
    """Rendering of CDM conceptual region.

    This contains information about a CDM database-defined region.
    If the `gosmart/goosefoot-mesher-base` container has been used,
    volumetric meshing will be automatically performed and objects
    with this class will know their mesh labels within the generated
    `MSH <http://gmsh.info>`_ file.

    """

    __regions_by_group = {}
    __regions_by_meshed_as = {}

    @classmethod
    def meshed_as(cls, meshed_as):
        """Find all regions that are meshed as, say, 'surface' or 'zone',
        that is, are (poss. internal) boundary or volumetric subdomains."""

        if meshed_as in cls.__regions_by_meshed_as:
            return cls.__regions_by_meshed_as[cls]
        return None

    @classmethod
    def zone(cls, idx):
        """Find all volumetric subdomains."""
        return cls.__regions_by_meshed_as["zone"][idx]

    @classmethod
    def surface(cls, idx):
        """Find all (internal and external) boundary subdomains."""
        return cls.__regions_by_meshed_as["surface"][idx]

    @classmethod
    def group(cls, group):
        """Find all regions within a (CDM-defined) named group (e.g. 'organs', 'tumours')."""
        if group in cls.__regions_by_group:
            return cls.__regions_by_group[group]
        return None

    @classmethod
    def add_region_to_group(cls, group, region):
        """(Mostly internal) add a region to a given group name."""
        if group not in cls.__regions_by_group:
            cls.__regions_by_group[group] = []
        cls.__regions_by_group[group].append(region)

    @classmethod
    def add_region_to_meshed_as(cls, meshed_as, region):
        """(Mostly internal) globally register a region as surface/zone."""
        if meshed_as not in cls.__regions_by_meshed_as:
            cls.__regions_by_meshed_as[meshed_as] = {}
        cls.__regions_by_meshed_as[meshed_as][region.idx] = region

    def am(self, group):
        """Check whether this region is in named CDM group."""
        return group in self.groups

    def __init__(self, key, region_dict):
        self.key = key
        self.idx = region_dict['id'] if 'id' in region_dict else None
        self.groups = region_dict['groups']

        if 'filename' in region_dict:
            self.filename = region_dict['filename']
        elif 'input' in region_dict:
            self.filename = os.path.join('input', region_dict['input'])
        else:
            self.filename = None

        for group in self.groups:
            self.add_region_to_group(group, self)

        if 'meshed_as' in region_dict:
            self.meshed_as = region_dict['meshed_as']
            if 'id' in region_dict:
                self.add_region_to_meshed_as(self.meshed_as, self)
        else:
            self.meshed_as = None
