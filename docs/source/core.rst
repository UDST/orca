Orca Core
=========

.. note::
   In the documentation below the following imports are implied::

       import orca
       import pandas as pd

Tables
------

Tables are Pandas DataFrames_.
Use the :py:func:`~orca.orca.add_table` function to register
a DataFrame under a given name::

    df = pd.DataFrame({'a': [1, 2, 3]})
    orca.add_table('my_table', df)

Or you can use the decorator :py:func:`~orca.orca.table`
to register a function that returns a DataFrame::

    @orca.table('halve_my_table')
    def halve_my_table(my_table):
        df = my_table.to_frame()
        return df / 2

The decorator argument, which specifies the name to register the table with,
is optional. If left out, the table is registered under the name of the
function that is being decorated. The decorator example above could be
written more concisely::

    @orca.table()
    def halve_my_table(my_table):
        df = my_table.to_frame()
        return df / 2

Note that the decorator parentheses are still required.

By registering ``halve_my_table`` as a function, its values will always be
half those in ``my_table``, even if ``my_table`` is later changed.
If you'd like a function to *not* be evaluated every time it
is used, pass the ``cache=True`` keyword when registering it.

Here's a demo of the above table definitions shown in IPython:

.. code-block:: python

    In [19]: wrapped = orca.get_table('halve_my_table')

    In [20]: wrapped.to_frame()
    Out[20]:
         a
    0  0.5
    1  1.0
    2  1.5

Table Wrappers
~~~~~~~~~~~~~~

Notice in the table function above that we had to call a
:py:meth:`~orca.orca.DataFrameWrapper.to_frame` method
before using the table in a math operation. The values injected into
functions are not DataFrames, but specialized wrappers.
The wrappers facilitate caching, `computed columns <#columns>`__,
and lazy evaluation of table functions. Learn more in the API documentation:

* :py:class:`~orca.orca.DataFrameWrapper`
* :py:class:`~orca.orca.TableFuncWrapper`

Automated Merges
~~~~~~~~~~~~~~~~

Certain analyses can be easiest when some tables are merged together,
but in other places it may be best to keep the tables separate.
Orca can make these on-demand merges easy by letting you define table
relationships up front and then performing the merges for you as needed.
We call these relationships "broadcasts" (as in a rule for how to broadcast
one table onto another) and you register them using the
:py:func:`~orca.orca.broadcast` function.

For an example we'll first define some DataFrames that contain links
to one another and register them with Orca::

    df_a = pd.DataFrame(
        {'a': [0, 1]},
        index=['a0', 'a1'])
    df_b = pd.DataFrame(
        {'b': [2, 3, 4, 5, 6],
         'a_id': ['a0', 'a1', 'a1', 'a0', 'a1']},
        index=['b0', 'b1', 'b2', 'b3', 'b4'])
    df_c = pd.DataFrame(
        {'c': [7, 8, 9]},
        index=['c0', 'c1', 'c2'])
    df_d = pd.DataFrame(
        {'d': [10, 11, 12, 13, 15, 16, 16, 17, 18, 19],
         'b_id': ['b2', 'b0', 'b3', 'b3', 'b1', 'b4', 'b1', 'b4', 'b3', 'b3'],
         'c_id': ['c0', 'c1', 'c1', 'c0', 'c0', 'c2', 'c1', 'c2', 'c1', 'c2']},
        index=['d0', 'd1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8', 'd9'])

    orca.add_table('a', df_a)
    orca.add_table('b', df_b)
    orca.add_table('c', df_c)
    orca.add_table('d', df_d)

The tables have data so that 'a' can be broadcast onto 'b',
and 'b' and 'c' can be broadcast onto 'd'.
We use the :py:func:`~orca.orca.broadcast` function
to register those relationships::

    orca.broadcast(cast='a', onto='b', cast_index=True, onto_on='a_id')
    orca.broadcast(cast='b', onto='d', cast_index=True, onto_on='b_id')
    orca.broadcast(cast='c', onto='d', cast_index=True, onto_on='c_id')

The syntax is similar to that of the
`pandas merge function <http://pandas.pydata.org/pandas-docs/stable/generated/pandas.merge.html#pandas.merge>`__,
and indeed ``merge`` is used behind the scenes.
Once the broadcasts are defined, use the
:py:func:`~orca.orca.merge_tables` function to get a
merged DataFrame. Some examples in IPython:

.. code-block:: python

    In [4]: orca.merge_tables(target='b', tables=[a, b])
    Out[4]:
       a_id  b  a
    b0   a0  2  0
    b3   a0  5  0
    b1   a1  3  1
    b2   a1  4  1
    b4   a1  6  1

    In [5]: orca.merge_tables(target='d', tables=[a, b, c, d])
    Out[5]:
       b_id c_id   d  c a_id  b  a
    d0   b2   c0  10  7   a1  4  1
    d3   b3   c0  13  7   a0  5  0
    d2   b3   c1  12  8   a0  5  0
    d8   b3   c1  18  8   a0  5  0
    d9   b3   c2  19  9   a0  5  0
    d4   b1   c0  15  7   a1  3  1
    d6   b1   c1  16  8   a1  3  1
    d1   b0   c1  11  8   a0  2  0
    d5   b4   c2  16  9   a1  6  1
    d7   b4   c2  17  9   a1  6  1

Note that it's the target table's index that you find in the final merged
table, though the order may have changed.
:py:func:`~orca.orca.merge_tables` has an optional
``columns=`` keyword that can contain column names from any the tables
going into the merge so you can limit which columns end up in the final table.
(Columns necessary for performing merges will be included whether or not
they are in the ``columns=`` list.)

.. note:: :py:func:`~orca.orca.merge_tables` calls
   `pandas.merge <http://pandas.pydata.org/pandas-docs/stable/generated/pandas.merge.html#pandas.merge>`__
   with ``how='inner'``, meaning that only items that
   appear in both tables are kept in the merged table.

Columns
-------

Often, not all the columns you need are preexisting on your tables.
You may need to collect information from other tables
or perform a calculation to generate a column. Orca allows you to
register a Series_ or function as a column on a registered table.
Use the :py:func:`~orca.orca.add_column` function or
the :py:func:`~orca.orca.column` decorator::

    s = pd.Series(['a', 'b', 'c'])
    orca.add_column('my_table', 'my_col', s)

    @orca.column('my_table')
    def my_col_x2(my_table):
        df = my_table.to_frame(columns=['my_col'])
        return df['my_col'] * 2

In the ``my_col_x2`` function we use the ``columns=`` keyword on
:py:meth:`~orca.orca.DataFrameWrapper.to_frame` to get only
the one column necessary for our calculation. This can be useful for
avoiding unnecessary computation or to avoid recursion (as would happen
in this case if we called ``to_frame()`` with no arguments).

Accessing columns on a table is such a common occurrence that there
are additional ways to do so without first calling ``to_frame()``
to create an actual ``DataFrame``.

:py:class:`~orca.orca.DataFrameWrapper` supports accessing
individual columns in the same ways as ``DataFrames``::

    @orca.column('my_table')
    def my_col_x2(my_table):
        return my_table['my_col'] * 2  # or my_table.my_col * 2

Or you can use an expression to have a single column injected into a function::

    @orca.column('my_table')
    def my_col_x2(data='my_table.my_col'):
        return data * 2

In this case, the label ``data``, expressed as ``my_table.my_col``,
refers to the column ``my_col``, which is a pandas Series_ within
the table ``my_table``.

A demonstration in IPython using the column definitions from above:

.. code-block:: python

    In [29]: wrapped = orca.get_table('my_table')

    In [30]: wrapped.columns
    Out[30]: ['a', 'my_col', 'my_col_x2']

    In [31]: wrapped.local_columns
    Out[31]: ['a']

    In [32]: wrapped.to_frame()
    Out[32]:
       a my_col_x2 my_col
    0  1        aa      a
    1  2        bb      b
    2  3        cc      c

:py:class:`~orca.orca.DataFrameWrapper` has
:py:attr:`~orca.orca.DataFrameWrapper.columns`
and :py:attr:`~orca.orca.DataFrameWrapper.local_columns`
attributes that, respectively, list all the columns on a table and
only those columns that are part of the underlying DataFrame.

Columns are stored separate from tables so it is safe to define a column
on a table and then replace that table with something else. The column
will remain associated with the table.

Injectables
-----------

You will probably want to have things besides tables injected into functions,
for which Orca has "injectables". You can register *anything* and have
it injected into functions.
Use the :py:func:`~orca.orca.add_injectable` function or the
:py:func:`~orca.orca.injectable` decorator::

    orca.add_injectable('z', 5)

    @orca.injectable(autocall=False)
    def pow(x, y):
        return x ** y

    @orca.injectable()
    def zsquared(z, pow):
        return pow(z, 2)

    @orca.table()
    def ztable(my_table, zsquared):
        df = my_table.to_frame(columns=['a'])
        return df * zsquared

By default injectable functions are evaluated before injection and the return
value is passed into other functions. Use ``autocall=False`` to disable this
behavior and instead inject the function itself.
Like tables and columns, injectable functions that are automatically evaluated
can have their results cached with ``cache=True``.

Functions that are not automatically evaluated can also have their results
cached using the ``memoize=True`` keyword along with ``autocall=False``.
A memoized injectable will cache results based on the function inputs,
so this only works if the function inputs are hashable
(usable as dictionary keys).
Memoized functions can have their caches cleared manually using their
``clear_cached`` function attribute.
The caches of memoized functions are also hooked into the global Orca
caching system,
so you can also manage their caches via the ``cache_scope`` keyword argument
and the :py:func:`~orca.orca.clear_cache` function.

An example of the above injectables in IPython:

.. code-block:: python

    In [38]: wrapped = orca.get_table('ztable')

    In [39]: wrapped.to_frame()
    Out[39]:
        a
    0  25
    1  50
    2  75

Caching
-------

Orca has cache system so that function results can be stored for re-use when it
is not necessary to recompute them every time they are used.

The decorators
:py:func:`~orca.orca.table`,
:py:func:`~orca.orca.column`, and
:py:func:`~orca.orca.injectable`
all take two keyword arguments related to caching:
``cache`` and ``cache_scope``.

By default results are not cached. Register functions with ``cache=True``
to enable caching of their results.

Cache Scope
~~~~~~~~~~~

Cached items have an associated "scope" that allows Orca to automatically
manage how long functions have their results cached before re-evaluating them.
The three scope settings are:

* ``'forever'`` (the default setting) -
  Results are cached until manually cleared by user commands.
* ``'iteration'`` -
  Results are cached for the remainder of the current pipeline iteration.
* ``'step'`` -
  Results are cached until the current pipeline step finishes.

An item's cache scope can be modified using 
:py:func:`~orca.orca.update_injectable_scope`,
:py:func:`~orca.orca.update_table_scope`, or
:py:func:`~orca.orca.update_column_scope`. Omitting the scope or passing ``None``
turns caching off for the item. These functions were added in Orca v1.6.

Disabling Caching
~~~~~~~~~~~~~~~~~

There may be situations, especially during testing,
that require disabling the caching system.

Caching can be turned off globally using the
:py:func:`~orca.orca.disable_cache` function
(and turned back on by :py:func:`~orca.orca.enable_cache`).

To run a block of commands with the cache disabled, but have it automatically
re-enabled, use the :py:func:`~orca.orca.cache_disabled`
context manager::

    with orca.cache_disabled():
        result = orca.eval_variable('my_table')

Manually Clearing Cache
~~~~~~~~~~~~~~~~~~~~~~~

Orca's entire cache can be cleared using :py:func:`~orca.orca.clear_cache`.

Cache can also be cleared manually for individual items, to allow finer control
over re-computation. These functions were added in Orca v1.6.

To clear the cached value of an injectable, use
:py:func:`~orca.orca.clear_injectable`. To clear the cached copy of an entire
table, use :py:func:`~orca.orca.clear_table`.

A dynamically generated column can be cleared using
:py:func:`~orca.orca.clear_column`::

    orca.clear_column('my_table', 'my_col')

To clear all dynamically generated columns from a table, use
:py:func:`~orca.orca.clear_columns`::

    orca.clear_columns('my_table')

Or clear a subset of the columns like this::

    orca.clear_columns('my_table', ['col1', 'col2'])


Steps
-----

A step is a function run by Orca with argument matching.
Use the :py:func:`~orca.orca.step` decorator to register a step function.
Steps are generally important for their side-effects, their
return values are discarded during pipeline runs.
For example, a step might replace a column
in a table (a new table, though similar to ``my_table`` above)::

    df = pd.DataFrame({'a': [1, 2, 3]})
    orca.add_table('new_table', df)

    @orca.step()
    def replace_col(new_table):
        new_table['a'] = [4, 5, 6]

Or update some values in a column::

    @orca.step()
    def update_col(new_table):
        s = pd.Series([99], index=[1])
        new_table.update_col_from_series('a', s)

Or add rows to a table::

    @orca.step()
    def add_rows(new_table):
        new_rows = pd.DataFrame({'a': [100, 101]}, index=[3, 4])
        df = new_table.to_frame()
        df = pd.concat([df, new_rows])
        orca.add_table('new_table', df)

The first two of the above examples update ``my_tables``'s underlying
DataFrame and so require it to be a :py:class:`~orca.orca.DataFrameWrapper`.
If your table is a wrapped function, not a DataFrame, you can update
columns by replacing them entirely with a new Series_ using the
:py:func:`~orca.orca.add_column` function.

A demonstration of running the above steps:

.. code-block:: python

    In [68]: orca.run(['replace_col', 'update_col', 'add_rows'])
    Running step 'replace_col'
    Running step 'update_col'
    Running step 'add_rows'

    In [69]: orca.get_table('new_table').to_frame()
    Out[69]:
         a
    0    4
    1   99
    2    6
    3  100
    4  101

In the context of a simulation steps can be thought of as model steps
that will often advance the simulation by updating data.
Steps are plain Python functions, though, and there is no restriction on
what they are allowed to do.

Running Pipelines
-----------------

You start pipelines by calling the :py:func:`~orca.orca.run` function and
listing which steps you want to run.
Calling :py:func:`~orca.orca.run` with just a list of steps,
as in the above example, will run through the steps once.
To run the pipeline over some a sequence, provide those values as a sequence
to :py:func:`~orca.orca.run` using the ``iter_vars`` argument.

The ``iter_var`` injectable stores the current value from the ``iter_vars`` argument to :py:func:`~orca.orca.run` function. 
The ``iter_step`` injectable is a ``namedtuple`` with fields named ``step_num`` and ``step_name``, 
stored in that order. 
``step_num`` is a zero-based index based on the list of step names passed to the :py:func:`~orca.orca.run` function.

.. code-block:: python

    In [77]: @orca.step()
       ....: def print_year(iter_var,iter_step):
       ....:         print '*** the iteration value is {} ***'.format(iter_var)
       ....:         print '*** step number {0} is named {1} ***'.format(iter_step.step_num, iter_step.step_name)
       ....:

    In [78]: orca.run(['print_year'], iter_vars=range(2010, 2015))
    Running iteration 1 with iteration value 2010
    Running step 'print_year'
    *** the iteration value is 2010 ***
    *** step number 0 is named print_year ***
    Time to execute step 'print_year': 0.00 s
    Total time to execute iteration 1 with iteration value 2010: 0.00 s
    Running iteration 2 with iteration value 2011
    Running step 'print_year'
    *** the iteration value is 2011 ***
    *** step number 0 is named print_year ***
    Time to execute step 'print_year': 0.00 s
    Total time to execute iteration 2 with iteration value 2011: 0.00 s
    Running iteration 3 with iteration value 2012
    Running step 'print_year'
    *** the iteration value is 2012 ***
    *** step number 0 is named print_year ***
    Time to execute step 'print_year': 0.00 s
    Total time to execute iteration 3 with iteration value 2012: 0.00 s
    Running iteration 4 with iteration value 2013
    Running step 'print_year'
    *** the iteration value is 2013 ***
    *** step number 0 is named print_year ***
    Time to execute step 'print_year': 0.00 s
    Total time to execute iteration 4 with iteration value 2013: 0.00 s
    Running iteration 5 with iteration value 2014
    Running step 'print_year'
    *** the iteration value is 2014 ***
    *** step number 0 is named print_year ***
    Time to execute step 'print_year': 0.00 s
    Total time to execute iteration 5 with iteration value 2014: 0.00 s

Running Orca Components a la Carte
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It can be useful to have Orca evaluate single variables and steps,
especially during development and testing.
To achieve this, use the
:py:func:`~orca.orca.eval_variable` and
:py:func:`~orca.orca.eval_step` functions.

``eval_variable`` takes the name of a variable (including variable expressions)
and returns that variable as it would be injected into a function Orca.
``eval_step`` takes the name of a step, runs that
step with variable injection, and returns any result.

.. note::
   Most steps don't have return values because Orca
   ignores them, but they can be useful for testing.

Both :py:func:`~orca.orca.eval_variable` and :py:func:`~orca.orca.eval_step`
take arbitrary keyword arguments that are temporarily turned into injectables
within Orca while the evaluation is taking place.
When the evaluation is complete Orca's state is reset to whatever
it was before calling the ``eval`` function.

An example of :py:func:`~orca.orca.eval_variable`:

.. code-block:: python

    In [15]: @orca.injectable()
       ....: def func(x, y):
       ....:     return x + y
       ....:

    In [16]: orca.eval_variable('func', x=1, y=2)
    Out[16]: 3

The keyword arguments are only temporarily set as injectables,
which can lead to errors in a situation like this with a table
where the evaluation of the table is delayed until
:py:meth:`~orca.orca.DataFrameWrapper.to_frame` is called:

.. code-block:: python

    In [12]: @orca.table()
       ....: def table(x, y):
       ....:     return pd.DataFrame({'a': [x], 'b': [y]})
       ....:

    In [13]: orca.eval_variable('table', x=1, y=2)
    Out[13]: <orca.TableFuncWrapper at 0x100733850>

    In [14]: orca.eval_variable('table', x=1, y=2).to_frame()
    ---------------------------------------------------------------------------
    KeyError                                  Traceback (most recent call last)
    <ipython-input-14-5bf660fb07b7> in <module>()
    ----> 1 orca.eval_variable('table', x=1, y=2).to_frame()

    <truncated>

    KeyError: 'y'

In order to get the injectables to be set for a controlled term you can
use the :py:func:`~orca.orca.injectables` context manager
to set the injectables:

.. code-block:: python

    In [12]: @orca.table()
       ....: def table(x, y):
       ....:     return pd.DataFrame({'a': [x], 'b': [y]})
       ....:

    In [20]: with orca.injectables(x=1, y=2):
       ....:     df = orca.eval_variable('table').to_frame()
       ....:

    In [21]: df
    Out[21]:
       a  b
    0  1  2

Archiving Data
~~~~~~~~~~~~~~

An option to the :py:func:`~orca.orca.run` function is to have
it save table data at set intervals.
Tables (and only tables) are saved as DataFrames_ to an HDF5 file via pandas'
`HDFStore <http://pandas.pydata.org/pandas-docs/stable/io.html#hdf5-pytables>`__
feature. If Orca is running only one loop the tables are stored
under their registered names. If it is running multiple iterations the tables are
stored under names like ``'<iter_var>/<table name>'``.
For example, if ``iter_var`` is ``2020`` the "buildings" table would be stored
as ``'2020/buildings'``.
The ``out_interval`` keyword to :py:func:`~orca.orca.run`
controls how often the tables are saved out. For example, ``out_interval=5``
saves tables every fifth iteration.
In addition, the final data is always saved
under the key ``'final/<table name>'``.

Argument Matching
-----------------

A key feature of Orca is that it matches the names of function arguments to
the names of registered variables in order to
inject variables when evaluating functions.
For that reason, it's important that variables be registered with names
that are also
`valid Python variables <http://en.wikibooks.org/wiki/Python_Beginner_to_Expert/Native_Types>`__.

Variable Expressions
~~~~~~~~~~~~~~~~~~~~

Argument matching is extended by a feature we call "variable expressions".
Expressions allow you to specify a variable to inject with Python keyword
arguments. Here's an example redone from above using
variable expressions::

    @orca.table()
    def halve_my_table(data='my_table'):
        df = data.to_frame()
        return df / 2

The variable registered as ``'my_table'`` is injected into this function
as the argument ``data``.

Expressions can also be used to refer to columns within a registered table::

    @orca.column('my_table')
    def halved(data='my_table.a'):
        return data / 2

In this case, the expression ``my_table.a`` refers to the column ``a``,
which is a pandas Series_ within the table ``my_table``. We return
a new Series to register a new column on ``my_table`` using the
:py:func:`~orca.orca.column` decorator. We can take a
look in IPython:

.. code-block:: python

    In [21]: orca.get_table('my_table').to_frame()
    Out[21]:
       a  halved
    0  1     0.5
    1  2     1.0
    2  3     1.5

Expressions referring to columns may be useful in situations where a
function requires only a single column from a table and the user would
like to specifically document that in the function's arguments.

API
---

.. currentmodule:: orca.orca

Table API
~~~~~~~~~

.. autosummary::

   add_table
   table
   get_table
   list_tables
   DataFrameWrapper
   TableFuncWrapper

Column API
~~~~~~~~~~

.. autosummary::

   add_column
   column
   list_columns

Injectable API
~~~~~~~~~~~~~~

.. autosummary::

   add_injectable
   injectable
   get_injectable
   list_injectables

Merge API
~~~~~~~~~

.. autosummary::

   broadcast
   list_broadcasts
   merge_tables

Step API
~~~~~~~~

.. autosummary::

   add_step
   step
   get_step
   list_steps
   run

Cache API
~~~~~~~~~

.. autosummary::

   clear_cache
   disable_cache
   enable_cache
   cache_on
   clear_injectable
   clear_table
   clear_column
   clear_columns
   update_injectable_scope
   update_table_scope
   update_column_scope

API Docs
~~~~~~~~

.. automodule:: orca.orca
   :members:

.. _DataFrame: http://pandas.pydata.org/pandas-docs/stable/dsintro.html#dataframe
.. _DataFrames: http://pandas.pydata.org/pandas-docs/stable/dsintro.html#dataframe
.. _Series: http://pandas.pydata.org/pandas-docs/stable/dsintro.html#series
