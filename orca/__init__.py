from importlib.metadata import version as _distribution_version

from .orca import *

version = __version__ = _distribution_version("orca")
