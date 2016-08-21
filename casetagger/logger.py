import casetagger.config as config


def log(content):
    if config.VERBOSITY_LEVEL >= 1:
        print("[Log]: " + str(content))


def debug(content):
    if config.VERBOSITY_LEVEL == 2:
        print("[Debug]: " + str(content))


def error(content):
    if config.VERBOSITY_LEVEL >= 1:
        print("[Error]: " + str(content))


def critical(content):
    print("[Critical error]: " + str(content))
