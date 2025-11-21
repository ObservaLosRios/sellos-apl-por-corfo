from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable

import pandas as pd


class DataValidator(ABC):
    """Base class for dataframe validation rules."""

    @abstractmethod
    def validate(self, dataframe: pd.DataFrame) -> None:
        ...


class NonEmptyFrameValidator(DataValidator):
    """Ensures the dataframe has at least one row of data."""

    def validate(self, dataframe: pd.DataFrame) -> None:
        if dataframe.empty:
            message = "The extracted dataframe is empty."
            raise ValueError(message)


class RequiredColumnsValidator(DataValidator):
    """Ensures the dataframe contains the expected columns."""

    def __init__(self, expected_columns: Iterable[str]) -> None:
        self._expected_columns = tuple(expected_columns)

    def validate(self, dataframe: pd.DataFrame) -> None:
        missing_columns = [column for column in self._expected_columns if column not in dataframe.columns]
        if missing_columns:
            message = f"Missing required columns: {missing_columns}"
            raise ValueError(message)
