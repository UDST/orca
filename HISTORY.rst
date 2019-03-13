v1.5.2
======

* Update required version of PyTables to solve an installation problem in Pip.

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
