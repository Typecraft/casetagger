#!/usr/bin/env python
# -*- coding: utf-8 -*-

from casetagger.models.util import get_glosses_concatenated
from tc_xml_python.models.morpheme import Morpheme


class TestUtil(object):

    @classmethod
    def setup_class(cls):
        pass

    def test_get_morphemes_concatenated(self):
        morpheme = Morpheme()

        morpheme.glosses.append("1SG")
        morpheme.glosses.append("3SG")
        morpheme.glosses.append("2SG")

        concatted = get_glosses_concatenated(morpheme)
        assert concatted == "1SG.2SG.3SG"
