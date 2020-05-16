from monalert.uscis import USCIS
from typing import Tuple

import click


@click.group()
def cli() -> None:
    pass


@cli.command(help="Check USCIS case status and notify upon case status change")
@click.argument(
    "receipt_nums",
    type=click.STRING,
    nargs=-1,
    required=True,
)
def uscis(receipt_nums: Tuple[str]) -> None:
    for receipt_num in receipt_nums:
        USCIS(receipt_num).monitor_and_alert_if_should()


if __name__ == "__main__":
    cli()
