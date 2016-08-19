from casetagger.models.db import Case, CaseRelation, CaseFromCounter
from tc_xml_python.models.morpheme import Morpheme


def copy_case(c):
    return Case(id=c.id, type=c.type, case_to=c.case_to, case_from=c.case_from, occurrences=c.occurrences)


def copy_case_relation(cr):
    return CaseRelation(case_1=cr.case_1, case2=cr.case_2)


def copy_case_from_counter(cfc):
    return CaseFromCounter(id=cfc.id, type=cfc.type, case_from=cfc.case_from, occurrences=cfc.occurrences)


def case_to_case_from_counter(c):
    return CaseFromCounter(type=c.type, case_from=c.case_from)


def get_glosses_concatenated(morpheme):
    assert isinstance(morpheme, Morpheme)

    return ".".join(sorted(morpheme.glosses))
