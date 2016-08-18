import os.path

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
NUMBER_OF_PASSES = 1

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

counter = 0
CASE_TYPE_POS_WORD = ++counter
CASE_TYPE_POS_WORD_CASE = ++counter
CASE_TYPE_POS_PREFIX_WORD = ++counter
CASE_TYPE_POS_SUFFIX_WORD = ++counter
CASE_TYPE_POS_PREFIX_POS = ++counter
CASE_TYPE_POS_SUFFIX_POS = ++counter
CASE_TYPE_POS_MORPHEME = ++counter
CASE_TYPE_POS_WORD_CONTAINS_CASE = ++counter

CASE_TYPE_GLOSS_MORPH = ++counter
CASE_TYPE_GLOSS_PREFIX_GLOSS = ++counter
CASE_TYPE_GLOSS_SUFFIX_GLOSS = ++counter
CASE_TYPE_GLOSS_PREFIX_MORPH = ++counter
CASE_TYPE_GLOSS_SUFFIX_MORPH = ++counter
CASE_TYPE_GLOSS_WORD = ++counter
CASE_TYPE_PREFIX_WORD = ++counter
CASE_TYPE_SUFFIX_WORD = ++counter

