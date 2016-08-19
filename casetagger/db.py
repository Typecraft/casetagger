import os
import copy

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from casetagger.config import BASE_DIR
from casetagger.models.db import Base, Case, CaseRelation, CaseFromCounter
from casetagger.models.extras import Cases
from casetagger.models.util import copy_case, copy_case_from_counter, copy_case_relation, case_to_case_from_counter


def create_db_path(language):
    return BASE_DIR + '/db/' + language + '_db.db'


class DbHandler:
    """
    Class that takes care of all database-interacton
    """

    def __init__(self, language, use_memory=False):
        """
        Inits a new DbHandler on a specific language
        :param language:
        """
        self.language = language
        self.db_path = create_db_path(language)
        self.use_memory = use_memory

        if use_memory:
            self.engine = create_engine('sqlite://')
            Base.metadata.create_all(self.engine)

            self.copy_from_db(create_db_path(language))
        else:
            db_path = create_db_path(language)

            self.engine = create_engine('sqlite:////' + db_path)
            Base.metadata.create_all(self.engine)

        self.db_factory = sessionmaker(bind=self.engine)

    def close(self):
        self.engine.dispose()

    def copy_from_db(self, db_url):
        """
        Loads a database into the current database.

        :param db_url:
        :param language:
        :return:
        """
        from_engine = create_engine('sqlite:////' + db_url)
        from_session = sessionmaker(bind=from_engine)()
        to_session = sessionmaker(bind=self.engine)()

        cases = from_session.query(Case).all()
        case_relations = from_session.query(CaseRelation).all()
        case_counters = from_session.query(CaseFromCounter).all()

        cases = map(lambda x: copy_case(x), cases)
        case_relations = map(lambda x: copy_case(x), case_relations)
        case_counters = map(lambda x: copy_case(x), case_counters)

        to_session.add_all(cases)
        to_session.add_all(case_relations)
        to_session.add_all(case_counters)

        to_session.commit()

        to_session.close()
        from_session.close()

    def insert_case(self, case):
        """
        Inserts a new case into the database, will not check if a 'similar' case already exists.

        :param case:
        :return:
        """
        if not isinstance(case, Case):
            raise Exception("Wrong argument to insert_case, expected Case instance")

        session = self.db_factory()

        session.add(case)
        session.commit()
        session.expunge_all()

        return session.commit()

    def insert_or_increment_case(self, case):
        """
        Inserts a new case, or increments the occurrence counter if the case already exists.

        :param case:
        :return:
        """

        if not isinstance(case, Case):
            raise Exception("Wrong argument to insert_or_increment_case, expected Case instance")

        existing_case = self.get_case_by_object(case)
        if existing_case is not None:
            session = self.db_factory()
            session.query(Case).filter(Case.id == existing_case.id).update(
                {'occurrences': existing_case.occurrences + 1})
            session.commit()
            session.close()
            self.insert_or_increment_case_counter(CaseFromCounter(type=case.type, case_from=case.case_from))
        else:
            case_from_counter = CaseFromCounter(type=case.type, case_from=case.case_from)
            self.insert_case(case)
            self.insert_or_increment_case_counter(case_from_counter)

    def insert_case_counter(self, case_from_counter):
        """
        Inserts a new CaseFromCounter. Does not check if a matching one already exists

        :param case_from_counter:
        :return:
        """
        if not isinstance(case_from_counter, CaseFromCounter):
            raise Exception("Wrong argument to insert_case_Counter, expected CaseFromCounter instance")

        session = self.db_factory()

        session.add(case_from_counter)
        session.commit()
        return

    def insert_or_increment_case_counter(self, case_from_counter):
        """
        Inserts a new CaseFromCounter if on with the same attributes does not already exist,
        else it increments the occurrence counter on the existing one.

        :param case_from_counter:
        :return:
        """
        if not isinstance(case_from_counter, CaseFromCounter):
            raise Exception("Wrong argument to insert_or_increment_case_counter, expected CaseFromCounter instance")

        session = self.db_factory()
        existing_case_counter = self.get_case_counter_from_object(case_from_counter)

        # This should probably never happen
        if existing_case_counter is None:
            session.commit()
            session.close()
            self.insert_case_counter(case_from_counter)
        else:
            session.query(CaseFromCounter). \
                filter(CaseFromCounter.id == existing_case_counter.id). \
                update({'occurrences': existing_case_counter.occurrences + 1})
            session.commit()
            session.close()

    def get_case(self, case_id):
        """
        Fetches a case by id.

        :param case_id:
        :return:
        """

        if case_id is not None:
            session = self.db_factory()
            case = session.query(Case).filter(Case.id == case_id).first()

            if case is None:
                session.close()
                return None
            else:
                session.expunge(case)
                session.close()

            return case

        return None

    def get_case_by_data(self, case_type, case_to, case_from):
        """
        Returns a case by its defining data.

        :param case_type:
        :param case_to:
        :param case_from:
        :return:
        """
        session = self.db_factory()
        case = session.query(Case).filter(Case.type == case_type, Case.case_to == case_to,
                                          Case.case_from == case_from).first()

        if case is None:
            session.close()
            return None
        else:
            session.expunge(case)
            session.close()

        return case

    def get_case_by_object(self, case):
        """
        Returns the persisted version of a case.

        :param case:
        :return:
        """
        return self.get_case_by_data(case.type, case.case_to, case.case_from)

    def fetch_all_to_cases(self, cases):
        """
        Extends a set of from-cases to include all possible to scenarios.

        For instance, say we have the following list of cases:

        [
            {type: CASE_TYPE_POS_WORD, from: "Gut"},
            {type: CASE_TYPE_POS_WORD_CASE: from: "1"}
        ]

        And we have several cases in the database matching these, we would return all the possible matches, e.g:

        [
            {type: CASE_TYPE_POS_WORD, from: "Gut", to: "PREP"},
            {type: CASE_TYPE_POS_WORD_CASE: from: "1", to: "PREP"}
            {type: CASE_TYPE_POS_WORD, from: "Gut", to: "N"},
            {type: CASE_TYPE_POS_WORD_CASE: from: "1", to: "N"}
        ]

        The method will also populate all probabilities by calling self.populate_probabilities

        :param cases:
        :return:
        """
        if not isinstance(cases, Cases):
            raise Exception("Wrong argument to populate_word_cases, expected Cases as second argument")

        session = self.db_factory()

        new_cases = []
        for case in cases.cases:
            db_cases = session.query(Case) \
                .filter(Case.type == case.type) \
                .filter(Case.case_from == case.case_from) \
                .all()

            new_cases.extend(db_cases)

        session.expunge_all()
        session.close()

        new_cases_obj = Cases()
        new_cases_obj.from_array(new_cases)

        self.populate_probabilities(new_cases_obj)
        return new_cases_obj

    def populate_probabilities(self, cases):
        """
        Takes a set of cases, and populates their occurrence-probabilities.

        :param cases:
        :return:
        """
        if not isinstance(cases, Cases):
            raise Exception("Wrong argument to populate_probabilities, expected Cases object")

        from_case_set = set(map(lambda c: (c.type, c.case_from), cases))
        fetched_from_cases = {}  # Dictionary for easy retrieval later
        hash_name = lambda fc: str(fc.type) + fc.case_from  # Lambda for generating hash-name from case_from

        for from_case in from_case_set:
            fetched_from_case = self.get_case_counter_from_data(from_case[0], from_case[1])

            assert fetched_from_case is not None

            fetched_from_cases[hash_name(fetched_from_case)] = fetched_from_case

        # Calculate probabilities
        for case in cases:
            from_case = fetched_from_cases[hash_name(case)]
            prob = float(case.occurrences) / float(from_case.occurrences)

            case.set_prob(prob)

    def get_case_counter(self, case_counter_id):
        """
        Fetches a case_counter by id.

        :param case_counter_id:
        :return:
        """
        if case_counter_id is not None:
            session = self.db_factory()
            case_counter = session.query(CaseFromCounter).filter(CaseFromCounter.id == case_counter_id).first()

            if case_counter is None:
                session.close()
                return None
            else:
                session.expunge(case_counter)
                session.close()

            return case_counter

        return None

    def get_case_counter_from_data(self, case_type, case_from):
        session = self.db_factory()

        case_counter = session.query(CaseFromCounter).filter(CaseFromCounter.type == case_type,
                                                             CaseFromCounter.case_from == case_from).first()
        if case_counter is None:
            session.close()
            return None
        else:
            session.expunge(case_counter)
            session.close()

        return case_counter

    def get_case_counter_from_object(self, case):
        """
        Returns the case counter of a case /or casecounter
        :param case:
        :return:
        """

        return self.get_case_counter_from_data(case.type, case.case_from)

    def _clear_database(self):
        """
        Clears the entire contents of a database.

        Warning, is dangerous.
        :return:
        """
        session = self.db_factory()

        session.query(Case).delete()
        session.query(CaseRelation).delete()
        session.query(CaseFromCounter).delete()
        session.commit()

        session.close()

    def _destroy_database(self):
        """
        Destroys a database instance, clearing its contents and destroys the db-file.

        :return:
        """
        self._clear_database()

        if not self.use_memory:
            os.remove(self.db_path)
