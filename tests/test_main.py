from doccov.main import *

sys.path.insert(0, '.')


def doc_func():
    """has doc"""
    pass


def nodoc_func():
    """ """
    pass


class SampleClass():
    """
    Short class summary.

    .....
    """

    def __init__(self):
        """init"""
        pass

    def doc_func(self):
        """
        Class func
        """
        pass

    def no_doc_func(self):
        pass


def test_count_class():
    coverage = count_class(SampleClass)

    assert coverage.counters[Type.FUNCTION.name].true == 2
    assert coverage.counters[Type.FUNCTION.name].all == 3
    assert coverage.counters[Type.CLASS.name].true == 1
    assert coverage.counters[Type.CLASS.name].all == 1


def test_count_module():
    from .sample_project import module_fulldoc
    coverage = count_module(module_fulldoc)
    assert coverage.counters[Type.FUNCTION.name].true == 3
    assert coverage.counters[Type.FUNCTION.name].all == 4
    assert coverage.counters[Type.CLASS.name].true == 1
    assert coverage.counters[Type.CLASS.name].all == 1


def test_count_module_package():
    from .sample_project import package_A
    coverage = count_module(package_A)
    assert coverage.counters[Type.FUNCTION.name].true == 0
    assert coverage.counters[Type.FUNCTION.name].all == 0
    assert coverage.counters[Type.CLASS.name].true == 0
    assert coverage.counters[Type.CLASS.name].all == 0
    assert coverage.counters[Type.MODULE.name].true == 1
    assert coverage.counters[Type.MODULE.name].all == 1


def test_count_module_package():
    from .sample_project.package_A import module_fulldoc
    coverage = count_module(module_fulldoc)
    assert coverage.counters[Type.FUNCTION.name].true == 1
    assert coverage.counters[Type.FUNCTION.name].all == 1
    assert coverage.counters[Type.CLASS.name].true == 0
    assert coverage.counters[Type.CLASS.name].all == 0
    assert coverage.counters[Type.MODULE.name].true == 1
    assert coverage.counters[Type.MODULE.name].all == 1


def test_counter():
    a = Counter(1, 1)
    b = Counter(5, 3)
    target = a + b
    expected = Counter(6, 4)

    assert target == expected


def test_coverage():
    a = Coverage()
    a.add(doc_func, Type.FUNCTION)
    a.add(nodoc_func, Type.FUNCTION)

    b = Coverage()
    b.add(doc_func, Type.FUNCTION)

    target = a + b
    counter = target.counters[Type.FUNCTION.name]

    assert counter.all == 3
    assert counter.true == 2


def test_sample_project():
    _, coverage = walk('tests/sample_project')
    report(coverage, 'str', [Type.FUNCTION, Type.CLASS, Type.MODULE], False)

    assert coverage.counters[Type.FUNCTION.name].true == 4
    assert coverage.counters[Type.FUNCTION.name].all == 7
    assert coverage.counters[Type.CLASS.name].true == 1
    assert coverage.counters[Type.CLASS.name].all == 1
    assert coverage.counters[Type.MODULE.name].true == 3
    assert coverage.counters[Type.MODULE.name].all == 6


def test_output_all_csv():
    summary('tests/sample_project', 'csv', [Type.FUNCTION], True)


def test_output_str():
    summary('tests/sample_project', 'str',
            [Type.FUNCTION, Type.MODULE, Type.CLASS], False)


def test_ignore_path():
    _, coverage = walk('tests/sample_project', ['tests/sample_project/package_A'])
    assert coverage.counters[Type.FUNCTION.name].true == 3
    assert coverage.counters[Type.FUNCTION.name].all == 6
    assert coverage.counters[Type.CLASS.name].true == 1
    assert coverage.counters[Type.CLASS.name].all == 1
    assert coverage.counters[Type.MODULE.name].true == 1
    assert coverage.counters[Type.MODULE.name].all == 4


def test_ignore_path_tree():
    _, coverage = walk('tests/sample_project', ['tests/sample_project/package_B'])
    report(coverage, 'str', [Type.FUNCTION, Type.CLASS, Type.MODULE], False)
    assert coverage.counters[Type.FUNCTION.name].true == 4
    assert coverage.counters[Type.FUNCTION.name].all == 5
    assert coverage.counters[Type.CLASS.name].true == 1
    assert coverage.counters[Type.CLASS.name].all == 1
    assert coverage.counters[Type.MODULE.name].true == 3
    assert coverage.counters[Type.MODULE.name].all == 3
