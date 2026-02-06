"""Infrastructure layer - file I/O and external dependencies."""

from .file_reader import FileReader, FileReaderError

__all__ = ["FileReader", "FileReaderError"]
