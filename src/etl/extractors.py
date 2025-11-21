from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Protocol

import pandas as pd


class DataValidator(Protocol):
    """Protocol describing dataframe validation behavior."""

    def validate(self, dataframe: pd.DataFrame) -> None:
        ...


class Extractor(ABC):
    """Defines the interface every extractor must follow."""

    @abstractmethod
    def extract(self) -> pd.DataFrame:
        """Fetch raw data and provide it as a dataframe."""


class CSVExtractor(Extractor):
    """Loads CSV files located in the local filesystem."""

    def __init__(self, source: Path, validator: DataValidator | None = None) -> None:
        self._source = source
        self._validator = validator

    def extract(self) -> pd.DataFrame:
        dataframe = pd.read_csv(self._source, encoding="utf-8", skip_blank_lines=True)
        if self._validator is not None:
            self._validator.validate(dataframe)
        return dataframe
