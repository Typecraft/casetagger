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
from casetagger.models.db import Case, CaseFromCounter
from casetagger.models.extras import Cases


class TestCasetagger(object):

    @classmethod
    def setup_class(cls):
        cls.db = DbHandler("test/test", False)

    def test_exists(self):
        db = DbHandler("nno")

        assert db is not None

    def test_insert_case(self):
        case_1 = Case(type=config.CASE_TYPE_GLOSS_PREFIX_GLOSS, case_from="from", case_to="to")

        self.db.insert_case(case_1)
        case_fetched = self.db.get_case(1)

        assert case_fetched.type == config.CASE_TYPE_GLOSS_PREFIX_GLOSS
        assert case_fetched.case_from == "from"
        assert case_fetched.case_to == "to"

        self.db._clear_database()

    def test_insert_or_increment_case(self):
        case_1 = Case(type=config.CASE_TYPE_GLOSS_PREFIX_GLOSS, case_from="from", case_to="to")
        case_2 = Case(type=config.CASE_TYPE_GLOSS_PREFIX_GLOSS, case_from="from", case_to="to")

        self.db.insert_case(case_1)
        self.db.insert_or_increment_case(case_2)

        case_fetched = self.db.get_case(1)
        case_fetched_2 = self.db.get_case(2)

        assert case_fetched_2 is None
        assert case_fetched.occurrences == 2

        self.db._clear_database()

    def test_insert_case_counter(self):
        case_counter = CaseFromCounter(type=config.CASE_TYPE_GLOSS_PREFIX_GLOSS, case_from="from")

        self.db.insert_case_counter(case_counter)

        case_counter_fetched = self.db.get_case_counter(1)

        assert case_counter_fetched is not None
        assert case_counter_fetched.type == config.CASE_TYPE_GLOSS_PREFIX_GLOSS
        assert case_counter_fetched.case_from == "from"

        self.db._clear_database()

    def test_insert_or_increment_case_counter(self):
        case_counter = CaseFromCounter(type=config.CASE_TYPE_GLOSS_PREFIX_GLOSS, case_from="from")
        case_counter_2 = CaseFromCounter(type=config.CASE_TYPE_GLOSS_PREFIX_GLOSS, case_from="from")

        self.db.insert_case_counter(case_counter)
        self.db.insert_or_increment_case_counter(case_counter)

        case_counter_fetched = self.db.get_case_counter(1)
        case_counter_fetched_2 = self.db.get_case_counter(2)

        assert case_counter_fetched is not None
        assert case_counter_fetched_2 is None

        assert case_counter_fetched.occurrences == 2

    def test_insert_case_should_create_case_counter(self):
        pass

    def test_insert_or_increment_case_should_increment_counter(self):
        pass

    def test_copy_from_db(self):
        db = DbHandler("test/test_2", False)

        case = Case(type=config.CASE_TYPE_GLOSS_WORD, case_from="from", case_to="to")
        db.insert_case(case)

        db.close()

        db_2 = DbHandler("test/test_2", True)

        case_2 = db_2.get_case(1)
        assert case_2 is not None
        assert case_2.type == config.CASE_TYPE_GLOSS_WORD
        assert case_2.case_from == "from"
        assert case_2.case_to == "to"

        db._destroy_database()
        db_2._destroy_database()

    def test_fetch_all_to_cases(self):

        case_1 = Case(type=config.CASE_TYPE_GLOSS_PREFIX_GLOSS, case_from="from", case_to="to_1")
        case_2 = Case(type=config.CASE_TYPE_GLOSS_PREFIX_GLOSS, case_from="from", case_to="to_1")
        case_3 = Case(type=config.CASE_TYPE_GLOSS_PREFIX_GLOSS, case_from="from", case_to="to_1")
        case_4 = Case(type=config.CASE_TYPE_GLOSS_SUFFIX_MORPH, case_from="from", case_to="to_1")
        case_5 = Case(type=config.CASE_TYPE_POS_MORPHEME, case_from="from", case_to="to_1")
        case_6 = Case(type=config.CASE_TYPE_POS_MORPHEME, case_from="from", case_to="to_2")
        case_7 = Case(type=config.CASE_TYPE_GLOSS_PREFIX_GLOSS, case_from="from", case_to="to_3")

        self.db.insert_or_increment_case(case_1)
        self.db.insert_or_increment_case(case_2)
        self.db.insert_or_increment_case(case_3)
        self.db.insert_or_increment_case(case_5)
        self.db.insert_or_increment_case(case_6)
        self.db.insert_or_increment_case(case_7)

        cases = Cases()
        cases.add_case(config.CASE_TYPE_GLOSS_PREFIX_GLOSS, "from", None)
        cases.add_case(config.CASE_TYPE_POS_MORPHEME, "from", None)

        # This should return all cases where case_from and type are equal
        # to either case_1 or case_2
        fetched = self.db.fetch_all_to_cases(cases)

        assert fetched is not None
        assert len(fetched) == 4
        for f in fetched:
            print("")
            print("%s, %s: %f" % (f.type, f.case_to, f.prob))

        self.db._clear_database()

    def test_clear_and_destroy_database(self):
        db = DbHandler("test/test_2", False)

        case_1 = Case(type=config.CASE_TYPE_GLOSS_PREFIX_GLOSS, case_from="from", case_to="to_1")
        db.insert_case(case_1)

        case = db.get_case(1)

        assert case is not None

        db._clear_database()

        case_2 = db.get_case(1)

        assert case_2 is None

        db._destroy_database()

        assert not os.path.isfile(db.db_path)

    def test_populate_probabilities(self):

        case_1 = Case(type=config.CASE_TYPE_GLOSS_PREFIX_GLOSS, case_from="from", case_to="to_1")
        self.db.insert_case(case_1)


    @classmethod
    def teardown_class(cls):
        cls.db._destroy_database()
