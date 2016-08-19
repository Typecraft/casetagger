#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tc_xml_python.models.text import Text
from tc_xml_python.models.phrase import Phrase
from tc_xml_python.models.word import Word
from tc_xml_python.models.morpheme import Morpheme

from casetagger.tagger import CaseTagger
from casetagger.models.db import Case

import random

words = ["Hei", "dette", "er", u"gøy", "og", "veldig", "morsomt", "la", "oss", "leke"]
pos = ["N", "V", "NMASC", "PREP", "ADJ", "CARD"]


class TestTagger(object):

    @classmethod
    def setup_class(cls):
        # Create a simple test-text for us

        cls.bulk_text = Text()

        # Create 100 phrases
        for i in range(0, 100):
            phrase_word_count = random.randint(0, len(words))
            selected_words = random.sample(words, phrase_word_count)

            phrase = " ".join(selected_words)
            phrase_obj = Phrase()
            phrase_obj.phrase = phrase

            for word in selected_words:
                word_obj = Word()
                word_obj.word = word
                word_obj.pos = random.choice(pos)

                phrase_obj.add_word(word_obj)

            cls.bulk_text.add_phrase(phrase_obj)

        cls.detail_text = Text()

        phrase_1 = Phrase()
        phrase_1.phrase = "These are my phrases"

        word_1 = Word()
        word_2 = Word()
        word_3 = Word()
        word_4 = Word()

        word_1.word = "These"
        word_2.word = "are"
        word_3.word = "my"
        word_4.word = "phrases"

        word_1.pos = "DET"
        word_2.pos = "V"
        word_3.pos = "PRON"
        word_4.pos = "N"

        morpheme_1 = Morpheme()
        morpheme_2 = Morpheme()
        morpheme_3 = Morpheme()
        morpheme_4 = Morpheme()
        morpheme_5 = Morpheme()

        morpheme_1.morpheme = "These"
        morpheme_2.morpheme = "are"
        morpheme_3.morpheme = "my"
        morpheme_4.morpheme = "phrase"
        morpheme_5.morpheme = "s"

        morpheme_1.glosses = ["POSS"]
        morpheme_2.glosses = ["ERG"]
        morpheme_3.glosses = ["AD"]
        morpheme_4.glosses = ["AD"]
        morpheme_5.glosses = ["AUX"]

        word_1.add_morpheme(morpheme_1)
        word_2.add_morpheme(morpheme_2)
        word_3.add_morpheme(morpheme_3)
        word_4.add_morpheme(morpheme_4)

        phrase_1.add_word(word_1)
        phrase_1.add_word(word_2)
        phrase_1.add_word(word_3)
        phrase_1.add_word(word_4)

        cls.detail_text.add_phrase(phrase_1)

    def test_train(self):
        CaseTagger.instantiate_db("test")
        CaseTagger.train(self.detail_text)

        session = CaseTagger.db.db_factory()

        results = session.query(Case).all()

        assert len(results) > 0

        #for result in results:
        #    print(result)

        CaseTagger.db._clear_database()

    def test_tag_simple_text(self):
        CaseTagger.instantiate_db("test")
        CaseTagger.train(self.detail_text)
        CaseTagger.db._clear_database()

        phrase = Phrase()
        phrase.phrase = "This is a phrase"

        word_1 = Word()
        word_2 = Word()
        word_3 = Word()
        word_4 = Word()

        word_1.word = "This"
        word_2.word = "is"
        word_3.word = "a"
        word_4.word = "phrase"

        phrase.add_word(word_1)
        phrase.add_word(word_2)
        phrase.add_word(word_3)
        phrase.add_word(word_4)

        text = Text()
        text.add_phrase(phrase)

        CaseTagger.tag_text(text)

        for phrase in text.phrases:
            for word in phrase.words:
                print(word.word + ": " + word.pos)

    @classmethod
    def teardown_class(cls):
        CaseTagger.db._destroy_database()

