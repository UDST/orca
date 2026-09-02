v1.9
====

* Require Python 3.10 or newer.
* Support pandas 2 and 3, NumPy 2, and current PyTables, with minimum
  versions of pandas 1.5, NumPy 1.21, PyTables 3.8, and PyToolz 0.12.
* Behavior change under pandas 3: with ``copy_col=False``, pandas's
  mandatory copy-on-write means that modifying a column returned from a
  table no longer writes through to the table's underlying DataFrame.
  Use ``update_col`` or ``update_col_from_series`` to change table values.
* Modernize Python packaging and continuous integration.

v1.8
====

* Adds granular column specification to `write_tables`.

v1.7
====

* Support for PyTables 3.7+
* Tested against Python 3.9 and 3.10
* Removes server module

v1.6
====

* New functionality to clear cache and update cache scope: https://udst.github.io/orca/core.html#caching
* Server module deprecated

v1.5.4
======

* Support for PyToolz 0.11+

v1.5.3
======

* Updated requirements to streamline installation.

v1.5.2
======

* Never released.

v1.5.1
======

* Update required version of `toolz`.

v1.5.0
======

* Remove `zbox` from dependencies.

v1.4.0
======

* Modify `merge_tables` behavior in case of identical column names in multiple
tables
* Add `cast` option to `update_col_from_series` to handle type mismatches
* Updated logic for outputting HDF5 files
* Add file compression to `run` and `write_tables`
* Fix base year output for `iter_var` dependencies
* Add `iter_step` injectable to track current simulation step
* Change default behavior to output only local tables to `out_run_tables`
* Use sets instead of lists in `to_frame`


v1.3.0
======

* Add `temporary_tables` context manager

v1.2.0
======

* Add Orca server and supporting functionality

v1.1.0
======

* Rename ``clear_sim`` function to ``clear_all``
