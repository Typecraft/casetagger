#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_casetagger
----------------------------------

Tests for `casetagger` module.
"""
import os

import casetagger.config as config
from casetagger.db import DbHandler
from casetagger.models import Cases, Case, CaseFromCounter


class TestDatabase(object):

    @classmethod
    def setup_class(cls):
        cls.db = DbHandler("test/test", False)

    def test_exists(self):
        db = DbHandler("test/exist", False)

        assert db is not None
        assert db.conn is not None
        assert os.path.isfile(db.db_path) is True

        db._destroy_database()

    def test_insert_case(self):
        case_1 = Case(config.CASE_TYPE_GLOSS_PREFIX_GLOSS, "from", "to")

        self.db.insert_case(case_1)
        # If no exception is thrown, we have succeeded, hurray!
        self.db._clear_database()

    def test_insert_unicode(self):
        case_1 = Case(config.CASE_TYPE_GLOSS_PREFIX_GLOSS, u"åøle", u"øÆEfEe")

        self.db.insert_case(case_1)

        case_fetched = self.db.get_case(config.CASE_TYPE_GLOSS_PREFIX_GLOSS, u"åøle", u"øÆEfEe")

        assert case_fetched == case_1

        self.db._clear_database()

    def test_get_case(self):
        case_1 = Case(config.CASE_TYPE_GLOSS_PREFIX_GLOSS, "from", "to")

        self.db.insert_case(case_1)

        case = self.db.get_case(config.CASE_TYPE_GLOSS_PREFIX_GLOSS, "from", "to")

        assert case.type == case_1.type
        assert case.case_from == case_1.case_from
        assert case.case_to == case_1.case_to

        self.db._clear_database()

    def test_insert_should_increment_case(self):
        case_1 = Case(config.CASE_TYPE_GLOSS_PREFIX_GLOSS, "from", "to")
        case_2 = Case(config.CASE_TYPE_GLOSS_PREFIX_GLOSS, "from", "to")

        self.db.insert_case(case_1)
        self.db.insert_case(case_2)

        case_fetched = self.db.get_case(config.CASE_TYPE_GLOSS_PREFIX_GLOSS, "from", "to")

        assert case_fetched is not None
        assert case_fetched.occurrences == 2

        self.db.insert_case(case_2)

        case_fetched = self.db.get_case(config.CASE_TYPE_GLOSS_PREFIX_GLOSS, "from", "to")
        assert case_fetched is not None
        assert case_fetched.occurrences == 3

        self.db._clear_database()

    def test_insert_case_should_increment_case_counter(self):
        case_1 = Case(config.CASE_TYPE_GLOSS_PREFIX_GLOSS, "from", "to_1")
        case_2 = Case(config.CASE_TYPE_GLOSS_PREFIX_GLOSS, "from", "to_2")
        case_3 = Case(config.CASE_TYPE_GLOSS_PREFIX_GLOSS, "from", "to_2")

        self.db.insert_case(case_1)
        self.db.insert_case(case_2)
        self.db.insert_case(case_3)

        case_counter = self.db.get_case_counter(config.CASE_TYPE_GLOSS_PREFIX_GLOSS, "from")

        assert case_counter is not None
        assert case_counter.occurrences == 3

        self.db._clear_database()

    def test_insert_case_counter(self):
        case_counter = CaseFromCounter(config.CASE_TYPE_GLOSS_PREFIX_GLOSS, "from")

        self.db.insert_case_counter(case_counter)
        self.db._clear_database()

    def test_insert_case_counter_should_increment(self):
        case_counter = CaseFromCounter(config.CASE_TYPE_GLOSS_PREFIX_GLOSS, "from")
        case_counter_2 = CaseFromCounter(config.CASE_TYPE_GLOSS_PREFIX_GLOSS, "from")

        self.db.insert_case_counter(case_counter)
        self.db.insert_case_counter(case_counter_2)

        case_counter_fetched = self.db.get_case_counter(config.CASE_TYPE_GLOSS_PREFIX_GLOSS, "from")

        assert case_counter_fetched is not None
        assert case_counter_fetched.occurrences == 2

        self.db._clear_database()

    def test_copy_from_db(self):
        db = DbHandler("test/copy_1", False)

        case = Case(config.CASE_TYPE_GLOSS_WORD, "from", "to")
        db.insert_case(case)

        db_2 = DbHandler("test/copy_2", True)

        case_2 = db.get_case(config.CASE_TYPE_GLOSS_WORD, "from", "to")
        assert case_2 is not None
        assert case_2.type == config.CASE_TYPE_GLOSS_WORD
        assert case_2.case_from == "from"
        assert case_2.case_to == "to"

        db._destroy_database()
        db_2._destroy_database()

    def test_get_all_to_cases(self):

        case_1 = Case(config.CASE_TYPE_GLOSS_PREFIX_GLOSS, "from", "to_1")
        case_2 = Case(config.CASE_TYPE_GLOSS_PREFIX_GLOSS, "from", "to_1")
        case_3 = Case(config.CASE_TYPE_GLOSS_PREFIX_GLOSS, "from", "to_1")
        case_4 = Case(config.CASE_TYPE_GLOSS_SUFFIX_MORPH, "from", "to_1")
        case_5 = Case(config.CASE_TYPE_POS_MORPHEME, "from", "to_1")
        case_6 = Case(config.CASE_TYPE_POS_MORPHEME, "from", "to_2")
        case_7 = Case(config.CASE_TYPE_GLOSS_PREFIX_GLOSS, "from", "to_3")

        self.db.insert_case(case_1)
        self.db.insert_case(case_2)
        self.db.insert_case(case_3)
        self.db.insert_case(case_4)
        self.db.insert_case(case_5)
        self.db.insert_case(case_6)
        self.db.insert_case(case_7)

        cases = Cases()
        cases.add_case(config.CASE_TYPE_GLOSS_PREFIX_GLOSS, "from", None)
        cases.add_case(config.CASE_TYPE_POS_MORPHEME, "from", None)

        # This should return all cases where case_from and type are equal
        # to either case_1 or case_2
        fetched = self.db.get_all_to_cases(cases)

        assert fetched is not None
        assert len(fetched) == 4

        self.db._clear_database()

    def test_clear_and_destroy_database(self):
        db = DbHandler("test/test_2", False)

        case_1 = Case(config.CASE_TYPE_GLOSS_PREFIX_GLOSS, "from", "to_1")
        db.insert_case(case_1)

        case = db.get_case(config.CASE_TYPE_GLOSS_PREFIX_GLOSS, "from", "to_1")

        assert case is not None

        db._clear_database()

        case_2 = db.get_case(config.CASE_TYPE_GLOSS_PREFIX_GLOSS, "from", "to_1")

        assert case_2 is None

        db._destroy_database()

        assert not os.path.isfile(db.db_path)

    @classmethod
    def teardown_class(cls):
        cls.db._destroy_database()
        pass

