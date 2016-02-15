import json


def convert_parameter(parameter, typ=None, try_json=True):
    # Why do we distinguish between numeric classes in Python?!
    # Because we do not want to introduce rounding errors where
    # none are expected by switching a counter to float. Also,
    # some Python functions, like range, require an int.

    if parameter == "null" or parameter is None:
        return None

    if typ == "float":
        cast = float
    elif typ == "integer":
        cast = int
    elif typ == "boolean":
        cast = lambda s: (s.lower() != "false" and bool(s))
    elif typ == "string":
        cast = str
    else:
        cast = None

    if cast is not None:
        try:
            return cast(parameter)
        except ValueError:
            print("UNCASTABLE", parameter, cast)
            pass

    if try_json:
        try:
            return json.loads(parameter)
        except:
            pass

    return parameter
