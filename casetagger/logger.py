import casetagger.config as config


def log(content):
    if config.VERBOSITY_LEVEL >= 1:
        print("[Log]: " + unicode(content))


def debug(content):
    if config.VERBOSITY_LEVEL == 2:
        print("[Debug]: " + unicode(content))


def error(content):
    if config.VERBOSITY_LEVEL >= 1:
        print("[Error]: " + unicode(content))


def critical(content):
    print("[Critical error]: " + unicode(content))
