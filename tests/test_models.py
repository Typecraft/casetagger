from casetagger.models import Cases, Case


class TestModels(object):

    @classmethod
    def setup_class(cls):
        pass

    def test_create_case(self):
        pass

    def test_create_tuples(self):
        cases = Cases()

        cases.add_case(1, "a", "b")
        cases.add_case(4, "c", "b")
        cases.add_case(16, "c", "b")

        cases.create_tuple_cases()

        case_instances = cases.cases

        assert Case(1, "a", "b") in case_instances
        assert Case(4, "c", "b") in case_instances
        assert Case(16, "c", "b") in case_instances
        assert Case(5, "ac", "b") in case_instances
        assert Case(17, "ac", "b") in case_instances
        assert Case(20, "cc", "b") in case_instances

