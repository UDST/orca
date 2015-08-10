Orca
====

.. image:: https://pypip.in/version/orca/badge.svg
    :target: https://pypi.python.org/pypi/orca/
    :alt: PyPI Latest Version

.. image:: https://pypip.in/py_versions/orca/badge.svg
    :target: https://pypi.python.org/pypi/orca/
    :alt: Supported Python versions

.. image:: https://travis-ci.org/udst/orca.svg?branch=master
    :target: https://travis-ci.org/udst/orca
    :alt: Build Status

.. image:: https://coveralls.io/repos/udst/orca/badge.svg?branch=master
  :target: https://coveralls.io/r/udst/orca?branch=master
  :alt: Coverage

.. image:: https://pypip.in/wheel/orca/badge.svg
    :target: https://pypi.python.org/pypi/orca/
    :alt: Wheel Status

Orca is a pipeline orchestration tool that allows you to define dynamic data
sources and explicitly connect them to processing functions.
Orca has many features for working with `Pandas <http://pandas.pydata.org/>`__
data structures, but it can be used with anything.

Learn more in the official docs at https://udst.github.io/orca/.

Building the Orca UI JS Bundle
------------------------------

Orca ships with a bundle of JavaScript for the server UI.
If you've installed Orca from ``pip`` or ``conda`` you already have the
bundle, but if you're working on Orca you might need to build it manually:

* Make sure `nodejs <https://nodejs.org/>`__ is installed.
  (I use `Homebrew <http://brew.sh/>`__ on my Mac.)
* Install `gulp <http://gulpjs.com/>`__: ``npm install -g gulp``
* Change directories to ``orca/server/static``
* Run ``npm install`` to install dependencies
* Build the bundle: ``gulp js-build``, or
* Watch JS files to rebuild the bundle on changes: ``gulp js-watch``
