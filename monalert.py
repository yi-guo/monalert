from monalert.uscis import USCIS
from typing import NoReturn

import click
import os


@click.group()
def cli() -> NoReturn:
    pass


@cli.command(help="Check USCIS case status and notify upon case status change")
@click.argument("receipt_num", type=click.STRING)
def uscis(receipt_num: str) -> NoReturn:
    USCIS(receipt_num).monitor_and_alert_if_should()


if __name__ == "__main__":
    cli()
