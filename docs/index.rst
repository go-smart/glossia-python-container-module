.. Glossia Python Container Module documentation master file, created by
   sphinx-quickstart on Tue Mar 29 11:03:40 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Glossia Python Container Module's documentation!
===========================================================

Contents:

.. toctree::
   :maxdepth: 2

   documentation
   api/index

This module allows easy setup of a new Glossia simulation container image, wrapping a
previously unsupported piece of software. While Glossia is much more flexible, this
is an opinionated approach to accelerate the process for the end-user.

In particular, this module assumes it is running in a Glossia container and performs
several (non-destructive) checks `at import time`. In other circumstances,
this would not be desirable but for less familiar Python users, this reduces the
burden on end-user scripts, ensuring submodules imported immediately have transparent access
to parameter information.

Within the container script, one may simply enter:

::

    >>> from gosmart.parameters import P
    >>> P.CONSTANT_MAGIC_NUMBER
    3.0


where ``CONSTANT_MAGIC_NUMBER`` is a (float) parameter defined in for the numerical model.

Region information may be accessed by:

::

    >>> from gosmart.parameters import R
    >>> [r.idx for r in R.group("organ")]
    [1, 2, 3]

where these indices are mesh volumetric subdomain labels for any regions within the `organs`
group (if the auto-pre-meshing container base is used).

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

