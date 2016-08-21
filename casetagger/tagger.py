# -*- coding: utf-8 -*-

import casetagger.config as config
from casetagger.db import DbHandler
from casetagger.models import WordCases, MorphemeCases
from tc_xml_python.models import Text


class CaseTagger:
    """
    This is the class that does the primary work-load.
    """

    def __init__(self):
        pass

    @classmethod
    def instantiate_db(cls, language):
        """
        Instantiates a database for a given language as the 'current db'.

        We use this method to avoid having to create the database connection
        'every time' we want to do something.

        :param language:
        :return:
        """
        cls.db = DbHandler(language, config.USE_MEMORY_DB)

    @classmethod
    def train(cls, text):
        """
        Trains the database specified by a text
        :param text:
        :return:
        """
        if not isinstance(text, Text):
            raise Exception("Invalid argument to tag_text, expected tc_xml_python.models.text.Text object")

        language = text.language

        if cls.db is not None:
            db = cls.db
        else:
            db = DbHandler(language, config.USE_MEMORY_DB)

        for phrase in text.phrases:
            for word in phrase.words:

                # If we don't have an option to ignore words with empty poses
                if not (word.pos is None and not config.REGISTER_EMPTY_POS):
                    word_cases = WordCases(word, phrase)
                    db.insert_cases(word_cases)

                for morpheme in word.morphemes:

                    # If we don't want to ignore empty glosses
                    if not (len(morpheme.glosses) == 0 and not config.REGISTER_EMPTY_GLOSS):
                        morpheme_cases = MorphemeCases(morpheme, word, phrase)

                        db.insert_cases(morpheme_cases)

    @classmethod
    def tag_text(cls, text):
        """
        Tags a text.

        :param text:
        :return:
        """
        if not isinstance(text, Text):
            raise Exception("Invalid argument to tag_text, expected tc_xml_python.models.text.Text object")

        language = text.language

        db = None
        if cls.db is not None:
            db = cls.db
        else:
            db = DbHandler(language, config.USE_MEMORY_DB)

        for i in range(config.NUMBER_OF_PASSES):
            for phrase in text.phrases:
                for word in phrase.words:
                    word_cases = WordCases(word, phrase)

                    # Fetches all cases matching the type and case_from of the ones we have
                    word_cases = db.get_all_to_cases(word_cases)

                    most_likely_pos = word_cases.merge()
                    print(most_likely_pos)

                    word.pos = most_likely_pos

                    for morpheme in word.morphemes:
                        morpheme_cases = MorphemeCases(morpheme, word, phrase)

                        morpheme_cases = db.get_all_to_cases(morpheme_cases)

                        most_likely_gloss = morpheme_cases.merge()
                        morpheme.glosses = most_likely_gloss.split(".")

