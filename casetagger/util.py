from typecraft_python.models import Morpheme


def get_glosses_concatenated(morpheme):
    if not isinstance(morpheme, Morpheme):
        raise Exception("Wrong argument to get_closses_concatenated, expected morpheme, got " + str((type(morpheme))))

    return ".".join(sorted(morpheme.glosses))


def separate_texts_by_languages(texts):
    """
    Takes a list of texts and returns a new dict of texts separated by language.

    :param texts:
    :return:
    """
    dict = {}

    for text in texts:
        lan = text.language

        if not lan in dict:
            dict[lan] = []

        dict[lan].append(text)

    return dict


def get_text_words(text):
    """
    Returns all words of a text.
    :param text:
    :return:
    """
    return [word for phrase in text for word in phrase]


def get_text_morphemes(text):
    """
    Returns all morphemes of a text.

    :param text:
    :return:
    """
    return [morpheme for word in get_text_words(text) for morpheme in word]


def get_consecutive_sublists_of_length(parent_list, length):
    """
    Returns all consecutive sublists of a lists of a given length.

    For example, let parent_list = [1,2,3,4,5] and length=2.
    Then the method will return

    [1,2], [2,3], [3,4], [4,5]

    :param parent_list:
    :param length:
    :return:
    """
    sublists = []
    for i in range(len(parent_list) - length + 1):
        sublists.append(parent_list[i:i+length])
    return sublists


def get_consecutive_sublists_of_length_around_index(parent_list, index, length):
    """
    Returns all consecutive sublists of a list of a given length around an index.

    In other words, it returns the surrounding ngrams around an index, without the index
    itself.

    Example:

    parent_list = [1,2,3,4,5,6]
    index = 3 (i.e. [..., 4, ...]
    length = 3

    yields

    [1,2,3] (leading 3-gram)
    [2,3,5] (first containing 3-gram)
    [3,5,6] (second containing 3-gram)

    If the list were [1,2,3,4,5,6,7] we would also get a fourth 3-gram

    [5,6,7] (trailing 3-gram)

    :param parent_list:
    :param index:
    :param length:
    :return:
    """
    list_length = len(parent_list)
    lowest_relevant_index = max(index - length, 0)
    highest_relevant_index = min(index + length + 1, list_length)
    list_with_index_removed = parent_list[lowest_relevant_index:index] + parent_list[index+1:highest_relevant_index]

    return get_consecutive_sublists_of_length(list_with_index_removed, length)
