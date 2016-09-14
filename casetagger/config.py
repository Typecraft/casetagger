import os.path

"""
"""
VERSION = "0.3.1"

"""
Verbosity level.

0 = Print nothing (default)
1 = Print errors and start-finish messages
2 = Print debug messages

"""
VERBOSITY_LEVEL = 0

"""
Error printing
"""
PRINT_TEST_ERROR_DETAIL = False

"""
Base directory of config.
"""
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

"""
Possible values:
    'tcxml',
    'plain'
"""
OUTPUT_TYPE = 'tcxml'

"""
Possible values:
    'pos',
    'gloss',
    'all'
"""
TAG_LEVEL = 'all'

"""
Possible values:
    1-n
"""
NUMBER_OF_PASSES = 2

"""
Possible values:
"""
USE_MEMORY_DB = False

"""
"""
PROBABILITY_COUNT_THRESHOLD = 10

"""
"""
REGISTER_EMPTY_POS = True

"""
"""
REGISTER_EMPTY_GLOSS = True


"""
"""
OCCURRENCE_ORDER_OF_MAGNITUDE = 1000

"""
"""
ADJUST_FOR_OCCURRENCE = True

"""
"""
ADJUST_FOR_IMPORTANCE = True

"""
TODO
"""
SPLIT_GLOSSES = False

"""
"""
IGNORE_EMPTY_FROM_CASES = True

"""
Maximal length of surrounding n-gram.
"""
SURROUNDING_NGRAM_LENGTH_MAX = 3

"""
Maximal tuple combinations to use when merging cases.

Say for example we have the cases

case1: (TYPE_1, FROM_1 => TO_1)
case2: (TYPE_1, FROM_2 => TO_1)
case3: (TYPE_3, FROM_1 => TO_1)

All tuples of length two would then be

(TYPE_1 | TYPE_1, FROM_1 + FROM_2 => TO_1)
(TYPE_1 | TYPE_3, FROM_1 + FROM_1 => TO_1)
(TYPE_1 | TYPE_3, FROM_2 + FROM_1 => TO_1)
"""
TUPLE_LENGTH_MAX = 3

"""
Whether or not we should ignore creating tuples which
has the same type.

In the example given above TUPLE_LENGTH_MAX we would then ignore
creating the first tuple.
"""
IGNORE_TUPLES_OF_SAME_TYPE = True

"""
Cases
"""
CASE_TYPE_POS_WORD = 1
CASE_TYPE_POS_WORD_CASE = 1 << 1
CASE_TYPE_POS_MORPHEME = 1 << 2
CASE_TYPE_POS_WORD_CONTAINS_CASE = 1 << 3
CASE_TYPE_POS_SURROUNDING_NGRAM = 1 << 4

CASE_TYPE_GLOSS_MORPH = 1 << 16
CASE_TYPE_GLOSS_WORD = 1 << 17
CASE_TYPE_GLOSS_WORD_CASE = 1 << 18
CASE_TYPE_GLOSS_WORD_CONTAINS_CASE = 1 << 19
CASE_TYPE_GLOSS_SURROUNDING_NGRAM = 1 << 20

"""
CASE IMPORTANCE
"""
CASE_IMPORTANCE = {
    CASE_TYPE_POS_WORD: 1.0,
    CASE_TYPE_POS_WORD_CASE: 0.2,
    CASE_TYPE_POS_MORPHEME: 0.8,
    CASE_TYPE_POS_WORD_CONTAINS_CASE: 0.8,
    CASE_TYPE_POS_SURROUNDING_NGRAM: 1.0,

    CASE_TYPE_GLOSS_MORPH: 1.0,
    CASE_TYPE_GLOSS_WORD: 0.8,
    CASE_TYPE_GLOSS_WORD_CASE: 0.2,
    CASE_TYPE_GLOSS_WORD_CONTAINS_CASE: 1.0,
    CASE_TYPE_GLOSS_SURROUNDING_NGRAM: 1.0,
}

