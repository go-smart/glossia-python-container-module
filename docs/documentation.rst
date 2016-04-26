Documentation workflow
======================

To regenerate and upload a new documentation version:

.. code-block:: sh

    cd docs/
    make apidocs
    make html
    ghp-import -n _build/html
    git push origin gh-pages

This should become visible at https://go-smart.github.io/glossia-python-container-module.
