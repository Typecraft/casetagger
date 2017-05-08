from casetagger.config import config
import codecs
import sys

UTF8Writer = codecs.getwriter('utf8')
sys.stdout = UTF8Writer(sys.stdout)


def log(content):
    if config['verbosity_level'] >= 0:
        print("[Log]: " + unicode(content))


def debug(content):
    if config['verbosity_level'] == 2:
        print("[Debug]: " + unicode(content))


def error(content):
    if config['verbosity_level'] >= 1:
        print("[Error]: " + unicode(content))


def critical(content):
    print("[Critical error]: " + unicode(content))


def debug_print_cases(cases):
    if config["verbosity_level"] == 2:
        if hasattr(cases, '__iter__'):
            for case in cases:
                print(unicode(case))
        else:
            print(unicode(cases))
