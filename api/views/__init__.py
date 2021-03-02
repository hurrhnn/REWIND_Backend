from os import listdir
from os.path import dirname, abspath
from importlib import import_module

PATH = dirname(abspath(__file__))
print(PATH)

__all__ = [x.rsplit(".", 1)[0] for x in listdir(PATH)
           if x.endswith(".py") and not x.startswith("__")]

for x in __all__:
    print(x)
    globals()[x] = import_module(f".{x}", "api.views")

del PATH, listdir, dirname, abspath, import_module
