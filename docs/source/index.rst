.. urbansim documentation master file, created by
   sphinx-quickstart on Thu May 22 12:13:43 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Orca
====

Introduction
------------

Orca is a pipeline orchestration framework that allows you to define dynamic
data sources and explicitly connect them to processing functions. Orca has many
features for working with Pandas_ data
structures, but it can be used with any data.
Orca was originally designed to orchestrate UrbanSim_ simulations and so
has capabilities for running a pipeline multiple times while iterating
over a set of input data.

Goals
~~~~~

Orca has explit goals of flexibility, transparency, lazy execution,
and encouraging good practices. Those goals are achieved by:

* Flexibility

  * Users may write and run any Python

* Transparency

  * Dependencies between data and processing units are explicitly listed
  * Your code is a record of everything that happens

* Lazy execution

  * Orca only calls functions if they are explicitly needed

* Good practices

  * Encourage small, functional units
  * Encourage code re-use

Components
~~~~~~~~~~

The units of Orca pipelines are Python functions registered with Orca
via decorators.
Orca calls these functions by matching their arguments to other registered
data.
(This format is heavily inspired by
`pytest's fixtures <http://pytest.org/latest/fixture.html#fixture>`__.)
The main components of a pipeline include:

* Steps

  * Steps are Python functions registered with Orca whose main utility
    is via their side-effects.
    Some steps will update the pipeline data somehow, maybe by updating
    a column in a table or adding rows to a table; other steps might
    generate plots or save processed data.

* Tables

  * Orca has a built-in understanding of Pandas DataFrames_,
    which are referred to as "tables".
    Tables can be registered as plain DataFrames or as
    functions that return DataFrames.

* Columns

  * Columns can be dynamically added to tables by registering
    individual pandas Series_ instances or by registering functions
    that return Series.

* Injectables

  * Functions may need to make use of data that are not in a table/column.
    For these you can register any object or any function as an "injectable"
    to make it available throughout an Orca pipeline.

Orca offers some conveniences for streamlining the construction of pipelines:

* Argument matching

  * When a registered function needs to be evaluated, Orca inspects
    the function's argument names and keyword argument values. Orca
    matches those arguments to registered variables, such as tables,
    columns, or injectables, and calls the function with those arguments
    (in turn calling any other functions as necessary and injecting
    other arguments).

* Functions as data

  * If something needs to be recomputed on-demand you can register
    a function that returns your table/column/injectable. That function
    will be evaluated anytime the variable is used in the pipeline so
    that the value is always current.

* Caching

  * Have some data that needs to be computed, but not very frequently?
    You can enable caching on individual items to save time, then later clear
    the cache on just that item or clear the entire cache in one call.
    You can also set limited scopes on caching so that items are removed
    from the cache at set intervals.

* Automated Merges

  * Orca can merge multiple tables to some target table once you have
    described relationships between them.

* Data archives

  * After running a pipeline it can be useful to look at how the data changed
    as it progressed. Orca can save registered tables out
    to an HDF5 file during every iteration or at set intervals.

Installation
------------

Orca requires Pandas, PyTables, and PyToolz, which will be installed automatically if they are not already present in your Python environment.


You can install Orca with pip::

    pip install orca

Or with conda::

    conda install orca --channel conda-forge


Links
-----

* `GitHub <https://github.com/udst/orca>`__
* `PyPi <https://pypi.python.org/pypi/orca>`__

Contents
--------

.. toctree::
   :maxdepth: 2

   example
   core
   utils

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _Pandas: http://pandas.pydata.org/
.. _UrbanSim: http://udst.github.io/urbansim/
.. _DataFrame: http://pandas.pydata.org/pandas-docs/stable/dsintro.html#dataframe
.. _DataFrames: http://pandas.pydata.org/pandas-docs/stable/dsintro.html#dataframe
.. _Series: http://pandas.pydata.org/pandas-docs/stable/dsintro.html#series
