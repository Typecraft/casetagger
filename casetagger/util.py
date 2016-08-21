from tc_xml_python.models import Morpheme


def get_glosses_concatenated(morpheme):
    assert isinstance(morpheme, Morpheme)

    return ".".join(sorted(morpheme.glosses))
