import casetagger.config as config
import casetagger.models.db as models

from tc_xml_python.models.phrase import Phrase


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


class WordFullCases(Cases):
    pass


class MorphemeTargetCases(Cases):
    def __init__(self, morpheme, word, phrase):
        """

        :param morpheme:
        :param word:
        :param phrase:
        """

    def merge(self):
        pass


class WordTargetCases(Cases):
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
        morphemes = []

        if word_index > 0:
            prefix_word = phrase.words[0].word
            prefix_pos = phrase.words[0].pos

        if word_index < word_length - 1:
            suffix_word = phrase.words[word_index + 1]
            suffix_pos = phrase.words[0].pos

        if len(word.morphemes) > 0:
            morphemes = map(lambda x: x.morpheme, word.morphemes)

        if prefix_word is not None:
            self.add_case(config.CASE_TYPE_POS_PREFIX_WORD, prefix_word, None)

        if suffix_word is not None:
            self.add_case(config.CASE_TYPE_POS_SUFFIX_WORD, suffix_word, None)

        if prefix_pos is not None:
            self.add_case(config.CASE_TYPE_POS_PREFIX_POS, prefix_pos, None)

        if suffix_pos is not None:
            self.add_case(config.CASE_TYPE_POS_SUFFIX_POS, suffix_pos, None)

        if len(morphemes) > 0:
            for morpheme in morphemes:
                self.add_case(config.CASE_TYPE_POS_MORPHEME, morpheme.morpheme, None)

    def merge(self):
        return self.cases[0]

