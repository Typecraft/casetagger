# -*- coding: utf-8 -*-
import copy

from casetagger.config import config
from casetagger import logger
from casetagger.db import DbHandler
from casetagger.models import WordCases, MorphemeCases, TestResult
from typecraft_python.models import Text


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
        cls.db = DbHandler(language, config['use_memory_db'])

    @classmethod
    def train(cls, text):
        """
        Trains the database specified by a text
        :param text:
        :return:
        """
        if not isinstance(text, Text):
            raise Exception("Invalid argument to tag_text, expected typecraft_python.models.text.Text object")

        language = text.language

        if cls.db is not None:
            db = cls.db
        else:
            db = DbHandler(language, config['use_memory_db'])

        # Used for debug only
        phrase_len = len(text.phrases)
        i = 0

        for phrase in text.phrases:

            cursor = db.conn.cursor()

            i += 1

            if i % 100:
                db.conn.commit()

            logger.debug("Training with phrase " + str(i) + "/" + str(phrase_len) + "\r")
            for word in phrase.words:

                # If we don't have an option to ignore words with empty poses
                if not (word.pos is None and word.pos is not "" and not config['register_empty_pos']):
                    word_cases = WordCases(word, phrase)
                    db.insert_cases(word_cases, cursor)

                for morpheme in word.morphemes:
                    # If we don't want to ignore empty glosses
                    if not (len(morpheme.glosses) == 0 and not config['register_empty_gloss']):
                        morpheme_cases = MorphemeCases(morpheme, word, phrase)

                        db.insert_cases(morpheme_cases, cursor)

            db.conn.commit()

    @classmethod
    def tag_text(cls, text):
        """
        Tags a text.

        :param text:
        :return:
        """
        if not isinstance(text, Text):
            raise Exception("Invalid argument to tag_text, expected typecraft_python.models.text.Text object")

        language = text.language

        db = None
        if cls.db is not None:
            db = cls.db
        else:
            db = DbHandler(language, config['use_memory_db'])

        for i in range(config['number_of_passes']):
            for phrase in text.phrases:
                for word in phrase.words:
                    word_cases = WordCases(word, phrase)

                    # Fetches all cases matching the type and case_from of the ones we have
                    word_cases = db.get_all_to_cases(word_cases)

                    most_likely_pos = word_cases.merge()

                    word.pos = most_likely_pos

                    for morpheme in word.morphemes:
                        morpheme_cases = MorphemeCases(morpheme, word, phrase)

                        morpheme_cases = db.get_all_to_cases(morpheme_cases)

                        most_likely_gloss = morpheme_cases.merge()
                        morpheme.glosses = most_likely_gloss.split(".")

    @classmethod
    def test_text(cls, text):
        if not isinstance(text, Text):
            raise Exception

        copied_text = copy.deepcopy(text)

        CaseTagger.tag_text(text)

        return TestResult.from_data(copied_text, text)




