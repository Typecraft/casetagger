import math

from casetagger.config import config
import itertools

from casetagger.util import *
from typecraft_python.models import Phrase


class Case:
    """
    Class we use to mock the db-version of a Case.
    """
    def __init__(self, case_type, case_from, case_to, occurrences=1, prob=0):
        self.type = case_type
        self.case_from = case_from
        self.case_to = case_to
        self.occurrences = occurrences
        self.prob = prob

    def get_case_types(self):
        """
        Returns all case types of the Case.

        :return:
        """
        types = []
        for i in range(0, 32):
            if (self.type & (1 << i)) > 0:
                types.append(1 << i)

        return types

    def __eq__(self, other):
        return self.type == other.type and self.case_from == other.case_from and self.case_to == other.case_to

    def __str__(self):
        return "%d %s => %s [occurrences=%s, prob=%s]" % (self.type, self.case_from, self.case_to, self.occurrences, self.prob)


class CaseFromCounter:
    """
    Class we use to mock the db-data of a CaseFromCounter
    """
    def __init__(self, case_type, case_from, occurrences=1):
        self.type = case_type
        self.case_from = case_from
        self.occurrences = occurrences

    def __str__(self):
        return "%d %s => occurences %d" % (self.type, self.case_from, self.occurrences)


class Cases:
    """
    This class represents a collection of cases.

    We have a specific data structure for the purpose of collection some
    utility methods in overriding classes.
    """
    def __init__(self):
        self.cases = []
        self.max_occurrence_count = 0

    def add_case(self, case_type, case_from, case_to, occurrences=1, prob=0):
        self.cases.append(Case(case_type, case_from, case_to, occurrences, prob))

    def add_all_cases(self, cases):
        for case in cases:
            self.add_case(case.type, case.case_from, case.case_to, case.occurrences)

    def create_tuple_cases(self):
        # TODO: Filter and remove morpheme cases?
        case_combinations = itertools.combinations(self.cases, 2)

        for case_tuple in case_combinations:
            case_1 = case_tuple[0]
            case_2 = case_tuple[1]

            # We don't both creating tuple cases of the same type.
            # This is primarily to avoid creating a lot of ngram-tuples
            # which yield no additional information when combined.
            if config['ignore_tuples_of_same_type'] and case_1.type == case_2.type:
                continue

            # Note that case_to will be the same for all tuples
            self.add_case(case_1.type | case_2.type,
                          case_1.case_from + case_2.case_from,
                          case_1.case_to)

    def __iter__(self):
        return self.cases.__iter__()

    def __len__(self):
        return len(self.cases)

    def merge(self):
        """
        This is the 'magic-method' of the algorithm.

        It takes a set of cases, and "merges" them into the result case which is most likely.

        The algorithm works in the following manner:

            1. Merge cases with similar to-endpoints, and combine their probability
            2. We have n cases we want to merge.
            3. We take n/2 tuples
            4. For each tuple, we eliminate the least likely one
            5. If n initially was 2, and we have one case remaining, we are done.
               Else we go back to step 1 and reiterate.

        :return:
        """

        merged_cases = self.cases
        if len(self.cases) == 0:
            return ""

        Cases.adjust_probabilities(merged_cases)
        merged_cases = Cases.combine_similar_cases(merged_cases)
        if config['print_test_error_detail']:
            for case in merged_cases:
                print("Case", unicode(case))

        best_case = max(merged_cases, key=lambda case: case.prob)
        if config['print_test_error_detail']:
            print("Best case", unicode(best_case))
            print("\n\n")
        return best_case.case_to

    @staticmethod
    def combine_similar_cases(cases):
        """
        Takes a set of cases and combines the ones which are predicting the same
        outcome. Their probability is merged simply by calculating 1 minus the probability
        that they are all wrong:

        1 - (sum_{case in cases}(1 - case.prob))

        :param cases: A set of unique to_cases with their calculated probabilities.
        :return:
        """
        combined_cases = []

        combined_case_dict = {}

        for case in cases:
            combined_case_dict.setdefault(case.case_to, []).append(case)

        for _, cases in combined_case_dict.items():
            prob = 1
            for case in cases:
                prob *= (1-case.prob)

            cases[0].prob = 1 - prob
            combined_cases.append(cases[0])

        return combined_cases

    @staticmethod
    def adjust_probabilities(cases):
        """
        This method adjusts the probabilities of cases. The adjustment is
        done in accordance with the importance of each case, as defined in
        the config.

        :param cases:
        :return:
        """
        for case in cases:
            case.prob = Cases.adjust_importance(case.prob, case)
            case.prob = Cases.adjust_occurrence(case.prob, case.occurrences)

    @staticmethod
    def merge_cases(case_1, case_2):
        """
        Merges two cases, returning the most likely case
        :param case_1:
        :param case_2:
        :return:
        """
        return case_1 if case_1.prob > case_2.prob else case_2

    @staticmethod
    def adjust_importance(probability, case):
        case_types = case.get_case_types()

        importance = sum(map(lambda _case_type: config['case_importance'][str(_case_type)], case_types))

        return importance * probability

    @staticmethod
    def adjust_occurrence(probability, occurrence):
        return probability * (1 - (1 / math.exp(float(occurrence + 5 * math.log(2)) / 5)))


class WordCases(Cases):
    def __init__(self, word, phrase):
        """
        Creates the word-cases object.

        This constructor initialises all relevant cases for the WordCases object.

        :param word:
        :param phrase:
        """

        Cases.__init__(self)
        if not isinstance(phrase, Phrase):
            raise Exception("Invalid argument to WordCases.__init__, expected Phrase as second argument")

        word_index = phrase.words.index(word)
        pos = word.pos

        morphemes = []

        if len(word.morphemes) > 0:
            morphemes = list(map(lambda x: x.morpheme, word.morphemes))

        self.add_case(config['case_type_pos_word'], word.word.lower(), pos)

        if len(morphemes) > 0:
            for morpheme in morphemes:
                if not is_empty_ignore(morpheme):
                    self.add_case(config['case_type_pos_morpheme'], morpheme.lower(), pos)

        self.add_word_surrounding_ngram_cases(word_index, phrase, pos)
        self.create_tuple_cases()

    def add_word_surrounding_ngram_cases(self, word_index, phrase, pos_to):
        """
        Adds the internal word n-gram cases of the phrase/word.

        :param word_index:
        :param phrase:
        :param pos_to:
        :return:
        """
        for i in range(2, config['surrounding_ngram_max_length']+1):
            ngrams_of_length_i = get_consecutive_sublists_of_length_around_index(phrase.words, word_index, i)
            for ngram in ngrams_of_length_i:
                self.add_case(config['case_type_pos_surrounding_ngram'],
                              "".join(map(lambda word: word.word if word.word is not None else "", ngram)),
                              pos_to)
                self.add_case(config['case_type_pos_surrounding_ngram'],
                              "".join(map(lambda word: word.pos if word.pos is not None else "", ngram)),
                              pos_to)


class MorphemeCases(Cases):
    def __init__(self, morpheme, word, phrase):
        """
        Creates the MorphemeTargetCases object, registering all valid cases.

        :param morpheme:
        :param word:
        :param phrase:
        """
        Cases.__init__(self)
        morpheme_index = word.morphemes.index(morpheme)

        # Case variables
        gloss = get_glosses_concatenated(morpheme)
        word_index = phrase.words.index(word)

        self.add_case(config['case_type_gloss_morph'], morpheme.morpheme.lower(), gloss)
        self.add_case(config['case_type_gloss_word'], morpheme.morpheme.lower(), gloss)

        self.add_surrounding_morpheme_ngram_cases(morpheme_index, word.morphemes, gloss)
        self.add_surrounding_word_ngram_cases(word_index, phrase.words, gloss)

    def add_surrounding_morpheme_ngram_cases(self, morpheme_index, morphemes, gloss_to):
        """
        Adds the surrounding morph and gloss n-grams of a given morpheme.

        :param morpheme_index:
        :param morphemes:
        :param gloss_to:
        :return:
        """
        for i in range(2, config['surrounding_ngram_max_length']+1):
            ngrams_of_length_i = get_consecutive_sublists_of_length_around_index(morphemes, morpheme_index, i)
            for ngram in ngrams_of_length_i:
                self.add_case(config['case_type_gloss_surrounding_ngram'],
                              "".join(map(lambda morpheme: morpheme.morpheme if morpheme.morpheme is not None else "", ngram)),
                              gloss_to)
                self.add_case(config['case_type_gloss_surrounding_ngram'],
                              "".join(map(lambda morpheme: get_glosses_concatenated(morpheme), ngram)),
                              gloss_to)

    def add_surrounding_word_ngram_cases(self, word_index, words, gloss_to):
        """
        Adds the surrounding word and pos n-grams of a given morpheme.

        :param word_index:
        :param words:
        :param gloss_to:
        :return:
        """
        for i in range(2, config['surrounding_ngram_max_length']+1):
            ngrams_of_length_i = get_consecutive_sublists_of_length_around_index(words, word_index, i)
            for ngram in ngrams_of_length_i:
                self.add_case(config['case_type_gloss_surrounding_ngram'],
                              "".join(map(lambda word: word.word if word.word is not None else "", ngram)),
                              gloss_to)
                self.add_case(config['case_type_gloss_surrounding_ngram'],
                              "".join(map(lambda word: word.pos if word.pos is not None else "", ngram)),
                              gloss_to)


class TestResult:
    def __init__(self, title="SomeTest", words_total=0, morphemes_total=0, words_correct=0, morphemes_correct=0,
                       wrong_words=[], wrong_morphemes=[]):
        self.title = title
        self.words_total = words_total
        self.morphemes_total = morphemes_total
        self.words_correct = words_correct
        self.morphemes_correct = morphemes_correct
        self.wrong_words = wrong_words
        self.wrong_morphemes = wrong_morphemes

    def word_accuracy(self):
        return 100 * float(self.words_correct) / float(self.words_total)

    def morpheme_accuracy(self):
        return 100 * float(self.morphemes_correct) / float(self.morphemes_total)

    def __str__(self):
        res = """
            TestResult for %s:
                Words total = %s
                Morphemes total = %s
                Words correctly tagged = %s (%.2f %%)
                Morphemes correctly tagged = %s (%.2f %%)
            """ % (self.title, self.words_total, self.morphemes_total,
                   self.words_correct, self.word_accuracy(),
                   self.morphemes_correct, self.morpheme_accuracy())

        if config['print_test_error_detail']:
            res += "Word errors:\n"
            for word_tuple in self.wrong_words:
                res += "For word %s:\n\tCorrect: %s\n\tWrong: %s\n\n" % (word_tuple[0].word, word_tuple[0].pos, word_tuple[1].pos)

            res += "Morpheme errors:\n"
            for morph_tuple in self.wrong_morphemes:
                res += "For morpheme %s:\n\tCorrect: %s\n\tWrong: %s\n\n" % (morph_tuple[0].morpheme,
                                                                             get_glosses_concatenated(morph_tuple[0]),
                                                                             get_glosses_concatenated(morph_tuple[1]))

        return res

    @staticmethod
    def from_data(text_1, text_2):
        words_1 = get_text_words(text_1)
        words_2 = get_text_words(text_2)

        morphemes_1 = get_text_morphemes(text_1)
        morphemes_2 = get_text_morphemes(text_2)

        zipped_morphemes = zip(morphemes_1, morphemes_2)

        word_errors = filter(lambda x: x[0].pos != x[1].pos, zip(words_1, words_2))
        morpheme_errors = filter(lambda x: x[0].get_glosses_concatenated(True) != x[1].get_glosses_concatenated(True),
                                 zipped_morphemes)

        words_total = len(words_1)
        morphemes_total = len(morphemes_1)

        words_correct = words_total - len(word_errors)
        morphemes_correct = morphemes_total - len(morpheme_errors)

        return TestResult(
            text_1.title,
            words_total,
            morphemes_total,
            words_correct,
            morphemes_correct,
            word_errors,
            morpheme_errors
        )

    @staticmethod
    def merge(this, other):
        if this is None:
            return other

        if other is None:
            return this

        return TestResult(this.title + " | " + other.title,
                          this.words_total + other.words_total,
                          this.morphemes_total + other.morphemes_total,
                          this.words_correct + other.words_correct,
                          this.morphemes_correct + other.morphemes_correct,
                          this.wrong_words.extend(other.wrong_words),
                          this.wrong_morphemes.extend(other.wrong_morphemes))


def is_empty_ignore(content):
    return content is None or (config['ignore_empty_from_cases'] and content == "")
