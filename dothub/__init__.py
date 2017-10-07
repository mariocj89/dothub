"""Dothub allows you to specify your github configuration as code by using config files"""

from ._version import __version__
from .cli import dothub as cli_entry
from .config import load_config, CONFIG_FILE

__all__ = ['__version__', 'cli_entry', 'load_config', 'CONFIG_FILE']

