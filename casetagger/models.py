import math

import casetagger.config as config
import itertools
from casetagger import logger
from casetagger.util import get_glosses_concatenated, get_text_words, get_text_morphemes
from tc_xml_python.models import Phrase


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
        types = []
        for i in range(0, 32):
            if (self.type & (1 << i)) > 0:
                types.append(1 << i)

        return types

    def __eq__(self, other):
        return self.type == other.type and self.case_from == other.case_from and self.case_to == other.case_to

    def __str__(self):
        return "%d %s => %s [occurences=%s, prob=%s]" % (self.type, self.case_from, self.case_to, self.occurrences, self.prob)


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

    def from_array(self, array):
        for case in array:
            self.add_case(case.type, case.case_from, case.case_to, case.occurrences)

    def create_tuple_cases(self):
        # TODO: Filter and remove morpheme cases?
        case_combinations = itertools.combinations(self.cases, 2)

        for case_tuple in case_combinations:
            case_1 = case_tuple[0]
            case_2 = case_tuple[1]

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

        self.adjust_probabilities(merged_cases)
        merged_cases = self.combine_similar_cases(merged_cases)

        best_case = max(merged_cases, key=lambda case: case.prob)

        logger.debug("Found dominating case: " + str(best_case))
        return best_case.case_to

    def combine_similar_cases(self, cases):
        """
        Takes a set of cases and combines the ones with equal to-probability
        :param cases:
        :return:
        """
        combined_cases = []

        combined_case_dict = {}

        for case in cases:
            combined_case_dict.setdefault(case.case_to, []).append(case)

        for _, cases in combined_case_dict.iteritems():
            prob = 1
            for case in cases:
                prob *= (1-case.prob)

            cases[0].prob = 1 - prob
            combined_cases.append(cases[0])

        return combined_cases

    def adjust_probabilities(self, cases):
        for case in cases:
            case.prob = Cases.adjust_importance(case.prob, case)

        # Normalize
        best_case = max(cases, key=lambda x: x.prob).prob

        for case in cases:
            case.prob = case.prob / best_case

    def merge_cases(self, case_1, case_2):
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

        importance = sum(map(lambda _case_type: config.CASE_IMPORTANCE[_case_type], case_types))

        return importance * probability

    @staticmethod
    def adjust_probability(probability, occurrences, max_occurrences):
        """
        This method takes a probability, an occurrence-count, and a base-line max-occurrences,
        from which it calculates an adjusted probability.

        The idea behind this is to adjust probabilities which rely on "few" occurrence-counts to be more
        insecure than probabilities which have high occurrence counts.

        Quite simply, the scaling factor is log_a(occurences+1)/log_a(max_occurrences+1) where a is some
        base, 1000 by default. (+1 is to avoid division by 0)

        Example: We have a probability 0.8 with 2000 occurrences, and max_occurrences 8000

        This gives the adjusted probability = 0.8 * log_1000(2000)/log_1000(8000) = 0.67

        The scaling is clearly slow, as with max_occurrences equal to 100 000 we get a adjusted probability
        in the example above 0.52.

        Note that probability adjusting can be turned off by setting config.ADJUST_FOR_OCCURRENCE to false

        :param max_occurrences:
        :param occurrences:
        :param probability:
        :return:
        """

        return probability * math.log(occurrences+1, config.OCCURRENCE_ORDER_OF_MAGNITUDE) / math.log(max_occurrences+1, config.OCCURRENCE_ORDER_OF_MAGNITUDE)


class WordCases(Cases):
    def __init__(self, word, phrase):
        """
        Creates the word-cases object
        :param word:
        :param phrase:
        """

        Cases.__init__(self)
        if not isinstance(phrase, Phrase):
            raise Exception("Invalid argument to WordCases.__init__, expected Phrase as second argument")

        word_index = phrase.words.index(word)
        word_length = len(phrase.words)

        # Case variables
        prefix_word = None
        suffix_word = None
        prefix_pos = None
        suffix_pos = None
        pos = word.pos

        morphemes = []

        if word_index > 0:
            prefix_word = phrase.words[word_index - 1].word
            prefix_pos = phrase.words[word_index - 1].pos

        if word_index < word_length - 1:
            suffix_word = phrase.words[word_index + 1].word
            suffix_pos = phrase.words[word_index + 1].pos

        if len(word.morphemes) > 0:
            morphemes = list(map(lambda x: x.morpheme, word.morphemes))

        self.add_case(config.CASE_TYPE_POS_WORD, word.word.lower(), pos)

        if len(word.word) > 0:
            if word.word[0].isupper():
                self.add_case(config.CASE_TYPE_POS_WORD_CASE, "True", pos)

        if word.word.lower() != word.word:
            self.add_case(config.CASE_TYPE_POS_WORD_CONTAINS_CASE, "True", pos)

        if not is_empty_ignore(prefix_word):
            self.add_case(config.CASE_TYPE_POS_PREFIX_WORD, prefix_word, pos)

        if not is_empty_ignore(suffix_word):
            self.add_case(config.CASE_TYPE_POS_SUFFIX_WORD, suffix_word, pos)

        if not is_empty_ignore(prefix_pos):
            self.add_case(config.CASE_TYPE_POS_PREFIX_POS, prefix_pos, pos)

        if not is_empty_ignore(suffix_pos):
            self.add_case(config.CASE_TYPE_POS_SUFFIX_POS, suffix_pos, pos)

        if len(morphemes) > 0:
            for morpheme in morphemes:
                if not is_empty_ignore(morpheme):
                    self.add_case(config.CASE_TYPE_POS_MORPHEME, morpheme.lower(), pos)

        self.create_tuple_cases()


class MorphemeCases(Cases):
    def __init__(self, morpheme, word, phrase):
        """
        Creates the MorphemeTargetCases object, registering all valid cases.

        :param morpheme:
        :param word:
        :param phrase:
        """
        Cases.__init__(self)
        morph_index = word.morphemes.index(morpheme)
        morphs_length = len(word.morphemes)

        # Case variables
        prefix_morph = None
        suffix_morph = None
        prefix_gloss = None
        suffix_gloss = None
        gloss = get_glosses_concatenated(morpheme)

        if morph_index > 0:
            prefix_morph = word.morphemes[morph_index - 1].morpheme
            prefix_gloss = get_glosses_concatenated(word.morphemes[morph_index - 1])

        if morph_index < morphs_length - 1:
            suffix_morph = word.morphemes[morph_index + 1].morpheme
            suffix_gloss = get_glosses_concatenated(word.morphemes[morph_index + 1])

        # Case variables
        prefix_word = None
        suffix_word = None
        prefix_pos = None
        suffix_pos = None

        word_index = phrase.words.index(word)
        word_length = len(phrase.words)

        if word_index > 0:
            prefix_word = phrase.words[word_index - 1].word
            prefix_pos = phrase.words[word_index - 1].pos

        if word_index < word_length - 1:
            suffix_word = phrase.words[word_index + 1].word
            suffix_pos = phrase.words[word_index + 1].pos

        self.add_case(config.CASE_TYPE_GLOSS_MORPH, morpheme.morpheme.lower(), gloss)
        self.add_case(config.CASE_TYPE_GLOSS_WORD, morpheme.morpheme.lower(), gloss)

        if len(word.word) > 0:
            if word.word[0].isupper():
                self.add_case(config.CASE_TYPE_GLOSS_WORD_CASE, "True", gloss)

        if word.word.lower() != word.word:
            self.add_case(config.CASE_TYPE_GLOSS_WORD_CONTAINS_CASE, "True", gloss)

        if not is_empty_ignore(prefix_word):
            self.add_case(config.CASE_TYPE_GLOSS_PREFIX_WORD, prefix_word, gloss)

        if not is_empty_ignore(suffix_word):
            self.add_case(config.CASE_TYPE_GLOSS_SUFFIX_WORD, suffix_word, gloss)

        if not is_empty_ignore(prefix_pos):
            self.add_case(config.CASE_TYPE_GLOSS_PREFIX_POS, prefix_pos, gloss)

        if not is_empty_ignore(suffix_pos):
            self.add_case(config.CASE_TYPE_GLOSS_SUFFIX_POS, suffix_pos, gloss)

        if not is_empty_ignore(prefix_gloss):
            self.add_case(config.CASE_TYPE_GLOSS_PREFIX_GLOSS, prefix_gloss, gloss)

        if not is_empty_ignore(suffix_gloss):
            self.add_case(config.CASE_TYPE_GLOSS_SUFFIX_GLOSS, suffix_gloss, gloss)

        if not is_empty_ignore(prefix_morph):
            self.add_case(config.CASE_TYPE_GLOSS_PREFIX_MORPH, prefix_morph, gloss)

        if not is_empty_ignore(suffix_morph):
            self.add_case(config.CASE_TYPE_GLOSS_SUFFIX_MORPH, suffix_morph, gloss)


class TestResult:
    def __init__(self, title = "SomeTest", words_total=0, morphemes_total=0, words_correct=0, morphemes_correct=0,
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

        if config.PRINT_TEST_ERROR_DETAIL:
            res += "Word errors:\n"
            for word_tuple in self.wrong_words:
                res += "\nCORRECT:\n" + str(word_tuple[0]) + "\nWRONG:\n" + str(word_tuple[1])
            for morph_tuple in self.wrong_morphemes:
                res += "\nCORRECT:\n" + str(morph_tuple[0]) + "\nWRONG:\n" + str(morph_tuple[1])

        return res

    @staticmethod
    def from_data(text_1, text_2):
        words_1 = get_text_words(text_1)
        words_2 = get_text_words(text_2)

        morphemes_1 = get_text_morphemes(text_1)
        morphemes_2 = get_text_morphemes(text_2)

        word_errors = filter(lambda x: x[0].pos != x[1].pos, zip(words_1, words_2))
        morpheme_errors = filter(lambda x: x[0].get_glosses_concatenated(True) != x[1].get_glosses_concatenated(True),
                                 zip(morphemes_1, morphemes_2))

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
    return content is None or (config.IGNORE_EMPTY_FROM_CASES and content == "")
