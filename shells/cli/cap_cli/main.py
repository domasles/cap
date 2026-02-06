"""Main CLI entry point."""

import click

from .meta import __version__
from .commands import serve, init


@click.group()
@click.version_option(version=__version__, prog_name="cap")
@click.pass_context
def cli(ctx):
    """
    CAP (Codebase Awareness Protocol) CLI.

    Manage and serve codebase awareness information for AI coding agents.
    """
    ctx.ensure_object(dict)


# Register command groups
cli.add_command(serve.serve)
cli.add_command(init.init)


def main():
    """Entry point for console script."""
    cli(obj={})


if __name__ == "__main__":
    main()
