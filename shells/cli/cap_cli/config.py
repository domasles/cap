"""CLI configuration - version compatibility definitions."""

from .meta import __version__

# Maps plugin names to lists of compatible plugin versions.
# Updated on release of new CLI or plugin versions.
# When a plugin version becomes unsupported, it's removed from the list.
COMPATIBLE_PLUGINS: dict[str, list[str]] = {
    "cap-vscode": ["1.0.1", "1.1.0"],
}
