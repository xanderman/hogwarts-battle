# Base must be imported first
from .base import *

# Import everything else
from importlib import import_module
from pathlib import Path
for f in Path(__file__).parent.glob("*.py"):
    if f.stem.startswith("_"):
        continue
    if f.stem.startswith("test_"):
        continue
    if f.stem == "base":
        continue
    import_module(f".{f.stem}", __package__)
del f, import_module, Path
