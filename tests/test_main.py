from doccov.main import *


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


def doc_func():
    """has doc"""
    pass


def nodoc_func():
    """ """
    pass


def test_package_A():
    _, coverage = walk('tests/sample_project/package_A')
    assert coverage.counters[Type.FUNCTION.name].all == 1
    assert coverage.counters[Type.FUNCTION.name].true == 1
    assert coverage.counters[Type.MODULE.name].all == 1
    assert coverage.counters[Type.MODULE.name].true == 1
    assert coverage.counters[Type.CLASS.name].all == 0
    assert coverage.counters[Type.CLASS.name].true == 0


def test_package_B():
    _, coverage = walk('tests/sample_project/package_B')
    assert coverage.counters[Type.FUNCTION.name].all == 3
    assert coverage.counters[Type.FUNCTION.name].true == 1
    assert coverage.counters[Type.MODULE.name].all == 3
    assert coverage.counters[Type.MODULE.name].true == 0
    assert coverage.counters[Type.CLASS.name].all == 1
    assert coverage.counters[Type.CLASS.name].true == 1


def test_sample_project():
    _, coverage = walk('tests/sample_project')
    assert coverage.counters[Type.FUNCTION.name].all == 5
    assert coverage.counters[Type.FUNCTION.name].true == 3
    assert coverage.counters[Type.MODULE.name].all == 7
    assert coverage.counters[Type.MODULE.name].true == 3
    assert coverage.counters[Type.CLASS.name].all == 2
    assert coverage.counters[Type.CLASS.name].true == 2


def test_output_all_csv():
    summary('tests/sample_project', 'csv', [Type.FUNCTION], True)


def test_output_str():
    summary('tests/sample_project', 'str', [Type.FUNCTION, Type.MODULE, Type.CLASS], False)
