#!/usr/bin/env python
# -*- coding: utf-8 -*-

from casetagger.util import get_glosses_concatenated, separate_texts_by_languages, get_text_words, get_text_morphemes
from tc_xml_python.models import Text, Morpheme, Phrase, Word


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

    def test_get_text_words(self):
        text = Text()
        phrase = Phrase()
        phrase_1 = Phrase()
        word_1 = Word()
        word_2 = Word()
        word_3 = Word()
        word_4 = Word()

        phrase.add_word(word_1)
        phrase.add_word(word_2)
        phrase.add_word(word_3)
        phrase_1.add_word(word_4)

        text.add_phrase(phrase)
        text.add_phrase(phrase_1)

        words = get_text_words(text)

        assert word_1 in words
        assert word_2 in words
        assert word_3 in words
        assert word_4 in words

    def test_get_text_morphemes(self):
        text = Text()
        phrase_1 = Phrase()
        phrase_2 = Phrase()
        word_1 = Word()
        word_2 = Word()
        word_3 = Word()
        morpheme_1 = Morpheme()
        morpheme_2 = Morpheme()
        morpheme_3 = Morpheme()
        morpheme_4 = Morpheme()
        morpheme_5 = Morpheme()

        phrase_1.add_word(word_1)
        phrase_2.add_word(word_2)
        phrase_2.add_word(word_3)

        word_1.add_morpheme(morpheme_1)
        word_1.add_morpheme(morpheme_2)
        word_2.add_morpheme(morpheme_3)
        word_2.add_morpheme(morpheme_4)
        word_3.add_morpheme(morpheme_5)

        text.add_phrase(phrase_1)
        text.add_phrase(phrase_2)

        morphemes = get_text_morphemes(text)

        assert morpheme_1 in morphemes
        assert morpheme_2 in morphemes
        assert morpheme_3 in morphemes
        assert morpheme_4 in morphemes
        assert morpheme_5 in morphemes

