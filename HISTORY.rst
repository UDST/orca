v1.9
====

2026/09/16

First release since v1.8 in October 2022. It restores compatibility with
current versions of Python, Pandas, and NumPy, modernizes the packaging and
continuous integration, and fixes two long-standing issues.

* Requires Python 3.10 or later, and is tested on Python 3.10 through 3.14
  with NumPy 1.21 through 2.x, Pandas 1.5 through 3.x, PyTables 3.8+, and
  PyToolz 0.12+. Drops support for Python 2 and for Python 3.9 and earlier
  (#62).
* Behavior change under Pandas 3: with ``copy_col=False``, Pandas's
  mandatory copy-on-write means that modifying a column returned from a
  table no longer writes through to the table's underlying DataFrame.
  Use ``update_col`` or ``update_col_from_series`` to change table values
  (#62).
* ``to_frame(columns)`` returns columns in the order requested, whether
  they are local or registered columns; since v1.4 the order of registered
  columns had varied from call to call. ``merge_tables(columns=...)``
  likewise resolves columns in the order given (#57, #68).
* ``broadcast`` accepts lists of column names for ``cast_on`` and
  ``onto_on``, for merges on multiple columns, as ``pandas.merge`` does
  (#37, #68).
* Moves package metadata to ``pyproject.toml`` and removes ``setup.py``
  (#62).
* Replaces the 2022 GitHub Actions workflows with continuous integration
  that tests the minimum and current dependency versions on Linux, macOS,
  and Windows, checks code quality, validates the built distributions, and
  builds the documentation with warnings as errors (#62, #66). Releases are
  built, verified, and published to PyPI by a GitHub Actions workflow using
  Trusted Publishing (#67).
* ``main`` is now the integration branch; ``dev`` is retired (#62).
* Documents the project's scope and status in the README (#64).
* Thanks to Paul Waddell for the compatibility, packaging, and CI work, and
  to Jeff Doyle for the multi-column broadcast report.

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
