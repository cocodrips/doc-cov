import argparse
import enum
import importlib
import inspect
import logging
import os
import pathlib
import pkgutil
import pydoc
import sys

logger = logging.getLogger(__name__)


class Type(enum.Enum):
    MODULE = 1
    CLASS = 2
    FUNCTION = 3


def report(coverage, output, output_types, is_all=False):
    """
    Args:
        coverage(Coverage):
        output(str): 'str' or 'csv'
        output_types([Type]):

    Returns:
        None
    """
    if output == 'str' and coverage.name and is_all:
        print('=============================')
        print(coverage.name)
        print('-----------------------------')
    for t in output_types:
        counter = coverage.counters[t.name]
        if output == 'str':
            print('{0:<10} {1:>3} / {2:>3} {3}'.format(
                t.name.lower(), counter.true, counter.all, counter.ratio_str()
            ))
        if output == 'csv':
            print(','.join((coverage.name, t.name.lower(),
                            str(counter.true), str(counter.all),
                            counter.ratio_str())))


class Counter():
    def __init__(self, all=0, true=0):
        self.all = all
        self.true = true

    def __add__(self, other):
        return Counter(all=self.all + other.all,
                       true=self.true + other.true)

    def __repr__(self):
        return '<Counter: {0}/{1}>'.format(self.true, self.all)

    def __eq__(self, other):
        return self.all == other.all and self.true == other.true

    def ratio_str(self):
        ratio = self.ratio()
        if ratio is None:
            return '-'
        return '{0:.2f}%'.format(ratio * 100)

    def ratio(self):
        if self.all < 1:
            return None
        return self.true / self.all

    def add(self, object):
        self.all += 1
        self.true += has_doc(object)


class Coverage():
    def __init__(self, counters=None, name=''):
        if counters is not None:
            self.counters = counters
        else:
            self.counters = {}
            for t in Type.__members__:
                self.counters[t] = Counter()

        self.name = name

    def __add__(self, other):
        """
        :param other(Coverage):
        :return:
            Coverage
        """
        merge = {}

        for t in Type.__members__:
            merge[t] = self.counters[t] + other.counters[t]

        return Coverage(name=self.name, counters=merge)

    def __repr__(self):
        c = self.counters[Type.FUNCTION.name]
        return f'<Coverage: {self.name} function:{c.true}/{c.all}>'

    def add(self, object, type_):
        """
        :param object(object): 
        :param type_(Type): 
        :return:
            None
        """
        self.counters[type_.name].add(object)


def has_doc(object):
    """
    target object has document or not.

    :param object: module, function,
    :return:
        int: 0 or 1
    """
    if not hasattr(object, '__doc__'):
        raise Exception()
    if object.__doc__ is None:
        return 0
    return int(object.__doc__.strip() != "")



def visiblename(name, all=None, obj=None):

    if name in {'__author__', '__builtins__', '__cached__', '__credits__',
                '__date__', '__doc__', '__file__', '__spec__',
                '__loader__', '__module__', '__name__', '__package__',
                '__path__', '__qualname__', '__slots__', '__version__'}:
        return False
    if name.startswith('__') and name.endswith('__'):
        return True
    if name.startswith('_') and hasattr(obj, '_fields'):
        return True
    if all is not None:
        return name in all
    else:
        return not name.startswith('_')


def count_class(object):

    name = object.__name__  # ignore the passed-in name
    try:
        all = object.__all__
    except AttributeError:
        all = None

    coverage = Coverage(name=name)

    if not inspect.isclass(object):
        return coverage

    coverage.add(object, Type.CLASS)
    for func_name, obj in inspect.getmembers(object, inspect.isfunction):
        if inspect.isbuiltin(obj):
            continue
        if visiblename(func_name, all, object):
            coverage.add(obj, Type.FUNCTION)

    return coverage

def count_module(object):
    """
    Reference: pydoc.HTMLDoc.docmodule

    :param object(object): module
    :return:
    """
    name = object.__name__  # ignore the passed-in name
    try:
        all = object.__all__
    except AttributeError:
        all = None

    coverage = Coverage(name=name)

    if inspect.ismodule(object):
        coverage.add(object, Type.MODULE)

    for class_name, obj in inspect.getmembers(object, inspect.isclass):
        # if __all__ exists, believe it.  Otherwise use old heuristic.
        if (all is not None or
                (inspect.getmodule(obj) or object) is object):
            if visiblename(class_name, all, object):
                coverage += count_class(obj)

    for func_name, obj in inspect.getmembers(object, inspect.isfunction):
        if visiblename(func_name, all, object):
            if inspect.isfunction(obj):
                coverage.add(obj, Type.FUNCTION)

    return coverage


def _get_coverage(package_name, importer, modname, ispkg, ignores):
    """

    Args:
        importer:
        modname:
        ispkg:
        ignores [pathlib.Path]:

    Returns:

    """

    importer_path = pathlib.Path(importer.path)
    for ignore in ignores:
        if importer_path.samefile(ignore):
            return
        if str(pathlib.Path(importer.path).resolve()).startswith(str(ignore)):
            return
        if ispkg and (importer_path / modname.split('.')[-1]).samefile(ignore):
            return

    try:
        if ispkg:
            spec = pkgutil._get_spec(importer, modname)
            object = importlib._bootstrap._load(spec)
        else:
            import_path = f"{package_name}.{modname}"
            object = importlib.import_module(import_path)
        counter = count_module(object)
        return counter
    except ImportError as e:
        logger.error(f"Failed to import {modname}: {e}")
        return
    except Exception as e:
        logger.error(f"Failed to parse: {modname}: {e}")
        return


def walk(root_path, ignore_paths=None):
    """
    Count coverage of root_path tree.

    Under ignores files is not counted.

    Args:
        root_path(str): Start path.

    Returns:
        [Coverage], Coverage: Return all module coverage and summary.
    """

    package_name = os.path.basename(os.path.normpath(root_path))
    scriptdir = os.path.abspath(os.path.join(root_path, '..'))

    if scriptdir in sys.path:
        sys.path.remove(scriptdir)
    sys.path.insert(0, scriptdir)

    packages = pkgutil.walk_packages([root_path])

    coverages = []
    summary = Coverage()

    ignores = []
    if ignore_paths:
        ignores = [pathlib.Path(ignore_path).resolve() for ignore_path in ignore_paths]

    for importer, modname, ispkg in packages:
        coverage = _get_coverage(package_name, importer, modname, ispkg, ignores)
        if coverage:
            coverages.append(coverage)
            summary += coverage

    summary.name = 'coverage'
    return coverages, summary


def summary(root_path, output, output_type, is_all, ignore_paths=None):
    """
    Args:
        root_path: Project path
        ignores:
        output:
        output_type:
        is_all:

    Returns:

    """
    coverages, summary = walk(root_path, ignore_paths)

    if is_all:
        for coverage in sorted(coverages, key=lambda x: x.name):
            report(coverage, output, output_type, is_all)

    report(summary, output, output_type, is_all)


def entry_point():
    parser = argparse.ArgumentParser()
    parser.add_argument("project_path", type=str)
    parser.add_argument("--output", dest='output', default='str', type=str,
                        help="[str,csv]")
    parser.add_argument("--ignore", dest='ignores', type=str, nargs='*',
                        help="Coverage of packages under <ignore> path is not aggregated.")

    parser.add_argument("--all", dest='all', action='store_true', default=False,
                        help="Print all module coverage")
    parser.add_argument("-m", "--module", dest='module', action='store_true',
                        default=False,
                        help="Print docstring coverage of modules.")
    parser.add_argument("-f", "--function", dest='function',
                        action='store_true', default=False,
                        help="Print docstring coverage of public functions.")
    parser.add_argument("-c", "--class", dest='klass', action='store_true',
                        default=False,
                        help="Print docstring coverage of classes.")

    args = parser.parse_args()

    output_type = []
    if args.klass:
        output_type.append(Type.CLASS)
    if args.module:
        output_type.append(Type.MODULE)
    if args.function or not output_type:
        output_type.append(Type.FUNCTION)

    summary(args.project_path, args.output, output_type, args.all, args.ignores)


if __name__ == '__main__':
    entry_point()
