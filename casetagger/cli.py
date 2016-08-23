# -*- coding: utf-8 -*-

import click
import copy

from casetagger.db import DbHandler
from casetagger.models import TestResult
from casetagger.tagger import CaseTagger

import casetagger.config as config
import casetagger.logger as logger
from casetagger.util import separate_texts_by_languages
from tc_xml_python.models import Text, Phrase, Word

from tc_xml_python.parsing.parser import Parser, TypecraftParseException


# Some utility methods
def input_to_texts(files, input_is_rawtext):
    """
    Converts given input to a list of files.

    :param files:
    :param input_is_rawtext:
    :return:
    """
    parsed_texts = []
    for file in files:
        file_contents = read_file(file)

        if input_is_rawtext:
            parsed_texts.append(file_contents)
        else:  # We interpret as typecraft-texts
            try:
                parsed_texts.extend(Parser.parse(file_contents))
            except TypecraftParseException, e:
                logger.critical("Invalid format in input-file: " + str(e))
                exit(1)

    if input_is_rawtext:
        parsed_texts.extend(list(map(lambda text_content: convert_raw_text_to_texts(text_content), parsed_texts)))

    return parsed_texts


def read_file(file):
    """
    Reads a file.

    :param file:
    :return:
    """
    file_contents = ""
    while True:
        chunk = file.read(1024)

        if not chunk:
            break

        file_contents += chunk

    return file_contents


def convert_raw_text_to_texts(text_content):
    """
    Converts a raw-text input to a set of Text objects.

    :param text_content:
    :return:
    """
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




@click.group()
@click.option('--debug', is_flag=True, default=False)
@click.option('-v', '--verbose', is_flag=True, default=False)
@click.option('--memory', is_flag=True, default=False)
@click.version_option(version=config.VERSION)
def main(debug, verbose, memory):
    config.VERBOSITY_LEVEL = 2 if debug else 1 if verbose else 0
    config.USE_MEMORY_DB = memory


@main.command()
@click.option('--language', default=None)
@click.option('--raw-text', is_flag=True, default=False)
@click.option('--output-raw-text', is_flag=True, default=False)
@click.option('--print-test-details', is_flag=True, default=False)
@click.argument('files', nargs=-1, type=click.File('rb'))
def test(language, raw_text, output_raw_text, print_test_details, files):
    if len(files) == 0:
        logger.critical("No input files")
        exit(1)

    if print_test_details:
        config.PRINT_TEST_ERROR_DETAIL = True

    logger.debug("Parsing files")
    parsed_texts = input_to_texts(files, raw_text)
    logger.debug("Tagging files")

    test_results = []

    if language is not None:
        CaseTagger.instantiate_db(language)

        for text in parsed_texts:
            test_results.append(CaseTagger.test_text(text))
    else:
        separated = separate_texts_by_languages(parsed_texts)

        for language, texts in separated.iteritems():
            CaseTagger.instantiate_db(language)

            for text in texts:
                test_results.append(CaseTagger.test_text(text))

    for result in test_results:
        click.echo("\n\n" + unicode(result))

    total_result = reduce(lambda x, y: TestResult.merge(x, y), test_results)

    click.echo("\n\n" + unicode(total_result))


@main.command()
@click.option('--language', default=None)
@click.option('--raw-text', is_flag=True, default=False)
@click.option('--output-raw-text', is_flag=True, default=False)
@click.argument('files', nargs=-1, type=click.File('rb'))
def tag(language, raw_text, output_raw_text, files):
    parsed_texts = []

    if len(files) == 0:
        logger.critical("No input files")
        exit(1)

    logger.debug("Parsing files")
    parsed_texts = input_to_texts(files, raw_text)

    if language is not None:
        CaseTagger.instantiate_db(language)

        for text in parsed_texts:
            logger.debug("Tagging text " + text.title)
            CaseTagger.tag_text(text)
    else:
        separated = separate_texts_by_languages(parsed_texts)

        for language, texts in separated.iteritems():
            CaseTagger.instantiate_db(language)

            for text in texts:
                CaseTagger.tag_text(text)

    click.echo(Parser.write((parsed_texts)))


@main.command()
@click.argument('files', nargs=-1, type=click.File('rb'))
@click.option('--language', default=None)
def train(files, language):

    if len(files) == 0:
        logger.critical("No input files")
        exit(1)

    parsed_texts = input_to_texts(files, False)

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
