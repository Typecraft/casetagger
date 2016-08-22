#!/usr/bin/env python
# -*- coding: utf-8 -*-

from casetagger.util import get_glosses_concatenated, separate_texts_by_languages
from tc_xml_python.models import Text, Morpheme


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

    def test_separate_texts_by_language(self):
        text_1 = Text()
        text_2 = Text()
        text_3 = Text()
        text_4 = Text()
        text_5 = Text()

        text_1.language = "nno"
        text_2.language = "eng"
        text_3.language = "eng"
        text_4.language = "kri"
        text_5.language = "nno"

        texts = [text_1, text_2, text_3, text_4, text_5]

        separated = separate_texts_by_languages(texts)

        assert isinstance(separated, dict)
        assert "nno" in separated
        assert "eng" in separated
        assert "kri" in separated

        assert isinstance(separated["nno"], list)
        assert isinstance(separated["eng"], list)
        assert isinstance(separated["kri"], list)

        assert text_1 in separated["nno"]
        assert text_2 in separated["eng"]
        assert text_3 in separated["eng"]
        assert text_4 in separated["kri"]
        assert text_5 in separated["nno"]
