import os


class Region:
    __regions_by_group = {}
    __regions_by_meshed_as = {}

    @classmethod
    def meshed_as(cls, meshed_as):
        if meshed_as in cls.__regions_by_meshed_as:
            return cls.__regions_by_meshed_as[cls]
        return None

    @classmethod
    def zone(cls, idx):
        return cls.__regions_by_meshed_as["zone"][idx]

    @classmethod
    def surface(cls, idx):
        return cls.__regions_by_meshed_as["surface"][idx]

    @classmethod
    def group(cls, group):
        if group in cls.__regions_by_group:
            return cls.__regions_by_group[group]
        return None

    @classmethod
    def add_region_to_group(cls, group, region):
        if group not in cls.__regions_by_group:
            cls.__regions_by_group[group] = []
        cls.__regions_by_group[group].append(region)

    @classmethod
    def add_region_to_meshed_as(cls, meshed_as, region):
        if meshed_as not in cls.__regions_by_meshed_as:
            cls.__regions_by_meshed_as[meshed_as] = {}
        cls.__regions_by_meshed_as[meshed_as][region.idx] = region

    def am(self, group):
        return group in self.groups

    def __init__(self, region_dict):
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
