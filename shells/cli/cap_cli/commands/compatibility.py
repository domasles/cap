"""Compatibility command - Report version compatibility information."""

import json
import click

from ..meta import __version__
from ..config import COMPATIBLE_PLUGINS
from ..utils import console, print_info


@click.command()
@click.option("--json", "json_output", is_flag=True, help="Output results as JSON for programmatic use")
@click.pass_context
def compatibility(ctx, json_output):
    """
    Show version compatibility information.

    Reports which plugin versions are compatible with this CLI version.
    Used by IDE extensions to verify they can work with the installed CLI.

    Example:
        cap compatibility            # Human-readable output
        cap compatibility --json     # JSON output for extensions
    """
    data = {
        "cli_version": __version__,
        "compatible_plugins": COMPATIBLE_PLUGINS,
    }

    if json_output:
        click.echo(json.dumps(data, indent=2))
        ctx.exit(0)

    console.print(f"\n[bold]CAP CLI {__version__}[/bold]\n")

    if not COMPATIBLE_PLUGINS:
        print_info("No compatible plugins defined.")
        ctx.exit(0)

    console.print("[bold]Compatible plugins:[/bold]")

    for plugin, versions in COMPATIBLE_PLUGINS.items():
        versions_str = ", ".join(versions)
        console.print(f"  {plugin}: {versions_str}")

    console.print()
