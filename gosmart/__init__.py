import yaml
import os

_parameters = None
_parameter_info = None
_prefix = 'input'
_check_declared = False


try:
    basestring
except:
    basestring = (str, bytes)


class GlossiaParameterLoadingError(RuntimeError):
    pass


def setup(parameters=True, prefix=None, check_declared=False):
    """Configure the Glossia Python Container Module (gosmart).

    Strictly, this is optional, as it will be called when the
    end-user wishes to use a parameter, but if the Glossia
    container parameter definition files are not found it will
    raise RuntimeErrors.

    Args:
        parameters (dict|str|True|False|None): this may either be a
            parameter dictionary or a string filename naming
            a parameter YAML file. If no parameters are to be
            loaded, False should be passed (this disables
            searching in gosmart.parameters).
            The None option is primarily for testing, to indicate
            parameters should not be loaded, but the processes
            should otherwise continue as normal. True indicates
            that standard locations should be tested.
        prefix (str): location of parameter files relative to
            the simulation working directory. Defaults to
            ``gosmart._prefix``.
        check_declared (bool): raise a warning if parameters are
            subsequently requested that haven't been declared in
            ``parameters``, even if they exist in the database-sourced
            parameter files.

    Raises:
        GlossiaParameterLoadingError: if parameters are requested but not found
            in the filesystem.

    """
    global _parameters, _parameter_info, _prefix, _check_declared

    _check_declared = check_declared

    if parameters is False:
        _parameters = False
        return

    if parameters is True:
        possible_locations = (
            os.path.join('/shared', 'output', 'run', 'parameters.yml'),
            os.path.join('/shared', 'output', 'parameters.yml'),
            os.path.join('/shared', 'input', 'parameters.yml'),
        )
        for location in possible_locations:
            try:
                setup(location, prefix, check_declared)
            except GlossiaParameterLoadingError:
                continue
            else:
                return

    if prefix is not None:
        _prefix = prefix

    if isinstance(parameters, basestring):
        try:
            with open(parameters, 'r') as f:
                _parameter_info = yaml.safe_load(f)
                _parameters = _parameter_info.keys()
        except Exception as e:
            raise GlossiaParameterLoadingError(
                "Go-Smart setup argument appears to be a string\n"
                "(%s)\nbut we cannot read parameters from it: %s" % (parameters, repr(e))
            )
    else:
        try:
            _parameters = parameters.keys()
            _parameter_info = parameters
        except:
            try:
                _parameters = [k for k in parameters]
                _parameter_info = {k: {} for k in parameters}
            except Exception as e:
                raise GlossiaParameterLoadingError(
                    "Go-Smart could not understand your parameter "
                    "format for setup. Please use a filename, dict "
                    "or iterable over strings: %s" % repr(e)
                )
