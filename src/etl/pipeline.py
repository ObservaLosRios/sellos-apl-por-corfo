from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List

import pandas as pd

from .config import DatasetConfig, ETLConfig
from .extractors import CSVExtractor
from .loaders import CSVLoader


@dataclass
class DatasetResult:
    """Represents the result of processing a single dataset."""

    dataset_name: str
    dataframe: pd.DataFrame
    output_path: str


class DatasetPipeline:
    """Runs the ETL process for a single dataset."""

    def __init__(
        self,
        extractor: CSVExtractor,
        transformations: Iterable[Callable[[pd.DataFrame], pd.DataFrame]],
        loader: CSVLoader,
    ) -> None:
        self._extractor = extractor
        self._transformations = list(transformations)
        self._loader = loader

    def run(self) -> DatasetResult:
        dataframe = self._extractor.extract()
        for transformation in self._transformations:
            dataframe = transformation(dataframe)
        self._loader.load(dataframe)
        return DatasetResult(
            dataset_name=self._loader.destination.stem,
            dataframe=dataframe,
            output_path=str(self._loader.destination),
        )


class ETLPipeline:
    """Coordinates multiple dataset pipelines end-to-end."""

    def __init__(self, config: ETLConfig) -> None:
        self._config = config

    def run(self) -> Dict[str, DatasetResult]:
        results: Dict[str, DatasetResult] = {}
        for dataset_name, dataset_config in self._config.dataset_configs.items():
            pipeline = self._build_dataset_pipeline(dataset_config)
            results[dataset_name] = pipeline.run()
        return results

    def _build_dataset_pipeline(self, dataset_config: DatasetConfig) -> DatasetPipeline:
        extractor = CSVExtractor(source=dataset_config.source_path)
        loader = CSVLoader(destination=dataset_config.output_path)
        return DatasetPipeline(
            extractor=extractor,
            transformations=dataset_config.transformations,
            loader=loader,
        )
