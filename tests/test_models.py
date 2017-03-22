from casetagger import config
from casetagger.models import Cases, Case, CaseFromCounter, Morpheme


def test_create_case():
    pass


def test_create_tuples():
    cases = Cases()

    cases.add_case(1, "a", "b")
    cases.add_case(4, "c", "b")
    cases.add_case(16, "c", "b")

    cases.create_tuple_cases()

    case_instances = cases.cases

    for case in case_instances:
        print(str(case))

    assert Case(1, "a", "b") in case_instances
    assert Case(4, "c", "b") in case_instances
    assert Case(16, "c", "b") in case_instances
    assert Case(5, "a@c", "b") in case_instances
    assert Case(17, "a@c", "b") in case_instances
    assert Case(20, "c@c", "b") not in case_instances  # As they are in the same group


def test_get_case_types():
    case_1 = Case(1 | 4 | 32 | 128, "a", "b")

    types = case_1.get_case_types()

    assert 1 in types
    assert 4 in types
    assert 32 in types
    assert 128 in types
    assert 2 not in types
    assert 16 not in types


def test_cases_combine_similar():
    cases = Cases()
    cases.add_case(1, "a", "a", 0, 0.5)
    cases.add_case(2, "a", "b", 0, 0.8)
    cases.add_case(8, "a", "b", 0, 0.2)
    cases.add_case(16, "a", "d", 0, 0.8)
    cases.add_case(4, "a", "c", 0, 0.45)
    cases.add_case(2, "a", "c", 0, 0.65)

    combined = cases.combine_similar_cases(cases.cases)

    for case in combined:
        print(case)


def test_case_str():
    case = Case(1, "from", "to")
    assert "1" in case.__str__()
    assert "from" in case.__str__()
    assert "to" in case.__str__()


def test_case_unicode_same_as_str():
    case = Case(1, "from", "to")

    assert case.__str__() == case.__unicode__()


def test_case_from_str():
    case_from_counter = CaseFromCounter(1, "from")
    assert "1" in case_from_counter.__str__()
