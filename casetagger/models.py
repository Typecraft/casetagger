import math

import casetagger.config as config
from casetagger.util import get_glosses_concatenated
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

    def __iter__(self):
        return self.cases.__iter__()

    def __len__(self):
        return len(self.cases)

    def merge(self):
        """
        This is the 'magic-method' of the algorithm.

        It takes a set of cases, and "merges" them into the result case which is most likely.

        The algorithm works in the following manner:

            1. We have n cases we want to merge.
            2. We take n/2 tuples
            3. For each tuple, we eliminate the least likely one
            4. If n initially was 2, and we have one case remaining, we are done.
               Else we go back to step 1 and reiterate.

        :return:
        """

        merged_cases = self.cases
        if len(self.cases) == 0:
            return ""

        self.max_occurrence_count = max(map(lambda case: case.occurrences, self.cases))

        while len(merged_cases) > 1:
            next_merged_cases = []
            for i in range(0, len(merged_cases), 2):
                to_be_merged = merged_cases[i:i+2]

                if len(to_be_merged) == 1:
                    next_merged_cases.append(to_be_merged[0])
                else:
                    next_merged_cases.append(self.merge_cases(to_be_merged[0], to_be_merged[1]))

            merged_cases = next_merged_cases

        return merged_cases[0].case_to

    def merge_cases(self, case_1, case_2):
        """
        Merges two cases, returning the most likely case
        :param case_1:
        :param case_2:
        :return:
        """
        prob_1 = case_1.prob
        prob_2 = case_2.prob

        if config.ADJUST_FOR_IMPORTANCE:
            prob_1 = Cases.adjust_importance(prob_1, case_1.type)
            prob_2 = Cases.adjust_importance(prob_2, case_2.type)

        return case_1 if prob_1 > prob_2 else case_2

    @staticmethod
    def adjust_importance(probability, case_type):
        if case_type not in config.CASE_IMPORTANCE:
            return probability

        importance = config.CASE_IMPORTANCE[case_type]

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

        if prefix_word is not None:
            self.add_case(config.CASE_TYPE_POS_PREFIX_WORD, prefix_word, pos)

        if suffix_word is not None:
            self.add_case(config.CASE_TYPE_POS_SUFFIX_WORD, suffix_word, pos)

        if prefix_pos is not "" and prefix_pos is not None:
            self.add_case(config.CASE_TYPE_POS_PREFIX_POS, prefix_pos, pos)

        if suffix_pos is not "" and suffix_pos is not None:
            self.add_case(config.CASE_TYPE_POS_SUFFIX_POS, suffix_pos, pos)

        if len(morphemes) > 0:
            for morpheme in morphemes:
                self.add_case(config.CASE_TYPE_POS_MORPHEME, morpheme.lower(), pos)


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
        self.add_case(config.CASE_TYPE_GLOSS_WORD, morpheme.morpheme.lower(), word.word.lower())

        if len(word.word) > 0:
            if word.word[0].isupper():
                self.add_case(config.CASE_TYPE_GLOSS_WORD_CASE, "True", gloss)

        if word.word.lower() != word.word:
            self.add_case(config.CASE_TYPE_GLOSS_WORD_CONTAINS_CASE, "True", gloss)

        if prefix_word is not None:
            self.add_case(config.CASE_TYPE_GLOSS_PREFIX_WORD, prefix_word, gloss)

        if suffix_word is not None:
            self.add_case(config.CASE_TYPE_GLOSS_SUFFIX_WORD, suffix_word, gloss)

        if prefix_pos is not None:
            self.add_case(config.CASE_TYPE_GLOSS_PREFIX_POS, prefix_pos, gloss)

        if suffix_pos is not None:
            self.add_case(config.CASE_TYPE_GLOSS_SUFFIX_POS, suffix_pos, gloss)

        if prefix_gloss is not None:
            self.add_case(config.CASE_TYPE_GLOSS_PREFIX_GLOSS, prefix_gloss, gloss)

        if suffix_gloss is not None:
            self.add_case(config.CASE_TYPE_GLOSS_SUFFIX_GLOSS, suffix_gloss, gloss)

        if prefix_morph is not None:
            self.add_case(config.CASE_TYPE_GLOSS_PREFIX_MORPH, prefix_morph, gloss)

        if suffix_morph is not None:
            self.add_case(config.CASE_TYPE_GLOSS_SUFFIX_MORPH, suffix_morph, gloss)
