import importlib
from pathlib import Path
import unittest
import sys


def import_parents(level=1):
    global __package__
    file = Path(__file__).resolve()
    parent, top = file.parent, file.parents[level]

    sys.path.append(str(top))
    try:
        sys.path.remove(str(parent))
    except ValueError:
        pass

    __package__ = '.'.join(parent.parts[len(top.parts):])
    importlib.import_module(__package__)


if __name__ == '__main__' and __package__ is None:
    import_parents(level=2)


if __name__ == "__main__":
    dir = "../test"
    suite = unittest.defaultTestLoader.discover(dir, pattern='test_*.py')
    runner = unittest.TextTestRunner()
    runner.run(suite)