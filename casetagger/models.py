import math
from functools import reduce

from casetagger.config import config
import itertools

from casetagger.logger import debug_print_cases, debug
from casetagger.util import *
from typecraft_python.models import Phrase, Word, Morpheme


class Case:
    """
    Class we use to mock the db-version of a Case.
    """

    def __init__(self, case_type, case_from, case_to, occurrences=1, prob=0):
        """
        Initialises the case.

        :param case_type: The type of the case. An integer between 1 - 2^32
        :param case_from: A string representing the from-part of the case.
        :param case_to: A string representing the to-part of the case.
        :param occurrences: The amount of times the case has occurred.
        :param prob: The probability value of this case.
        """
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
        # This gets all individual bits that are set in self.type
        for i in range(0, 32):
            if (self.type & (1 << i)) > 0:
                types.append(1 << i)

        return types

    def __eq__(self, other):
        """
        Checks if this case equals another case. Will look at
        the variables type, case_from, case_to.
        :param other: The case to test against.
        :return: True or false.
        """
        return self.type == other.type and self.case_from == other.case_from and self.case_to == other.case_to

    def __str__(self):
        """
        Converts the case into a readable string.
        :return: A string representing the case.
        """
        case_types = self.get_case_types()
        case_types_reversed = map(lambda x: config['reverse_names'][str(x)], case_types)
        case_types_reversed = " AND ".join(case_types_reversed)

        case_from_split = self.case_from.split("@")
        cases_from = " AND ".join(case_from_split)

        return u"%s: '%s' => %s [occurrences=%s, prob=%.3f]" \
               % (case_types_reversed, cases_from, self.case_to, self.occurrences, self.prob)

    def __unicode__(self):
        """
        Converts the
        :return:
        """
        return self.__str__()

    def __repr__(self):
        """
        Gets the hash of this case. This is just the string created by concatenating the case's type,
        case_from and case_to attributes.
        :return:
        """
        return u"%d%s%s" % (self.type, self.case_from, self.case_to)


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
        """
        Constructor.
        """
        self.cases = []
        self.max_occurrence_count = 0

    def add_case(self, case_type, case_from, case_to, occurrences=1, prob=0):
        """
        Adds a case to the Cases-object.

        :param case_type: The type of a case, an integer.
        :param case_from: The 'from'-token of the case.
        :param case_to: The 'to'-token of the case.
        :param occurrences: The amount of times this case has occurred.
        :param prob: The probability of this case. Defined as occurrences / sum_{i in allcases}(occurrence_i)
        :return: void
        """
        self.cases.append(Case(case_type, case_from, case_to, occurrences, prob))

    def add_all_cases(self, cases):
        """
        Adds a number of cases.

        :param cases: An iterable of cases.
        :return:
        """
        for case in cases:
            self.add_case_from_obj(case)

    def add_case_from_obj(self, case):
        """
        Adds a case from an 'Case'-object. Will not clone the case, and may thus be externally overwritten.
        :param case:
        :return:
        """
        assert isinstance(case, Case)

        self.cases.append(case)

    def create_tuple_cases(self):
        """
        This method will create tuple cases from the current cases.

        What this means can be illustrated with an example.
        Say we have the following cases:
            1 Arne N    (case_type_pos_word)
            65536 SBJ N     (case_type_gloss_morph)
            ...

        This method would then amongst other things, create a new case:
            65537 Arne@SBJ N

        This can be read as:
            'If we have the word Arne and the gloss SBJ', then we have the pos N.'

        The maximum length of tuples that are generated can be configured.

        :return: void
        """
        # TODO: Filter and remove morpheme cases?

        cases_to_be_added = []
        for i in range(2, config['tuple_max_length']+1):
            case_combinations = itertools.combinations(self.cases, i)

            for case_tuple in case_combinations:
                # We don't create tuple-cases if the cases are in the same case-group.
                # This is primarily to avoid creating a lot of ngram-tuples
                # which yield no additional information when combined.
                if config['ignore_tuples_of_same_type']:
                    # This somewhat ugly "if" simply says that if either of the cases share case_group...
                    if len(set(map(lambda x: config['case_groups'][str(x.type)], case_tuple))) < len(case_tuple):
                        continue

                cases = sorted(case_tuple, key=lambda x: x.type)

                cases_type = reduce(lambda x, y: x | y.type, cases, 0)
                cases_from = "@".join(map(lambda x: x.case_from, cases))
                cases_to = case_tuple[0].case_to

                # Note that case_to will be the same for all tuples
                cases_to_be_added.append(Case(cases_type, cases_from, cases_to))

        self.add_all_cases(cases_to_be_added)

    def __iter__(self):
        """
        Iterates the cases of this Cases object.
        :return: Iterator
        """
        return self.cases.__iter__()

    def __len__(self):
        """
        Returns the length of cases in this Cases object.
        :return: Iterator
        """
        return len(self.cases)

    def merge(self):
        """
        This is the 'magic-method' of the algorithm.

        It takes a set of cases, and "merges" them into the result case which is most likely.

        The algorithm works in the following manner:

            1. Merge cases with similar to-endpoints, and combine their probability
            2. We have n cases we want to merge.
            3. The the most likely

        :return: The most promising case.
        """

        merged_cases = self.cases

        # First check if we have a mapping
        for case in merged_cases:
            key = "%d%s" % (case.type, case.case_from)
            if key in config['case_mappings']:
                return config['case_mappings'][key]

        Cases.adjust_individual_probabilities(merged_cases)
        debug("Before merging:")
        debug_print_cases(merged_cases)
        debug("\n\n")
        if len(self.cases) == 0:
            return ""

        merged_cases = Cases.combine_similar_cases(merged_cases)
        debug("After merging:")
        debug_print_cases(merged_cases)
        debug("\n\n")

        Cases.adjust_collectional_probabilities(merged_cases)
        debug("After merging and adjusting:")
        debug_print_cases(merged_cases)
        debug("\n\n")

        best_case = max(merged_cases, key=lambda case: case.prob)
        debug("Best case:")
        debug("\n\n")
        debug_print_cases(merged_cases)
        debug("\n\n")
        return best_case.case_to

    @staticmethod
    def combine_similar_cases(cases):
        """
        Takes a set of cases and combines the ones which are predicting the same
        outcome. Their probability is merged simply by calculating 1 minus the probability
        that they are all wrong:

        1 - (prod_{case in cases}(1 - case.prob))

        :param cases: A set of unique to_cases with their calculated probabilities.
        :return:
        """
        combined_cases = []

        combined_case_dict = {}

        for case in cases:
            combined_case_dict.setdefault(case.case_to, []).append(case)

        for _, cases in combined_case_dict.items():
            prob = 1
            occurrences = 0
            for case in cases:
                prob *= (1-case.prob)
                occurrences += case.occurrences

            cases[0].prob = 1 - prob
            cases[0].occurrences = occurrences
            cases[0].case_from = ""
            combined_cases.append(cases[0])

        return combined_cases

    @staticmethod
    def adjust_individual_probabilities(cases):
        """
        This method adjusts the probabilities of cases. The adjustment is
        done in accordance with the importance of each case, as defined in
        the config.

        :param cases:
        :return:
        """
        for case in cases:
            case.prob = Cases.adjust_importance(case.prob, case)
            case.prob = Cases.adjust_case_from_importance(case.prob, case)
            case.prob = Cases.adjust_full_case_importance(case.prob, case)
            case.prob = Cases.adjust_from_case_complexity(case.prob, case.case_from)

    @staticmethod
    def adjust_collectional_probabilities(cases):
        """
        This method adjusts the probabilities of a collection of cases.

        Adjusting probabilities based on for instance the occurrence-count, can only really
        be done accurately in the context of other similar cases.

        :param cases: A collection of cases.
        :return: Void, everything is edited in place
        """
        occurrence_max = float(max(map(lambda case: case.occurrences, cases)))

        if occurrence_max == 0:
            return

        for case in cases:
            case.prob /= 1.0 + math.exp(-case.occurrences / (occurrence_max / 2))

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
    def adjust_from_case_complexity(probability, case_from):
        """
        Adjusts a cases probability from its complexity.

        A case is considered complex if it is a part of an ngram ('|'-delimiters), or it is a
        tuple-case ('@'-delimiters).

        :param probability: The probability to adjust.
        :param case_from: The case to find the complexity of.
        :return: New Probability
        """
        ngram_count = len(list(filter(lambda x: x == '|', case_from)))
        tuple_count = len(list(filter(lambda x: x == '@', case_from)))

        temp_prob = 1 - probability
        for i in range(1, ngram_count+1):
            temp_prob *= (1 - probability/i)

        for j in range(1, tuple_count+1):
            temp_prob *= (1 - probability/j)

        return 1 - temp_prob

    @staticmethod
    def adjust_importance(probability, case):
        """
        Adjust a cases importance from its importance as specified in the config.

        If the case is a tuple case, the importance is adjusted for all of the cases.

        :param probability: The probability to adjust.
        :param case_from: The case to find the complexity of.
        :return: New probability
        """
        case_types = case.get_case_types()
        importances = list(map(lambda _case_type: config['case_importance'][str(_case_type)], case_types))
        if len(importances) == 0:
            return probability
        importance = sum(importances) / len(importances)

        return importance * probability

    @staticmethod
    def adjust_case_from_importance(probability, case):
        """
        Adjusts a case by an importance of its (type, case_from), if such an adjustment exists.

        :param probability: The existing probability for the case.
        :param case: The case object.
        :return:
        """
        key = u"%d%s" % (case.type, case.case_from)

        if key in config['case_from_adjustments']:
            importance = config['case_from_adjustment']
            return probability * standard_0_to_1000_factor_scale(importance)
        return probability

    @staticmethod
    def adjust_full_case_importance(probablity, case):
        """
        Adjusts a case by an importance of the full case input, if such an adjustment exists.

        :param probability: The existing probability for the case.
        :param case: The case object.
        :return:
        """
        key = u"%d%s%s" % (case.type, case.case_from, case.case_to)

        if key in config['case_full_adjustments']:
            importance = config['case_from_adjustment']
            return probablity * standard_0_to_1000_factor_scale(importance)
        return probablity

    @staticmethod
    def adjust_occurrence(probability, occurrence):
        """
        Adjust a cases importance based on its occurrence.

        The idea here is simply that an often occurring case is 'more reliable' than a case we've only
        seen a few times.

        We adjust by using the raw sigmoid function.

        :param probability: The probability to adjust.
        :param case_from: The case to find the complexity of.
        :return: New probability
        """
        if occurrence < 0:
            return 0

        return (1.0 / (1.0 + math.exp(-occurrence/100))) * probability

    @staticmethod
    def adjust_case_from_config(case):
        case = Case


class WordCases(Cases):
    """
    This class specializes the 'Cases'-object, and implements some handy helper-methods
    for adding word-specific cases.
    """

    def __init__(self, word, phrase):
        """
        Creates the word-cases object.

        This constructor initialises all relevant cases for the WordCases object.

        :param word: The word to get the cases for.
        :param phrase: The surrounding phrase.
        """

        Cases.__init__(self)
        if not isinstance(phrase, Phrase):
            raise Exception("Invalid argument to WordCases.__init__, expected Phrase as second argument")

        word_index = phrase.words.index(word)
        pos = word.pos

        morphemes = []

        self.add_case(config['case_type_pos_word'], word.word.lower(), pos)

        if len(word.morphemes) > 0:
            for morpheme in word.morphemes:
                if not is_empty_ignore(morpheme.morpheme):
                    self.add_case(config['case_type_pos_morpheme'], morpheme.morpheme.lower(), pos)
                    for gloss in morpheme.glosses:
                        self.add_case(config['case_type_pos_gloss'], gloss, pos)

        if config['register_ngrams']:
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
        if len(phrase.words) <= 1:
            return

        max_length = config['surrounding_ngram_max_length']+1
        prefix_ngrams = get_all_prefix_sublists_upto_length(phrase.words,
                                                            word_index,
                                                            max_length)
        suffix_ngrams = get_all_suffix_sublists_upto_length(phrase.words,
                                                            word_index,
                                                            max_length)

        filler = Word()
        filler.word = '<>'
        filler.pos = '<>'
        # We add a filler here so we don't get ambiguous surroundings.
        # This can for instance happen with words at the edge of phrases
        # Where the position of the pos is not implicitly in the "center"
        surrounding_ngrams = get_surrounding_sublists_upto_length(phrase.words,
                                                                  word_index,
                                                                  max_length,
                                                                  filler=[filler])

        for ngram in prefix_ngrams:
            self.add_case(config['case_type_pos_prefix_ngram'],
                          "|".join(map(lambda word: word.word if word.word is not None else "", ngram)),
                          pos_to)
            self.add_case(config['case_type_pos_prefix_ngram'],
                          "|".join(map(lambda word: word.pos if word.pos is not None else "", ngram)),
                          pos_to)

        for ngram in suffix_ngrams:
            self.add_case(config['case_type_pos_suffix_ngram'],
                          "|".join(map(lambda word: word.word if word.word is not None else "", ngram)),
                          pos_to)
            self.add_case(config['case_type_pos_suffix_ngram'],
                          "|".join(map(lambda word: word.pos if word.pos is not None else "", ngram)),
                          pos_to)

        for ngram in surrounding_ngrams:
            self.add_case(config['case_type_pos_surrounding_ngram'],
                          "|".join(map(lambda word: word.word if word.word is not None else "", ngram)),
                          pos_to)
            self.add_case(config['case_type_pos_surrounding_ngram'],
                          "|".join(map(lambda word: word.pos if word.pos is not None else "", ngram)),
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
        self.add_case(config['case_type_gloss_pos'], word.pos, gloss)

        if config['register_ngrams']:
            self.add_surrounding_morpheme_ngram_cases(morpheme_index, word.morphemes, gloss)
            #self.add_surrounding_word_ngram_cases(word_index, phrase.words, gloss)
        self.create_tuple_cases()

    def add_surrounding_morpheme_ngram_cases(self, morpheme_index, morphemes, gloss_to):
        """
        Adds the surrounding morph and gloss n-grams of a given morpheme.

        :param morpheme_index:
        :param morphemes:
        :param gloss_to:
        :return:
        """
        if len(morphemes) <= 1:
            return

        max_length = config['surrounding_ngram_max_length']+1
        prefix_ngrams = get_all_prefix_sublists_upto_length(morphemes,
                                                            morpheme_index,
                                                            max_length)
        suffix_ngrams = get_all_suffix_sublists_upto_length(morphemes,
                                                            morpheme_index,
                                                            max_length)

        filler = Morpheme()
        filler.morpheme = '<>'
        filler.add_gloss('<>')
        # We add a filler here so we don't get ambiguous surroundings.
        # This can for instance happen with words at the edge of phrases
        # Where the position of the pos is not implicitly in the "center"
        surrounding_ngrams = get_surrounding_sublists_upto_length(morphemes,
                                                                  morpheme_index,
                                                                  max_length,
                                                                  filler=[filler])
        for ngram in prefix_ngrams:
            self.add_case(config['case_type_gloss_prefix_ngram'],
                          "|".join(map(lambda morpheme: morpheme.morpheme if morpheme.morpheme is not None else "", ngram)),
                          gloss_to)
            self.add_case(config['case_type_gloss_prefix_ngram'],
                          "|".join(map(lambda morpheme: get_glosses_concatenated(morpheme), ngram)),
                          gloss_to)

        for ngram in suffix_ngrams:
            self.add_case(config['case_type_gloss_suffix_ngram'],
                          "|".join(map(lambda morpheme: morpheme.morpheme if morpheme.morpheme is not None else "", ngram)),
                          gloss_to)
            self.add_case(config['case_type_gloss_suffix_ngram'],
                          "|".join(map(lambda morpheme: get_glosses_concatenated(morpheme), ngram)),
                          gloss_to)

        for ngram in surrounding_ngrams:
            self.add_case(config['case_type_gloss_surrounding_ngram'],
                          "|".join(map(lambda morpheme: morpheme.morpheme if morpheme.morpheme is not None else "", ngram)),
                          gloss_to)
            self.add_case(config['case_type_gloss_surrounding_ngram'],
                          "|".join(map(lambda morpheme: get_glosses_concatenated(morpheme), ngram)),
                          gloss_to)

    def add_surrounding_word_ngram_cases(self, word_index, words, gloss_to):
        """
        Adds the surrounding word and pos n-grams of a given morpheme.

        :param word_index:
        :param words:
        :param gloss_to:
        :return:
        """
        if len(words) <= 1:
            return
        for i in range(2, config['surrounding_ngram_max_length']+1):
            ngrams_of_length_i = get_consecutive_sublists_of_length_around_index(words, word_index, i)
            for ngram in ngrams_of_length_i:
                self.add_case(config['case_type_gloss_surrounding_ngram'],
                              "".join(map(lambda word: word.word if word.word is not None else "", ngram)),
                              gloss_to)
                self.add_case(config['case_type_gloss_surrounding_ngram'],
                              "".join(map(lambda word: word.pos if word.pos is not None else "", ngram)),
                              gloss_to)


def is_empty_ignore(content):
    return content is None or (config['ignore_empty_from_cases'] and content == "")
