import gosmart
from gosmart.utils import convert_parameter


class AttributeDict(dict):
    def __getattr__(self, attr):
        return self.__getitem__(attr)


# Note that this class is not ready to replace dict entirely (that
# requires more method overriding than here)
class ParameterDict(AttributeDict):
    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def __getattr__(self, attr):
        return self.__getitem__(attr)

    def __getitem__(self, attr):
        if attr not in declared_parameters:
            raise KeyError(
                "You have asked for an undeclared parameter, "
                "[%s], "
                "please check your gosmart.setup(...) call." % attr
            )

        return super(ParameterDict, self).__getitem__(attr)

    def __setitem__(self, attr, value):
        param = convert_parameter(value[1], value[0])
        super(ParameterDict, self).__setitem__(attr, param)

    def update(self, *args, **kwargs):
        update_dict = dict(*args, **kwargs)
        super(ParameterDict, self).update({k: convert_parameter(v[1], v[0]) for k, v in update_dict.items()})


if gosmart._parameters is None:
    try:
        gosmart.setup('parameters.yml')
    except Exception as e:
        try:
            gosmart.setup('/shared/input/parameters.yml')
        except Exception as f:
            print(e)
            print(f)
            raise RuntimeError(
                "To load Go-Smart parameters from a non-default location"
                ", you should first run "
                "gosmart.setup(parameters), where parameters is a "
                "parameter definition YAML filename, a string list or "
                "a dict, with string keys."
            )

declared_parameters = gosmart._parameters
