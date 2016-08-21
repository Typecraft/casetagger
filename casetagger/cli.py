# -*- coding: utf-8 -*-

import click

from casetagger.db import DbHandler
from casetagger.tagger import CaseTagger

import casetagger.config as config
import casetagger.logger as logger
from casetagger.util import separate_texts_by_languages

from tc_xml_python.parsing.parser import Parser, TypecraftParseException


@click.group()
@click.option('--debug', is_flag=True, default=False)
@click.option('-v', '--verbose', is_flag=True, default=False)
@click.version_option(version=config.VERSION)
def main(debug, verbose):
    config.VERBOSITY_LEVEL = 2 if debug else 1 if verbose else 0


@main.command()
@click.argument('files', nargs=-1, type=click.File('rb'))
@click.option('--language', default=None)
def train(files, language):
    parsed_texts = []

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
        except TypecraftParseException:
            logger.critical("Invalid format in input-file")

    if language is not None:
        CaseTagger.instantiate_db(language)

        for text in parsed_texts:
            CaseTagger.train(text)
    else:
        separated = separate_texts_by_languages(parsed_texts)

        for language, texts in separated.iteritems():
            CaseTagger.instantiate_db(language)

            for text in texts:
                CaseTagger.train(text)
