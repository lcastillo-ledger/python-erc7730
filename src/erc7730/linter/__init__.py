from abc import ABC, abstractmethod
from collections.abc import Callable
from enum import IntEnum, auto

from erc7730.model.erc7730_descriptor import ERC7730Descriptor

from pydantic import BaseModel, FilePath


class ERC7730Linter(ABC):
    """
    Linter for ERC-7730 descriptors, inspects a (structurally valid) descriptor and emits notes, warnings, or errors.
    """

    @abstractmethod
    def lint(self, descriptor: ERC7730Descriptor, out: "OutputAdder") -> None:
        raise NotImplementedError()

    class Output(BaseModel):
        """ERC7730Linter output notice/warning/error."""

        class Level(IntEnum):
            """ERC7730Linter output level."""

            INFO = auto()
            WARNING = auto()
            ERROR = auto()

        file: FilePath | None = None
        line: int | None = None
        title: str
        message: str
        level: Level = Level.ERROR

    OutputAdder = Callable[[Output], None]
    """ERC7730Linter output sink."""
