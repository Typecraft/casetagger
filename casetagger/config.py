import os.path
import glob
import json

"""
Version of the casetagger
"""
VERSION = "0.3.1"

"""
Base directory.
"""
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

"""
The primary config of the """
config = {
    """
    Verbosity level.

    0 = Print nothing (default)
    1 = Print errors and start-finish messages
    2 = Print debug messages

    """
    "verbosity_level": 0,

    """
    Should we print error details when running test?
    """
    "print_test_error_detail": False,

    """
    What format type should be output?

    Valid parameters:
        'tcxml'
        'graf'
        'plain text'
        'json'
        'yaml'
    """
    "output_type": "tcxml",

    """
    What should be tagged?

    Valid parameters:
        'pos'
        'gloss'
        'all
    """
    "tag_level": "all",

    """
    Number off passes to run when tagging.
    """
    "number_of_passes": 2,

    """
    Should we use the memory database?
    """
    "use_memory_db": False,

    """
    Should we register words which hve empty pos-tags when training?
    """
    "register_empty_pos": True,

    """
    Should we register morphemes which have empty gloss-tags when training?
    """
    "register_empty_gloss": True,

    """
    Should we adjust cases for occurrence count when training?
    """
    "adjust_for_occurrence": False,

    """
    Should we adjust cases for importance when training?
    """
    "adjust_for_importance": True,

    """
    Should we not concatenate glosses when training and tagging?

    Note that this value MUST be the same when tagging as it was when training.
    """
    "split_glosses": False,

    """
    Should we ignore cases which have a empty from_case?
    """
    "ignore_empty_from_cases": True,

    """
    Maximum length os a surrounding n-gram
    """
    "surrounding_ngram_max_length": 3,

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
    "tuple_max_length": 3,

    """
    Whether or not we should ignore creating tuples which
    has the same type.

        In the example given above TUPLE_LENGTH_MAX we would then ignore
        creating the first tuple.
    """
    "ignore_tuples_of_same_type": True,

    "case_type_pos_word": 1,
    "case_type_pos_morpheme": 2,
    "case_type_pos_surrounding_ngram": 4,
    "case_type_gloss_morph": 65536,
    "case_type_gloss_word": 131072,
    "case_type_gloss_surrounding_ngram": 262144,
    "case_importance": {
        "1": 1.0,
        "2": 1.0,
        "4": 1.0,
        "8": 1.0,
        "65536": 1.0,
        "131072": 1.0,
        "262144": 1.0,
    }
}

json_files = glob.glob(BASE_DIR + "/conf/*.json")

# Load all json config
for file_name in json_files:
    with open(file_name) as json_file:
        data = json.load(json_file)
        config.update(data)



"""
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

