from casetagger.config import BASE_DIR
from casetagger.models import Case, CaseFromCounter, Cases

import sqlite3
import os

from casetagger.res.db import DB_INIT


def create_db_path(language):
    return BASE_DIR + '/db/' + language + '_db.db'


class DbHandler:
    """
    Class that takes care of all database-interacton
    """

    def __init__(self, language, use_memory=False):
        self.db_path = create_db_path(language)
        self.memory = use_memory

        if not use_memory:
            self.conn = sqlite3.connect(self.db_path)
            self.init()
        else:
            self.conn = sqlite3.connect(':memory:')
            self.init()
            self.copy_from_db(language)

    def init(self):
        """
        Sets up the database
        :return:
        """
        cursor = self.conn.cursor()
        cursor.executescript(DB_INIT)
        self.conn.commit()

    def copy_from_db(self, language):
        other_db = DbHandler(language, False)
        cases = other_db.get_all_cases()
        self.insert_cases(cases)

    def get_case(self, case_type, case_from, case_to):
        res = self.conn.execute('''
            SELECT * FROM cases WHERE type=? AND case_from=? AND case_to=?''',
                             (case_type, case_from, case_to)).fetchone()

        return DbHandler._row_to_case(res)

    def get_cases_by_from(self, case_type, case_from):
        res = self.conn.execute('''
            SELECT * FROM cases WHERE type=? AND case_from=?''',
                                (case_type, case_from)).fetchall()

        return DbHandler._rows_to_case(res)

    def get_case_counter(self, case_type, case_from):
        res = self.conn.execute('''
            SELECT * FROM cases_from_counter WHERE type=? AND case_from=?''',
                                (case_type, case_from)).fetchone()

        return DbHandler._row_to_case_counter(res)

    def get_all_cases(self):
        res = self.conn.execute('''
            SELECT * FROM cases''').fetchall()

        return DbHandler._rows_to_case(res)

    def get_all_case_counters(self):
        res = self.conn.execute('''
            SELECT * FROM cases_from_counter''').fetchall()

        return DbHandler._rows_to_case_counters(res)

    def insert_case(self, case, cursor=None):
        assert isinstance(case, Case)

        should_commit = cursor is None

        if cursor is None:
            cursor = self.conn.cursor()

        cursor.execute('''
            INSERT OR IGNORE INTO cases(type, case_from, case_to, occurrences) VALUES (?,?,?,?)''',
                       (case.type, case.case_from, case.case_to, 0))

        cursor.execute('''
            UPDATE cases SET occurrences = occurrences + 1 WHERE type=? AND case_from=? AND case_to=?;''',
                       (case.type, case.case_from, case.case_to))

        self.insert_case_counter(case, cursor)

        if should_commit:
            self.conn.commit()

    def insert_cases(self, cases, cursor=None):
        should_commit = cursor is None

        if cursor is None:
            cursor = self.conn.cursor()

        for case in cases:
            self.insert_case(case, cursor)

        if should_commit:
            self.conn.commit()

    def insert_case_counter(self, case_counter, cursor=None):
        assert isinstance(case_counter, CaseFromCounter) or isinstance(case_counter, Case)

        should_commit = cursor is None

        if cursor is None:
            cursor = self.conn.cursor()

        cursor.execute('''
            INSERT OR IGNORE INTO cases_from_counter(type, case_from, occurrences) VALUES (?,?,?)''',
                       (case_counter.type, case_counter.case_from, 0))

        cursor.execute('''
            UPDATE cases_from_counter SET occurrences = occurrences + 1 WHERE type=? AND case_from=?''',
                       (case_counter.type, case_counter.case_from))

        if should_commit:
            self.conn.commit()

    def get_all_to_cases(self, cases):
        """
        Takes a set of cases, assumed to contain only cases populated with the type and case_from fields,
        and fetches all cases that match these two columns.

        :param cases:
        :return:
        """
        assert isinstance(cases, Cases)

        new_cases = []
        for case in cases:
            new_cases.extend(self.get_cases_by_from(case.type, case.case_from))

        cases_obj = Cases()
        cases_obj.add_all_cases(new_cases)
        self.populate_probabilities(cases_obj)

        return cases_obj

    def populate_probabilities(self, cases):
        """
        Populates a probability set.

        :param cases:
        :return:
        """
        if not isinstance(cases, Cases):
            raise Exception("Wrong argument to populate_probabilities, expected Cases object")

        from_case_set = set(map(lambda c: (c.type, c.case_from), cases))
        fetched_from_cases = {}  # Dictionary for easy retrieval later
        hash_name = lambda fc: str(fc.type) + fc.case_from  # Lambda for generating hash-name from case_from

        for from_case in from_case_set:
            fetched_from_case = self.get_case_counter(from_case[0], from_case[1])

            assert fetched_from_case is not None

            fetched_from_cases[hash_name(fetched_from_case)] = fetched_from_case

        # Calculate probabilities
        for case in cases:
            from_case = fetched_from_cases[hash_name(case)]
            prob = float(case.occurrences) / float(from_case.occurrences)
            case.prob = prob

    def _clear_database(self):
        self.conn.execute("DELETE FROM cases")
        self.conn.execute("DELETE FROM cases_from_counter")
        self.conn.commit()

    def _destroy_database(self):
        self._clear_database()

        if not self.memory:
            os.remove(self.db_path)

    @staticmethod
    def _row_to_case_counter(row):
        if row is None:
            return None

        return CaseFromCounter(row[1], row[2], row[3])

    @staticmethod
    def _rows_to_case_counters(rows):
        if rows is None:
            return []

        return map(lambda row: DbHandler._row_to_case_counter(row), rows)

    @staticmethod
    def _row_to_case(row):
        if row is None:
            return None

        return Case(row[1], row[2], row[3], row[4])

    @staticmethod
    def _rows_to_case(rows):
        if rows is None:
            return []

        return map(lambda row: DbHandler._row_to_case(row), rows)
