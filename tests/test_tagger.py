# coding=utf-8

from tc_xml_python.models.text import Text
from tc_xml_python.models.phrase import Phrase
from tc_xml_python.models.word import Word
from tc_xml_python.models.morpheme import Morpheme

import random

words = ["Hei", "dette", "er", u"gøy", "og", "veldig", "morsomt", "la", "oss", "leke"]
pos = ["N", "V", "NMASC", "PREP", "ADJ", "CARD"]

class TestTagger(object):

    @classmethod
    def setup_class(cls):
        # Create a simple test-text for us

        bulk_text = Text()

        # Create 100 phrases
        for i in range(0, 100):
            phrase_word_count = random.randint(len(words))
            selected_words = random.sample(words, phrase_word_count)

            phrase = " ".join(selected_words)
            phrase_obj = Phrase()
            phrase_obj.phrase = phrase

            for word in selected_words:
                word_obj = Word()
                word_obj.word = word
                word_obj.pos = random.choice(pos)

                phrase_obj.add_word(word_obj)

            bulk_text.add_phrase(phrase_obj)

        detail_text = Text()

        pass
