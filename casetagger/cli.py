# -*- coding: utf-8 -*-

import click
from db.db_handler import DbHandler

@click.command()
def main():
    db = DbHandler("nno")


if __name__ == "__main__":
    main()
