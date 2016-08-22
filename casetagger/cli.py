# -*- coding: utf-8 -*-

import click
import copy

from casetagger.db import DbHandler
from casetagger.tagger import CaseTagger

import casetagger.config as config
import casetagger.logger as logger
from casetagger.util import separate_texts_by_languages
from tc_xml_python.models import Text, Phrase, Word

from tc_xml_python.parsing.parser import Parser, TypecraftParseException


# Some utility methods
def read_file(file):
    file_contents = ""
    while True:
        chunk = file.read(1024)

        if not chunk:
            break

        file_contents += chunk

    return file_contents


def convert_raw_text_to_texts(text_content):
    text = Text()

    for line in text_content:
        phrase = Phrase()
        phrase.phrase = line

        words_content = line.split(" ")

        for word in words_content:
            word_obj = Word()
            word_obj.word = word
            phrase.add_word(word_obj)

    return text


def get_text_words(text):
    return [word for phrase in text for word in phrase]


@click.group()
@click.option('--debug', is_flag=True, default=False)
@click.option('-v', '--verbose', is_flag=True, default=False)
@click.version_option(version=config.VERSION)
def main(debug, verbose):
    config.VERBOSITY_LEVEL = 2 if debug else 1 if verbose else 0


@main.command()
@click.option('--language', default=None)
@click.option('--raw-text', is_flag=True, default=False)
@click.option('--output-raw-text', is_flag=True, default=False)
@click.argument('files', nargs=-1, type=click.File('rb'))
@click.argument('output', type=click.File('w'))
def test(language, raw_text, output_raw_text, files, output):
    parsed_texts = []

    logger.debug("Parsing files")
    for file in files:
        file_contents = read_file(file)

        if raw_text:
            parsed_texts.append(file_contents)
        else:  # We interpret as typecraft-texts
            try:
                parsed_texts.extend(Parser.parse(file_contents))
            except TypecraftParseException, e:
                logger.critical("Invalid format in input-file: " + str(e))

    if raw_text:
        parsed_texts.extend(list(map(lambda text_content: convert_raw_text_to_texts(text_content), parsed_texts)))

    copied_texts = list(map(lambda text: copy.deepcopy(text), parsed_texts))
    logger.debug("Tagging files")

    if language is not None:
        CaseTagger.instantiate_db(language)

        for text in copied_texts:
            CaseTagger.tag_text(text)
    else:
        separated = separate_texts_by_languages(copied_texts)

        for language, texts in separated.iteritems():
            CaseTagger.instantiate_db(language)

            for text in texts:
                CaseTagger.tag_text(text)

    total_words = 0
    total_errors = 0
    for i in range(0, len(copied_texts)):
        copied_text = copied_texts[i]
        tagged_text = parsed_texts[i]

        copied_words = get_text_words(copied_text)
        tagged_words = get_text_words(tagged_text)

        total_words += len(copied_words)

        for j in range(0, len(copied_words)):
            word_1 = copied_words[j]
            word_2 = tagged_words[j]

            if word_1.pos != word_2.pos:
                total_errors += 1

    total_correct = total_words - total_errors
    percent_correct = 100 * float(total_correct) / float(total_words)
    output.write("Test finished tagging %s words. Succesfully tagged %d words (%.2f %%)" % (
            total_words, total_correct, percent_correct))


@main.command()
@click.option('--language', default=None)
@click.option('--raw-text', is_flag=True, default=False)
@click.option('--output-raw-text', is_flag=True, default=False)
@click.argument('files', nargs=-1, type=click.File('rb'))
@click.argument('output', type=click.File('w'))
def tag(language, raw_text, output_raw_text, files, output):
    parsed_texts = []

    logger.debug("Parsing files")
    for file in files:
        file_contents = read_file(file)

        if raw_text:
            parsed_texts.append(file_contents)
        else:  # We interpret as typecraft-texts
            try:
                parsed_texts.extend(Parser.parse(file_contents))
            except TypecraftParseException, e:
                logger.critical("Invalid format in input-file: " + str(e))

    if raw_text:
        parsed_texts.extend(list(map(lambda text_content: convert_raw_text_to_texts(text_content), parsed_texts)))

    if language is not None:
        CaseTagger.instantiate_db(language)

        for text in parsed_texts:
            logger.debug("Tagging text " + text.title)
            CaseTagger.tag_text(text)
    else:
        print(parsed_texts)
        separated = separate_texts_by_languages(parsed_texts)

        for language, texts in separated.iteritems():
            CaseTagger.instantiate_db(language)

            for text in texts:
                CaseTagger.tag_text(text)

    for text in parsed_texts:
        output.write(str(text))


@main.command()
@click.argument('files', nargs=-1, type=click.File('rb'))
@click.option('--language', default=None)
def train(files, language):
    parsed_texts = []

    logger.debug("Parsing files")
    for fn in files:
        file_contents = ""
        while True:
            chunk = fn.read(1024)

            if not chunk:
                break

            file_contents += chunk

        # Our file is read, we can now parse it
        try:
            parsed_texts.extend(Parser.parse(file_contents))
        except TypecraftParseException, e:
            logger.critical("Invalid format in input-file: " + str(e))

    if language is not None:
        CaseTagger.instantiate_db(language)

        for text in parsed_texts:
            CaseTagger.train(text)
    else:
        separated = separate_texts_by_languages(parsed_texts)

        for language, texts in separated.iteritems():
            CaseTagger.instantiate_db(language)

            for text in texts:
                logger.debug("Training from text " + text.title)
                CaseTagger.train(text)
