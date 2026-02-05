"""File reader for CAP configuration files."""

from pathlib import Path
from typing import Optional

import yaml


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

        except Exception as e:
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
