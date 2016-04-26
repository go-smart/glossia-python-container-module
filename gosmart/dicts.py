import gosmart
from gosmart.utils import convert_parameter


class AttributeDict(dict):
    """Basic extension to dict allowing dot-access.

    Very helpful in keeping `Jinja2 <http://jinja.pocoo.org/>`_ files succinct.

    >>> A = AttributeDict({"name": "value"})
    >>> A.name
    value

    """
    def __getattr__(self, attr):
        return self.__getitem__(attr)


# Note that this class is not ready to replace dict entirely (that
# requires more method overriding than here)
class ParameterDict(AttributeDict):
    """Super-dict for Parameters.

    Extends :py:class:`~gosmart.dicts.AttributeDict` with additional
    Parameter-specific functionality. Allows things like (where
    `CONSTANT_MAGIC_NUMBER` is a float of value 3.0):

        >>> import gosmart
        >>> gosmart.setup(["CONSTANT_MAGIC_NUMBER"])
        >>> from gosmart.dicts import ParameterDict
        >>> paramdict = ParameterDict({
                "CONSTANT_MAGIC_NUMBER": ("float", "3")
                "CONSTANT_ELDRITCH_FIGURE": ("int", "3")
            })
        >>> paramdict["CONSTANT_MAGIC_NUMBER"]
        3.0
        >>> paramdict.CONSTANT_MAGIC_NUMBER + 1.0
        4.0
        >>> paramdict["CONSTANT_ELDRITCH_FIGURE"] + 1.0
        KeyError: You have asked for an undeclared parameter, [CONSTANT_ELDRITCH_FIGURE], please check your gosmart.setup(...) call.


    The class itself is primarily useful internally, but the most
    useful user-facing aspect is that you can check your declared parameters
    match the parameters you use in your code with the ``check_declared``
    option to :py:func:`gosmart.setup`. This should be a separate YAML
    file containing a list of expected parameters and will be used
    by the Go-Smart Clinical Domain Model to assign constraints to your
    numerical models (in the example, we pass a dict instead). If you
    use, in any parameter dictionary, a parameter not included in the
    master list an error will be thrown.

    At present, not all functionality of Goosefoot's ParameterDict is
    available, but when this is incorporated, it may be possible to
    access the original string and typestring from the returned value.
    However, this would require subclassing common types. If end-users
    consistently duck-type (i.e. no isinstances) this may be of benefit
    to them, but only as an optional parameter to :py:func:`gosmart.setup`.

    In the future, this YAML file may be replaced or supplemented
    by AST inspection within the Go-Smart CDM.

    Note that not all dictionary functionality is yet overridden.

    .. inheritance-diagram:: gosmart.dicts.ParameterDict

    """

    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def __getattr__(self, attr):
        return self.__getitem__(attr)

    def __getitem__(self, attr):
        if declared_parameters is not None and attr not in declared_parameters:
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
            print(
                "To load Go-Smart parameters from a non-default location"
                ", you should first run "
                "gosmart.setup(parameters), where parameters is a "
                "parameter definition YAML filename, a string list or "
                "a dict, with string keys."
            )

if gosmart._check_declared:
    declared_parameters = gosmart._parameters
else:
    declared_parameters = None
