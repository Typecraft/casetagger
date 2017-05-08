# coding: utf-8
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
BASE_DIR = os.path.dirname(__file__)

"""
The primary config
"""
config = {
    "verbosity_level": 0,
    "print_test_error_detail": False,
    "output_type": "tcxml",
    "tag_level": "all",
    "number_of_passes": 2,
    "use_memory_db": False,
    "register_empty_pos": True,
    "register_empty_gloss": True,
    "adjust_for_occurrence": False,
    "adjust_for_importance": True,
    "split_glosses": False,
    "ignore_empty_from_cases": True,
    "register_ngrams": True,
    "surrounding_ngram_max_length": 4,
    "tuple_max_length": 3,
    "ignore_tuples_of_same_type": True,
    "case_type_pos_word": 1,
    "case_type_pos_morpheme": 2,
    "case_type_pos_surrounding_ngram": 4,
    "case_type_pos_prefix_ngram": 8,
    "case_type_pos_suffix_ngram": 16,
    "case_type_pos_gloss": 32,
    "case_type_gloss_morph": 65536,
    "case_type_gloss_word": 131072,
    "case_type_gloss_surrounding_ngram": 262144,
    "case_type_gloss_prefix_ngram": 524288,
    "case_type_gloss_suffix_ngram": 1048576,
    "case_type_gloss_pos": 1 << 21,
    "reverse_names": {
        "1": "Word to POS",
        "2": "Morpheme to POS",
        "4": "Surrounding Ngram to POS",
        "8": "Prefix Ngram to POS",
        "16": "Suffix Ngram to POS",
        "32": "Gloss to POS",
        "65536": "Morph to Gloss",
        "131072": "Word to Gloss",
        "262144": "Surrounding Ngram to Gloss",
        "524288": "Prefix Ngram to Gloss",
        "1048576": "Suffix Ngram to POS",
        "2097152": "POS to Gloss"
    },
    "case_importance": {
        "1": 1.0,
        "2": 1.0,
        "4": 1.0,
        "8": 1.0,
        "16": 1.0,
        "32": 1.0,
        "65536": 1.0,
        "131072": 1.0,
        "262144": 1.0,
        "524288": 1.0,
        "1048576": 1.0,
        "2097152": 1.0
    },
    "case_groups": {
        "1": 1,
        "2": 2,
        "4": 3,
        "8": 3,
        "16": 3,
        "32": 7,
        "65536": 4,
        "131072": 5,
        "262144": 6,
        "524288": 6,
        "1048576": 6,
        "2097152": 8
    },
    "case_adjustments": {

    },
    "case_from_adjustments": {

    },
    "case_full_adjustments": {

    },
    "case_mappings": {
        "1jeg": "PN",
        "33na@FOC": "PRT",
        "1na": "CONJ",
        "1saa": "DEM",
        "17saa@N": "DEM",
        "1.": "PUN",
        "1,": "PUN",
        "1bi": "DET",
        "1ne": "CONJC",
        "1biara": "QUANT",
        "1mu": "Nrel",
        "33a@REL": "PNrel",
        "33a@RLN": "PRT",
        "33so@LOC": "LOC",
        "33so@LOC": "Nrel",
        "9so@V": "ADV",
        "1ntumi": "V",
        "1wɔn": "PN",
        "1baako": "NUM",
        "1de": "V",
        "1sɛ": "CONJ",
        "1nhyɛ": "V",
        "1ɔkra": "V",
        "1wɔntete": "V",
        "33no@DEF": "DET",
        "33no@3SG": "PN",
        "1aka": "V",
        "1adwenkyerɛ": "N",
        "1ɔkra": "N",
        "1den": "ADJ",
        "1nyinaa": "QUANT",
        "1too": "V",
        "1sɔre": "V",
        "1ɔde": "V",
        "1kɔn": "N",
        "1obiara": "PN",
        "1enti": "CONJ",
        "1enti": "CONJ",
        "1kura": "N",
        "65536kura": "",
        "65536wɔn": "3PL",
        "65536wɔm": "3PL",
        "65536wɔ": "3PL"
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
