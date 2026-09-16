Thanks for using Orca! 

This is an open source project that's part of the Urban Data Science Toolkit. Development and maintenance is a collaboration between UrbanSim Inc and other contributors.

You can contact Sam Maurer, the lead maintainer, at `maurer@urbansim.com`.


## If you have a problem:

- Take a look at the [open issues](https://github.com/UDST/orca/issues) and [closed issues](https://github.com/UDST/orca/issues?q=is%3Aissue+is%3Aclosed) to see if there's already a related discussion

- Open a new issue describing the problem -- if possible, include any error messages, the operating system and version of python you're using, and versions of any libraries that may be relevant


## Feature proposals:

- Take a look at the [open issues](https://github.com/UDST/orca/issues) and [closed issues](https://github.com/UDST/orca/issues?q=is%3Aissue+is%3Aclosed) to see if there's already a related discussion

- Post your proposal as a new issue, so we can discuss it (some proposals may not be a good fit for the project; see the project scope in the README)


## Contributing code:

- Create a new branch of `UDST/orca`, or fork the repository to your own account

- Make your changes, following the existing styles for code and inline documentation: [PEP 8](https://peps.python.org/pep-0008/) for code (checked with Ruff in CI) and the [NumPy format](https://numpydoc.readthedocs.io/en/latest/format.html) for docstrings

- Add tests if possible! They live in [`orca/tests`](https://github.com/UDST/orca/tree/main/orca/tests) and [`orca/utils/tests`](https://github.com/UDST/orca/tree/main/orca/utils/tests), and run with `pytest` from the repository root

- Open a pull request to the `UDST/orca` main branch, including a writeup of your changes -- take a look at some of the closed PR's for examples

- Automated checks run on every pull request: the test suite against the oldest and newest supported Python and dependency versions (on Linux, macOS, and Windows), a code quality check, a package build, and a documentation build

- Current maintainers will review the code, suggest changes, and hopefully merge it!


## Updating the version number:

- Each pull request that changes substantive code should increment the development version number, e.g. from `1.9.dev0` to `1.9.dev1`, so that users know exactly which version they're running

- It works best to do this just before merging (in case other PR's are merged first, and so you know the release date for the changelog and documentation)

- The version number lives in `orca/__init__.py` (`pyproject.toml` reads it from there); `docs/source/conf.py` repeats the latest production release

- Please also add a section to `HISTORY.rst` describing the changes!


## Updating the documentation: 

- See instructions in `docs/README.md`


## Preparing a release:

- Make a new branch for release prep

- Update the version number and changelog
  - `HISTORY.rst`
  - `orca/__init__.py`
  - `docs/source/conf.py`

- Make sure all the tests are passing, and check if updates are needed to `README.rst` or to the documentation

- Open a pull request to the main branch, and merge it once the checks pass

- Publish the release on GitHub: create a tag on the merge commit named with a `v` prefix (e.g. `v1.9` for version `1.9`), and use the changelog text as the release notes. Publishing the release starts the `Publish` workflow described below

- For anything more than a trivial release, do a dry run first with a release candidate: set the version to e.g. `1.9rc1`, tag it `v1.9rc1`, and mark the GitHub release as a pre-release. Pip ignores pre-releases unless asked for them (`pip install --pre orca==1.9rc1`), and the Conda Forge bots ignore them too, so this is a safe way to test the whole process. There's no need to delete the release candidate from PyPI afterward. Then repeat with the final version number

- After the release, rebuild and publish the documentation (see `docs/README.md`)


## Distributing a release on PyPI (for pip installation):

- Publishing is automated by the `Publish` GitHub Actions workflow (`.github/workflows/publish.yml`), which runs when a release is published on GitHub. It builds the source distribution and wheel, checks them with `twine check --strict`, installs the wheel and runs the test suite against it, confirms that the package version matches the release tag, and then uploads the files to PyPI using [Trusted Publishing](https://docs.pypi.org/trusted-publishers/), so no PyPI credentials are stored on GitHub

- The upload step runs in the repository's `pypi` deployment environment, which requires approval from a maintainer: once the build job succeeds, the workflow pauses until a reviewer approves the deployment from the workflow run page. Merging to `main` never publishes anything

- Check https://pypi.org/project/orca/ for the new version, and try `pip install orca` in a fresh environment

- One-time setup, in case it needs to be repeated: a PyPI owner of the project registers the trusted publisher at https://pypi.org/manage/project/orca/settings/publishing/ with owner `UDST`, repository `orca`, workflow `publish.yml`, and environment `pypi`; and a repository admin creates the `pypi` environment at https://github.com/UDST/orca/settings/environments with required reviewers

- Manual fallback, if the workflow can't be used: register an account at https://pypi.org with two-factor authentication enabled, ask one of the current maintainers to add you to the project, and create an API token scoped to the Orca project. Then `pip install build twine`, delete any old files in `dist/`, and run `python -m build`, `twine check --strict dist/*`, and `twine upload dist/*`, entering `__token__` as the username and the token as the password


## Distributing a release on Conda Forge (for conda installation):

- The [conda-forge/orca-feedstock](https://github.com/conda-forge/orca-feedstock) repository controls the Conda Forge release, including which GitHub users have maintainer status for the feedstock

- Conda Forge bots usually detect new releases on PyPI within a few hours and open a pull request to update the feedstock, which a current feedstock maintainer needs to review and merge

- Before merging, check that the run requirements and the Python version floor in `recipe/meta.yaml` still match `pyproject.toml`; the bot only updates the version and hash. Additional changes can be pushed to the bot's branch, for example to update the requirements or the list of maintainers

- You can also fork the feedstock and open a pull request manually, updating the version number and pasting the new hash of the `.tar.gz` file uploaded to PyPI (available on the pypi.org project page). It seems like this must be done from a personal account (not a group account like UDST) so that the bots can be granted permission for automated cleanup

- Check https://anaconda.org/conda-forge/orca for the new version (may take a few minutes for it to appear)


## Branch policy

The `main` branch is the default integration and release branch. All new pull requests should target `main`. (Before v1.9, development happened on a `dev` branch that was periodically merged into `main` for releases; as of the v1.9 release cycle, `dev` is retired.)
