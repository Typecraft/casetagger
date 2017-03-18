from typecraft_python.models import Morpheme, Word

from casetagger.config import config
from casetagger.util import get_text_morphemes
from casetagger.util import get_text_words


class TestWordResult(object):
    """
    Class representing a result for a word in a test-run.
    """
    def __init__(
        self,
        word_1,
        word_2
    ):
        assert isinstance(word_1, Word)
        assert isinstance(word_1, Word)

        self.word_1 = word_1
        self.word_2 = word_2

        self.equal = self.word_1.pos == self.word_2.pos

    def __str__(self):
        return u"Word: %s, POS: %s == %s: %s" \
               % (
                   self.word_1.word,
                   self.word_1.pos,
                   self.word_2.pos,
                   "TRUE" if self.equal else "FALSE"
               )


class TestMorphemeResult(object):
    """
    Class representing a result for a morpheme in a test-run.
    """
    def __init__(
        self,
        morph_1,
        morph_2
    ):
        assert isinstance(morph_1, Morpheme)
        assert isinstance(morph_2, Morpheme)
        self.morph_1 = morph_1
        self.morph_2 = morph_2

        self.equal = morph_1.get_glosses_concatenated(sort=True) == morph_2.get_glosses_concatenated(sort=True)

    def __str__(self):
        return u"Morpheme: %s, Glosses: %s == %s: %s" \
               % (
                   self.morph_1.morpheme,
                   self.morph_1.get_glosses_concatenated(),
                   self.morph_2.get_glosses_concatenated(),
                   "TRUE" if self.equal else "FALSE"
               )


class TestResult(object):
    """
    Class representing the results of a test-run.
    """
    def __init__(
        self,
        title="SomeTest",
        word_results=[],
        morpheme_results=[]
    ):
        self.title = title
        self.words_total = len(word_results)
        self.morphemes_total = len(morpheme_results)
        self.correct_words = list(filter(lambda x: x.equal, word_results))
        self.correct_morphemes = list(filter(lambda x: x.equal, morpheme_results))
        self.wrong_words = list(filter(lambda x: not x.equal, word_results))
        self.wrong_morphemes = list(filter(lambda x: not x.equal, morpheme_results))

    def word_accuracy(self):
        if self.words_total == 0:
            return -1
        return 100 * float(len(self.correct_words)) / float(self.words_total)

    def morpheme_accuracy(self):
        if self.morphemes_total == 0:
            return -1
        return 100 * float(len(self.correct_morphemes)) / float(self.morphemes_total)

    def __str__(self):
        res = u" \
            \nTestResult for %s:\n\
                Words total = %s\n\
                Morphemes total = %s\n\
                Words correctly tagged = %s (%.2f %%)\n\
                Morphemes correctly tagged = %s (%.2f %%)\n\
            " % (self.title, self.words_total, self.morphemes_total,
                 len(self.correct_words), self.word_accuracy(),
                 len(self.correct_morphemes), self.morpheme_accuracy())

        res += u"\nCorrect words:\n"
        for word_result in self.correct_words:
            res += u"\t"
            res += unicode(word_result)
            res += u"\n"
        res += u"Wrong words:\n"
        for word_result in self.wrong_words:
            res += u"\t"
            res += unicode(word_result)
            res += u"\n"

        res += u"\nCorrect morphemes\n"
        for morph_result in self.correct_morphemes:
            res += u"\t"
            res += unicode(morph_result)
            res += u"\n"
        res += u"Wrong Morphemes:\n"
        for word_result in self.wrong_morphemes:
            res += u"\t"
            res += unicode(word_result)
            res += u"\n"

        return res

    @staticmethod
    def from_data(text_1, text_2):
        words_1 = get_text_words(text_1)
        words_2 = get_text_words(text_2)

        morphemes_1 = get_text_morphemes(text_1)
        morphemes_2 = get_text_morphemes(text_2)

        words = map(lambda x: TestWordResult(x[0], x[1]), zip(words_1, words_2))
        morphemes = map(lambda x: TestMorphemeResult(x[0], x[1]), zip(morphemes_1, morphemes_2))

        return TestResult(
            text_1.title,
            words,
            morphemes
        )

    @staticmethod
    def merge(this, other):
        if this is None:
            return other

        if other is None:
            return this

        this.wrong_words.extend(other.wrong_words)
        this.wrong_morphemes.extend(other.wrong_morphemes)

        return TestResult(this.title + " | " + other.title,
                          this.words_total + other.words_total,
                          this.morphemes_total + other.morphemes_total,
                          this.correct_words + other.correct_words,
                          this.correct_morphemes + other.correct_morphemes,
                          this.wrong_words,
                          this.wrong_morphemes)


