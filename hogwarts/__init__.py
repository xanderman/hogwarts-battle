# Base must be imported first
from .base import *

# These are referenced by class from outside the module
from .detention import Detention
from .reparo import Reparo
from .tergeo import Tergeo

# Import everything else
from importlib import import_module
from pathlib import Path
for f in Path(__file__).parent.glob("*.py"):
    if f.stem.startswith("_"):
        continue
    if f.stem.startswith("test_"):
        continue
    if f.stem == "base" or f.stem == "detention" or f.stem == "reparo" or f.stem == "tergeo":
        continue
    import_module(f".{f.stem}", __package__)
del f, import_module, Path
