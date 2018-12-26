import argparse
import enum
import importlib
import inspect
import pkgutil
import pydoc
import sys


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

        return Coverage(counters=merge)

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

    classes, cdict = [], {}
    for key, value in inspect.getmembers(object, inspect.isclass):
        # if __all__ exists, believe it.  Otherwise use old heuristic.
        if (all is not None or
                (inspect.getmodule(value) or object) is object):
            if pydoc.visiblename(key, all, object):
                classes.append((key, value))
                cdict[key] = cdict[value] = '#' + key
    for key, value in classes:
        for base in value.__bases__:
            key, modname = base.__name__, base.__module__
            module = sys.modules.get(modname)
            if modname != name and module and hasattr(module, key):
                if getattr(module, key) is base:
                    if not key in cdict:
                        cdict[key] = cdict[base] = modname + '.html#' + key

    funcs, fdict = [], {}
    for key, value in inspect.getmembers(object, inspect.isroutine):
        # if __all__ exists, believe it.  Otherwise use old heuristic.
        if (all is not None or
                inspect.isbuiltin(value) or inspect.getmodule(value) is object):
            if pydoc.visiblename(key, all, object):
                funcs.append((key, value))
                fdict[key] = '#-' + key
                if inspect.isfunction(value): fdict[value] = fdict[key]

    coverage = Coverage(name=name)

    coverage.add(object, Type.MODULE)
    for _, obj in classes:
        coverage.add(obj, Type.CLASS)

    for _, obj in funcs:
        coverage.add(obj, Type.FUNCTION)

    return coverage


def walk(root_path):
    """
    Count coverage of root_path tree.

    Under ignores files is not counted.

    Args:
        root_path(str): Start path.

    Returns:
        [Coverage], Coverage: Return all module coverage and summary.
    """

    sys.path.insert(0, root_path)
    packages = pkgutil.walk_packages([root_path])

    coverages = []
    summary = Coverage()
    for importer, modname, ispkg in packages:
        spec = pkgutil._get_spec(importer, modname)

        object = importlib._bootstrap._load(spec)
        counter = count_module(object)

        coverages.append(counter)
        summary += counter

    summary.name = 'coverage'
    return coverages, summary


def summary(root_path, output, output_type, is_all):
    """
    Args:
        root_path: Project path
        ignores:
        output:
        output_type:
        is_all:

    Returns:

    """
    coverages, summary = walk(root_path)

    if is_all:
        for coverage in coverages:
            report(coverage, output, output_type, is_all)

    report(summary, output, output_type, is_all)


def entry_point():
    parser = argparse.ArgumentParser()
    parser.add_argument("project_path", type=str)
    parser.add_argument("--output", dest='output', default='str', type=str,
                        help="[str,csv]")
    parser.add_argument("--all", dest='all', action='store_true', default=False,
                        help="Print all module coverage")
    parser.add_argument("-m", "--module", dest='module', action='store_true', default=False,
                        help="Print docstring coverage of modules.")
    parser.add_argument("-f", "--function", dest='function', action='store_true', default=False,
                        help="Print docstring coverage of public functions.")
    parser.add_argument("-c", "--class", dest='klass', action='store_true', default=False,
                        help="Print docstring coverage of classes.")

    args = parser.parse_args()

    output_type = []
    if args.klass:
        output_type.append(Type.CLASS)
    if args.module:
        output_type.append(Type.MODULE)
    if args.function or not output_type:
        output_type.append(Type.FUNCTION)

    summary(args.project_path, args.output, output_type, args.all)


if __name__ == '__main__':
    entry_point()
