import casetagger.config as config
import casetagger.models.db as models

import math

from tc_xml_python.models import Phrase


class CaseMock:
    """
    Class we use to mock the db-version of a Case.

    This version gives a bit more flexibility in terms of values we might want added,
    as well as not having to care about persistance.
    """
    def __init__(self, case_type, case_from, case_to, occurrences=1, prob=0):
        self.type = case_type
        self.case_from = case_from
        self.case_to = case_to
        self.occurrences = occurrences
        self.prob = prob

    def set_prob(self, prob):
        self.prob = prob

    def __str__(self):
        return "%d %s => %s [occurences=%s, prob=%s]" % (self.type, self.case_from, self.case_to, self.occurrences, self.prob)


class Cases:
    """
    This class represents a collection of cases.

    We have a specific data structure for the purpose of collection some
    utility methods in overriding classes.
    """
    def __init__(self):
        self.cases = []

    def add_case(self, case_type, case_from, case_to, occurrences=1, prob=0):
        self.cases.append(CaseMock(case_type, case_from, case_to, occurrences, prob))

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

        The aglorithm works in the following manner:


        :return:
        """

        for case in self.cases:
            print("Merging: " + str(case))
        return "N"

    @classmethod
    def adjust_probability(self, probability, occurrences, max_occurences):
        """
        This method takes a probability, an occurrence-count, and a base-line max-occurrences,
        from which it calculates an adjusted probability.

        The idea behind this is to adjust probabilities which rely on "few" occurrence-counts to be more
        insecure than probabilities which have high occurrence counts.

        Quite simply, the scaling factor is log_a(occurences)/log_a(max_occurrences) where a is some
        base, 1000 by default.

        Example: We have a probability 0.8 with 2000 occurrences, and max_occurrences 8000

        This gives the adjusted probability = 0.8 * log_1000(2000)/log_1000(8000) = 0.67

        The scaling is clearly slow, as with max_occurrences equal to 100 000 we get a adjusted probability
        in the example above 0.52.

        Note that probability adjusting can be turned off by setting config.ADJUST_FOR_OCCURRENCE to false

        :param probability:
        :param occurences:
        :param max_occurences:
        :return:
        """

        return probability * math.log(occurrences, config.OCCURRENCE_ORDER_OF_MAGNITUDE) / math.log(max_occurences, config.OCCURRENCE_ORDER_OF_MAGNITUDE)

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
            morphemes = map(lambda x: x.morpheme, word.morphemes)

        self.add_case(config.CASE_TYPE_POS_WORD, word.word.lower(), pos)

        if str(word.word[0]).isupper():
            self.add_case(config.CASE_TYPE_POS_WORD_CASE, "True", pos)

        if str(word.word.lower() != word.word):
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
        Creates the MorphemeTargetCases object.

        :param morpheme:
        :param word:
        :param phrase:
        """
        Cases.__init__(self)
        word_index = word.morphemes.index(morpheme)
        morphs_length = len(word.morphemes)

        # Case variables
        prefix_morph = None
        suffix_morph = None
        prefix_gloss = None
        suffix_gloss = None
        gloss = ".".join(morpheme.glosses)

        if word_index > 0:
            prefix_morph = word.morphemes[0].word
            prefix_gloss = word.morphemes[0].pos

        if word_index < morphs_length - 1:
            suffix_morph = word.morphemes[word_index + 1]
            suffix_gloss = word.morphemes[0].pos




    def merge(self):
        pass
