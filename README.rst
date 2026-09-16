.. image:: https://img.shields.io/badge/coverage-97%25-green
  :alt: Coverage

Orca
====

Orca is a Python library for task orchestration. It's designed for workflows like city simulation, where the data representing a model's state is so large that it needs to be managed outside of the task graph.

The building blocks of a workflow are "steps", Python functions that can be assembled on the fly into linear or cyclical pipelines. Steps typically interact with a central data store that persists in memory while the pipeline runs. Derived tables and columns can be updated automatically as base data changes, and pipeline components are evaluated lazily to reduce unnecessary overhead.

Orca is used in `UrbanSim <https://github.com/udst/urbansim>`__ and other projects.

Project scope
-------------

**Status:** Active

**Mission:** Orca provides lightweight Python orchestration for data-intensive
analytical and simulation workflows.

**Architecture:** Orca's reference architecture targets dependency-managed
analytical computation within a Python process.

The project maintains and develops:

* registration and execution of workflow steps;
* managed tables, columns, and other injectable resources;
* dependency tracking and lazy evaluation;
* iterative and cyclical simulation pipelines;
* caching and lifecycle management within a Python process; and
* reusable APIs for composing model workflows.

Development that improves reliability, composability, performance, and
developer usability is welcome within this mission and architecture. Material
changes to the project's mission or execution architecture are considered
through UDST's organization-level governance process.

See the `UDST Project Directory
<https://github.com/UDST/.github/blob/main/PROJECTS.md>`__ for
organization-wide project status and policy.

Documentation
-------------

- `udst.github.io/orca/ <https://udst.github.io/orca/>`__

Installation
------------

- ``pip install orca``
- ``conda install orca --channel conda-forge``
