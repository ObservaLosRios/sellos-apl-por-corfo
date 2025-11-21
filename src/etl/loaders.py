from __future__ import annotations

from pathlib import Path

import pandas as pd


class CSVLoader:
    """Writes cleaned dataframes into CSV files."""

    def __init__(self, destination: Path) -> None:
        self._destination = destination

    def load(self, dataframe: pd.DataFrame) -> None:
        self._destination.parent.mkdir(parents=True, exist_ok=True)
        dataframe.to_csv(self._destination, index=False)

    @property
    def destination(self) -> Path:
        """Returns the path where the dataframe will be stored."""

        return self._destination
