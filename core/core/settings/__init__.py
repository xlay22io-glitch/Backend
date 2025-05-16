"""
Dynamic settings loader.

If DJANGO_ENV is unset → dev settings are used.
Valid values: dev / prod
"""
import os
from importlib import import_module

env = os.getenv("DJANGO_ENV", "dev").lower()
module = import_module(f"core.settings.{env}")
globals().update(vars(module))
