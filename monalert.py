from monalert.uscis import USCIS

import click


@click.group()
def cli() -> None:
    pass


@cli.command(help="Check USCIS case status and notify upon case status change")
@click.argument("receipt_num", type=click.STRING)
def uscis(receipt_num: str) -> None:
    USCIS(receipt_num).monitor_and_alert_if_should()


if __name__ == "__main__":
    cli()
