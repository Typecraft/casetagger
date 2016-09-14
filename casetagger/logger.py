from casetagger.config import config


def log(content):
    if config['verbosity_level'] >= 1:
        print("[Log]: " + unicode(content))


def debug(content):
    if config['verbosity_level'] == 2:
        print("[Debug]: " + unicode(content))


def error(content):
    if config['verbosity_level'] >= 1:
        print("[Error]: " + unicode(content))


def critical(content):
    print("[Critical error]: " + unicode(content))
