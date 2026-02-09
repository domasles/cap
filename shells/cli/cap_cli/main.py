"""Main CLI entry point."""

import click

from .meta import __version__
from .commands import serve, init, validate, compatibility


@click.group()
@click.version_option(__version__, "-v", "--version", prog_name="cap")
@click.help_option("-h", "--help")
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
cli.add_command(validate.validate)
cli.add_command(compatibility.compatibility)


def main():
    """Entry point for console script."""
    cli(obj={})


if __name__ == "__main__":
    main()
