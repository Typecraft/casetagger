# -*- coding: utf-8 -*-

from tc_xml_python.models.phrase import Phrase
from tc_xml_python.models.text import Text

import casetagger.config as config

from casetagger.models.db import Case, CaseFromCounter, CaseRelation
from casetagger.models.extras import WordTargetCases, Cases, MorphemeTargetCases
from casetagger.db import DbHandler


class CaseTagger:
    """
    This is the class that does the primary work-load.
    """

    def __init__(self):
        pass

    @staticmethod
    def tag_text(text):
        """
        Tags a text.

        :param text:
        :return:
        """
        if not isinstance(text, Text):
            raise Exception("Invalid argument to tag_text, expected tc_xml_python.models.text.Text object")

        language = text.language

        db = DbHandler(language, config.USE_MEMORY_DB)

        for i in range(config.NUMBER_OF_PASSES):
            for phrase in text.phrases:
                for word in phrase.words:
                    word_cases = WordTargetCases(word, phrase)
                    db.fetch_all_to_cases(word, word_cases)

                    most_likely_pos = word_cases.merge()

                    word.pos = most_likely_pos

                    for morpheme in word.morphemes:
                        morpheme_cases = MorphemeTargetCases(morpheme, word, phrase)

                        db.fetch_all_to_cases(morpheme, morpheme_cases)

                        most_likely_gloss = morpheme_cases.merge()
                        morpheme.glosses = most_likely_gloss.split(".")
