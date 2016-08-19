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

CASE_TYPE_POS_WORD = 1
CASE_TYPE_POS_WORD_CASE = 2
CASE_TYPE_POS_PREFIX_WORD = 3
CASE_TYPE_POS_SUFFIX_WORD = 4
CASE_TYPE_POS_PREFIX_POS = 5
CASE_TYPE_POS_SUFFIX_POS = 6
CASE_TYPE_POS_MORPHEME = 7
CASE_TYPE_POS_WORD_CONTAINS_CASE = 8

CASE_TYPE_GLOSS_MORPH = 9
CASE_TYPE_GLOSS_PREFIX_GLOSS = 10
CASE_TYPE_GLOSS_SUFFIX_GLOSS = 11
CASE_TYPE_GLOSS_PREFIX_MORPH = 12
CASE_TYPE_GLOSS_SUFFIX_MORPH = 13
CASE_TYPE_GLOSS_WORD = 14
CASE_TYPE_PREFIX_WORD = 15
CASE_TYPE_SUFFIX_WORD = 16

