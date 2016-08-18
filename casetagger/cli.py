# -*- coding: utf-8 -*-

import click

from casetagger.db import DbHandler


@click.command()
def main():
    db = DbHandler("nno")


if __name__ == "__main__":
    main()
