"""Base interface for AST language parsers."""

from abc import ABC, abstractmethod
from pathlib import Path
from src.models import FileSymbols


class BaseASTParser(ABC):
    """Abstract base class for language-specific AST symbol extractors."""

    @abstractmethod
    def parse_file(self, file_path: Path, relative_to: Path) -> FileSymbols:
        """Parse source file into structured FileSymbols."""
        pass
