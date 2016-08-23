from tc_xml_python.models import Morpheme


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
