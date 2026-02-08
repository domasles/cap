"""File reader for CAP configuration files."""

import logging
import yaml

from pathlib import Path
from typing import Optional, Sequence, Union


from ..domain.models.validation import ValidationIssue

logger = logging.getLogger(__name__)


class FileReaderError(Exception):
    """Raised when file reading fails."""

    def __init__(self, message: str):
        """
        Initialize FileReaderError.

        Args:
            message: Error description
        """
        self.message = message
        super().__init__(self.message)


def _collect_duplicate_keys(
    node: yaml.Node,
    path: list[str],
    duplicates: list[ValidationIssue],
) -> None:
    """Walk a YAML node tree and record paths with duplicate mapping keys."""
    if not isinstance(node, yaml.MappingNode):
        return

    seen: dict[str, bool] = {}
    for key_node, value_node in node.value:
        key = str(key_node.value)
        if key in seen:
            duplicates.append(
                ValidationIssue(
                    message=f"duplicate key: {'.'.join(path + [key])}",
                    line=key_node.start_mark.line,
                    column=key_node.start_mark.column,
                )
            )
        else:
            seen[key] = True
            _collect_duplicate_keys(value_node, path + [key], duplicates)


def _resolve_node(root: yaml.Node, loc: Sequence[Union[str, int]]) -> Optional[yaml.Node]:
    """
    Walk a composed YAML node tree following a Pydantic error location tuple.

    Returns the deepest node reachable along the path, or None.
    """
    current = root
    for part in loc:
        if isinstance(part, int):
            # Sequence index
            if isinstance(current, yaml.SequenceNode) and 0 <= part < len(current.value):
                current = current.value[part]
            else:
                return current
        else:
            # Mapping key
            key_str = str(part)
            if isinstance(current, yaml.MappingNode):
                found = False
                for key_node, value_node in current.value:
                    if str(key_node.value) == key_str:
                        current = value_node
                        found = True
                        break
                if not found:
                    return current
            else:
                return current
    return current


class FileReader:
    """Reads and parses YAML configuration files."""

    @staticmethod
    def read_yaml(file_path: str) -> dict:
        """
        Read and parse a YAML file.

        Args:
            file_path: Path to YAML file

        Returns:
            Parsed YAML as dict

        Raises:
            FileReaderError: If file cannot be read or parsed
        """
        path = Path(file_path)

        if not path.exists():
            raise FileReaderError(f"File not found: {file_path}")

        if not path.is_file():
            raise FileReaderError(f"Path is not a file: {file_path}")

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if data is None:
                raise FileReaderError(f"Empty or invalid YAML file: {file_path}")

            return data

        except yaml.YAMLError as e:
            raise FileReaderError(f"YAML parsing error in {file_path}: {e}")

        except OSError as e:
            raise FileReaderError(f"Error reading {file_path}: {e}")

    @staticmethod
    def find_cap_directory(workspace_path: str) -> Optional[Path]:
        """
        Find .cap/ directory in workspace.

        Args:
            workspace_path: Path to workspace root

        Returns:
            Path to .cap/ directory if found, None otherwise
        """
        workspace = Path(workspace_path)

        if not workspace.exists() or not workspace.is_dir():
            return None

        cap_dir = workspace / ".cap"

        if cap_dir.exists() and cap_dir.is_dir():
            return cap_dir

        return None

    @staticmethod
    def compose_yaml(file_path: str) -> Optional[yaml.Node]:
        """
        Compose a YAML file into a node tree without resolving values.

        Useful for inspecting structure with line/column information
        before values are merged by safe_load.

        Args:
            file_path: Path to YAML file

        Returns:
            Root YAML node, or None if parsing fails or file is empty
        """
        path = Path(file_path)

        if not path.exists():
            return None

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            return yaml.compose(content, Loader=yaml.SafeLoader)
        except yaml.YAMLError:
            logger.debug("YAML composition failed for %s", file_path)
            return None

    @staticmethod
    def find_duplicate_keys(root: yaml.Node) -> list[ValidationIssue]:
        """
        Find duplicate YAML mapping keys in a composed node tree.

        YAML silently overwrites duplicate keys. This method detects them
        by walking the node tree before values are merged.

        Args:
            root: Composed YAML root node (from compose_yaml)

        Returns:
            List of ValidationIssue for each duplicate key found
        """
        duplicates: list[ValidationIssue] = []
        _collect_duplicate_keys(root, [], duplicates)
        return duplicates

    @staticmethod
    def resolve_yaml_line(root: yaml.Node, loc: Sequence[Union[str, int]]) -> tuple[Optional[int], Optional[int]]:
        """
        Resolve a Pydantic error location to a line and column in a YAML node tree.

        Walks the composed node tree following the location path.
        Returns the deepest reachable node's position.

        Args:
            root: Composed YAML root node (from compose_yaml)
            loc: Pydantic error location tuple, e.g. ("dependencies", "python", 0, "name")

        Returns:
            (line, column) tuple, 0-indexed. Returns (None, None) if resolution fails.
        """
        if not loc:
            return (None, None)

        node = _resolve_node(root, loc)
        if node is not None and node.start_mark is not None:
            return (node.start_mark.line, node.start_mark.column)

        return (None, None)
