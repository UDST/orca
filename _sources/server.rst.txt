Orca Server
===========

*THE ORCA SERVER MODULE IS DEPRECATED AND WILL BE REMOVED IN A FUTURE RELEASE.*

Orca ships with a `Flask <http://flask.pocoo.org/>`__ server that can
provide data about and from an Orca configuration.
You can use it as a zero-configuration server for your data use the
bundled UI to browse an Orca configuration.

Requirements
------------

The Orca server requires three additional libraries:

* `Flask <http://flask.pocoo.org/>`__ >= 0.10
* `Pygments <http://pygments.org/>`__ >= 2.0
* `Six <http://pythonhosted.org/six/>`__ >= 1.9

You can get these libraries individually (they are available via
`pip <https://pip.pypa.io/en/stable/>`__ and
`conda <http://conda.pydata.org/>`__), or get them when you install
Orca by including the ``[server]`` option::

    pip install orca[server]

Building the Orca UI JS Bundle
------------------------------

This is NOT NECESSARY if you've installed Orca from ``pip`` or ``conda``, but these instructions may help if you're working directly with the Orca source code.

* Make sure `nodejs <https://nodejs.org/>`__ is installed.
  (`Homebrew <http://brew.sh/>`__ is a nice way to do this on Mac.)
* Install `gulp <http://gulpjs.com/>`__: ``npm install -g gulp``
* Change directories to ``orca/server/static``
* Run ``npm install`` to install dependencies
* Build the bundle: ``gulp js-build``, or
* Watch JS files to rebuild the bundle on changes: ``gulp js-watch``

Start the Server
----------------

Use the ``orca-server`` command line utility to start the Orca server::

    > orca-server --help
    usage: orca-server [-h] [-d] [-H HOST] [-p PORT] filename

    Start a Flask server that has HTTP endpoints that provide data about an Orca
    configuration and data registered with Orca.

    positional arguments:
      filename              File with Orca config

    optional arguments:
      -h, --help            show this help message and exit
      -d, --debug           Enable Flask's debug mode
      -H HOST, --host HOST  Hostname on which to run the server
      -p PORT, --port PORT  Port on which to run server

The ``filename`` argument is the name of a Python file that will be imported
by the server in order to populate Orca.
Refer to the documentation of Flask's
`run method <http://flask.pocoo.org/docs/0.10/api/#flask.Flask.run>`__
to learn more about the debug, host, and port options.

Server Routes
-------------

This section details the routes available from the Orca server.
Most of the routes return JSON, but some return text as noted in
the descriptions.

.. contents::
   :local:

UI
~~

* Route: ``/ui``
* Returns: HTML

The ``/ui`` route is meant for use with browsers and allows the user to
browse their Orca configuration.
Users can see lists of registered items, data previews, summary statistics,
and the source code definitions of functions registered with Orca.

.. note::

   Using the Orca browser requires an internet connection so the application
   can load some third-party CSS and JavaScript.

Schema
~~~~~~

* Route: ``/schema``
* Returns: JSON

The "schema" route returns a complete list of available tables, columns, steps,
injectables, and broadcasts.
Columns include both those registered on a table via Orca and those that
are local to a table.
The returned JSON object has keys ``tables``, ``steps``, ``injectables``,
``columns``, and ``broadcasts``.
The ``tables``, ``steps`` and ``injectables`` values are arrays of strings.
The ``injectables`` value is an array of two-value arrays with the names
of the "cast" and "onto" tables, respectively.
The ``columns`` value is an object whose keys are table names and values
are arrays of strings (column names).

Example:

.. code-block:: json

    {
      "tables": ["my_table", "another_table"],
      "columns": {
        "my_table": ["col1", "col2", "col3"],
        "another_table": ["data1", "data2"]
      },
      "injectables": ["val1", "val2"],
      "steps": ["process_data"],
      "broadcasts": [["my_table", "another_table"]]
    }

List Tables
~~~~~~~~~~~

* Route: ``/tables``
* Returns: JSON

The "tables" route returns a list of the tables registered with Orca.

.. code-block:: json

    {
      "tables": ["my_table", "another_table"]
    }

Table Info
~~~~~~~~~~

* Route: ``/tables/<table_name>/info``
* Returns: Text

Returns the text result of ``table.info(verbose=True)``::

    <class 'pandas.core.frame.DataFrame'>
    Int64Index: 2478 entries, 0 to 2477
    Data columns (total 10 columns):
    region          2478 non-null object
    subregion       2478 non-null object
    station         2478 non-null object
    abbreviation    2478 non-null object
    elevation       2478 non-null int64
    month           2478 non-null object
    precip          1869 non-null float64
    avg precip      2466 non-null float64
    pct of avg      1953 non-null float64
    year            2478 non-null int64
    dtypes: float64(3), int64(2), object(5)
    memory usage: 213.0+ KB

Table Preview
~~~~~~~~~~~~~

* Route: ``/tables/<table_name>/preview``
* Returns: JSON

Returns the result of ``table.head()`` as JSON in Pandas' "split" format.

.. code-block:: json

    {
      "columns": ["col1", "col2"],
      "data": [
        ["datum1", 19],
        ["datum2", 42],
        ["datum3", 99]
      ],
      "index": [12, 26, 40]
    }

Table Describe
~~~~~~~~~~~~~~

* Route: ``/tables/<table_name>/describe``
* Returns: JSON

Returns the result of ``table.describe()`` as JSON in Pandas' "split" format.

.. code-block:: json

    {
      "columns": [
        "elevation",
        "precip",
      ],
      "data": [
        [
          177.0,
          98.0
        ],
        [
          2782.581920904,
          15.3412244898
        ],
        [
          2540.805957787,
          11.8787421898
        ],
        [
          -194.0,
          1.49
        ],
        [
          384.0,
          5.6075
        ],
        [
          2400.0,
          12.465
        ],
        [
          4641.0,
          20.4625
        ],
        [
          9645.0,
          60.91,
        ],
      ],
      "index": [
        "count",
        "mean",
        "std",
        "min",
        "25%",
        "50%",
        "75%",
        "max"
      ]
    }

Table Definition
~~~~~~~~~~~~~~~~

* Route: ``/tables/<table_name>/definition``
* Returns: JSON

Get information about how a table is registered with Orca, for example whether
it is a registered DataFrame or function.
If the table is a registered function this returns the text of the function.

If the table is a registered DataFrame all that is returned is:

.. code-block:: json

    {"type": "dataframe"}

If the table is registered as a function the returned data will include the
filename, line number, and text of the function:

.. code-block:: json

    {
      "type": "function",
      "filename": "data.py",
      "lineno": 42,
      "text": "function text",
      "html": "function text as html"
    }

The HTML has been marked up by `Pygments <http://pygments.org/>`__ with the
``.highlight`` class.

Table CSV
~~~~~~~~~

* Route: ``/tables/<table_name>/csv``
* Returns: Text

Returns the entire table as CSV using Pandas' default CSV output.

::

    ,col1,col2
    12,datum1,19
    26,datum2,42
    40,datum3,99

Table Groupby Aggregation
~~~~~~~~~~~~~~~~~~~~~~~~~

* Route: ``/tables/<table_name>/groupbyagg``
* Returns: JSON

The groupby-agg API allows clients to perform a groupby on a table, then
an aggregation on a single column and get the resulti as JSON
in Pandas' "split" format.

The parameters of the groupby-agg are specified as URL parameters:

* `column` - Column to aggregate
* `agg` - Aggregation to perform. Supported values are `mean`, `median`,
  `std`, `sum`, and `size`.
* `by` (optional) - Column on which to group table
* `level` (optional) - Index level on which to group table

One of `by` or `level` must be provided, but not both.
For example, the URL might read::

    /groupbyagg?by=region&column=precip&agg=median

The data is returned as JSON in Pandas' "split" format:

.. code-block:: json

    {
      "data": [10.225, 2.15],
      "index": ["CENTRAL COAST", "COLORADO RIVER"],
      "name": "precip"
    }

List Columns For Table
~~~~~~~~~~~~~~~~~~~~~~

* Route: ``/tables/<table_name>/columns``
* Returns: JSON

List all columns for a table including both local and registered columns.

.. code-block:: json

    {
      "columns": ["col1", "col2"]
    }

Column Preview
~~~~~~~~~~~~~~

* Route: ``/tables/<table_name>/columns/<column_name>/preview``
* Returns: JSON

Return the first ten elements of a column as JSON in Pandas' "split" format:

.. code-block:: json

    {
      "data": [60.92, 12.63, 12.06, 12.11, 26.08],
      "index": [12, 26, 40, 54, 68],
      "name": "precip"
    }

Column Definition
~~~~~~~~~~~~~~~~~

* Route: ``/tables/<table_name>/columns/<column_name>/definition``
* Returns: JSON

Get information about how a column is registered with Orca, for example whether
it is a registered Series or function.
If the column is a registered function this returns the text of the function.

If the column is a registered Series all that is returned is:

.. code-block:: json

    {"type": "series"}

or if the column is local to a DataFrame the return value is:

.. code-block:: json

    {"type": "local"}

If the column is registered as a function the returned data will include the
filename, line number, and text of the function:

.. code-block:: json

    {
      "type": "function",
      "filename": "data.py",
      "lineno": 42,
      "text": "function text",
      "html": "function text as html"
    }

The HTML has been marked up by `Pygments <http://pygments.org/>`__ with the
``.highlight`` class.

Column Describe
~~~~~~~~~~~~~~~

* Route: ``/tables/<table_name>/columns/<column_name>/describe``
* Returns: JSON

Return summary statistics for a column as JSON in Pandas' "split" format:

.. code-block:: json

    {
      "data": [
        1771.0,
        1.3995482778,
        2.508358979,
        0.0,
        0.07,
        0.57,
        1.445,
        21.34
      ],
      "index": [
        "count",
        "mean",
        "std",
        "min",
        "25%",
        "50%",
        "75%",
        "max"
      ],
      "name": "precip"
    }

Column CSV
~~~~~~~~~~

* Route: ``/tables/<table_name>/columns/<column_name>/csv``
* Returns: Text

Return an entire column as CSV using Pandas' default output::

    0,0.04
    1,5.02
    2,2.35
    3,3.72
    4,19.48

List Injectables
~~~~~~~~~~~~~~~~

* Route: ``/injectables``
* Returns: JSON

Returns a list of all registered injectables:

.. code-block:: json

    {
      "injectables": ["var1", "var2"]
    }

Injectable Repr
~~~~~~~~~~~~~~~

* Route: ``/injectables/<injectable_name>/repr``
* Returns: JSON

Return the string representations of an injectable and the type of an
injectable:

.. code-block:: json

    {
      "repr": "2014",
      "type": "<class 'int'>"
    }

This will attempt to return the entire string representation of a value.
Use care with variables where that might be large.

Injectable Definition
~~~~~~~~~~~~~~~~~~~~~

* Route: ``/injectables/<injectable_name>/definition``
* Returns: JSON

Get the definition of an injectable. If the injectable is anything other
than a function the result will be:

.. code-block:: json

    {
      "type": "variable"
    }

If the injectable is a function the returned data will include the
filename, line number, and text of the function:

.. code-block:: json

    {
      "type": "function",
      "filename": "data.py",
      "lineno": 42,
      "text": "function text",
      "html": "function text as html"
    }

The HTML has been marked up by `Pygments <http://pygments.org/>`__ with the
``.highlight`` class.

List Broadcasts
~~~~~~~~~~~~~~~

* Route: ``/broadcasts``
* Returns: JSON

List all registered broadcasts as objects with "cast" and "onto" keys:

.. code-block:: json

    {
      "broadcasts": [
        {"cast": "table1", "onto": "table2"},
        {"cast": "table3", "onto": "table2"}
      ]
    }

Broadcast Definition
~~~~~~~~~~~~~~~~~~~~

* Route: ``/broadcasts/<cast_name>/<onto_name>/definition``
* Returns: JSON

Get the definition of a broadcast, which is essentially the arguments that
were passed to the :py:func:`~orca.orca.broadcast` function to register
the broadcast:

.. code-block:: json

    {
      "cast": "table1",
      "cast_index": false,
      "cast_on": "onto_id",
      "onto": "table2",
      "onto_index": true,
      "onto_on": null
    }

List Steps
~~~~~~~~~~

* Route: ``/steps``
* Returns: JSON

Returns a list of registered step names:

.. code-block:: json

  {
    "steps": ["concat_yearly", "concat_monthly"]
  }

Step Definition
~~~~~~~~~~~~~~~

* Route: ``/steps/<step_name>/definition``
* Returns: JSON

Get the source of a step function.
The returned data will include the
filename, line number, and text of the function:

.. code-block:: json

    {
      "type": "function",
      "filename": "data.py",
      "lineno": 42,
      "text": "function text",
      "html": "function text as html"
    }

The HTML has been marked up by `Pygments <http://pygments.org/>`__ with the
``.highlight`` class.
