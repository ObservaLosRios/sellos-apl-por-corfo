from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List

import pandas as pd

from . import transformers


@dataclass(frozen=True)
class DatasetConfig:
    """Configuration describing how a dataset should be transformed."""

    name: str
    source_path: Path
    output_path: Path
    transformations: List[Callable[[pd.DataFrame], pd.DataFrame]] = field(
        default_factory=list
    )


@dataclass(frozen=True)
class ETLConfig:
    """Holds global configuration for the ETL pipeline."""

    base_path: Path
    output_dir: Path
    dataset_configs: Dict[str, DatasetConfig]

    @classmethod
    def build_default(cls, project_root: Path) -> "ETLConfig":
        data_dir = project_root
        output_dir = project_root / "data" / "processed"

        dataset_configs: Dict[str, DatasetConfig] = {}

        dataset_configs["adhesion_by_year"] = DatasetConfig(
            name="adhesion_by_year",
            source_path=data_dir / "APL - Adhesión x año.csv",
            output_path=output_dir / "adhesion_by_year.csv",
            transformations=[
                transformers.drop_completely_empty_columns,
                transformers.drop_completely_empty_rows,
                transformers.standardize_column_names,
                transformers.make_column_renamer(
                    {
                        "ano_adhesion_establecimiento": "year",
                        "instalaciones_adheridas": "installations",
                        "empresas_adheridas": "companies",
                    }
                ),
                transformers.make_numeric_row_filter(column="year"),
                transformers.make_integer_column(column="year"),
                transformers.make_integer_enforcer(["installations", "companies"]),
                transformers.make_sorter(column="year"),
            ],
        )

        dataset_configs["adhesion_by_sector"] = DatasetConfig(
            name="adhesion_by_sector",
            source_path=data_dir / "APL - Adhesión x sector.csv",
            output_path=output_dir / "adhesion_by_sector.csv",
            transformations=[
                transformers.drop_completely_empty_columns,
                transformers.drop_completely_empty_rows,
                transformers.standardize_column_names,
                transformers.make_column_renamer(
                    {
                        "sector_economico": "sector",
                        "instalaciones_adheridas_por_sector": "installations",
                    }
                ),
                transformers.make_integer_column(column="installations"),
                transformers.make_sorter(column="installations", ascending=False),
            ],
        )

        dataset_configs["adhesion_by_size"] = DatasetConfig(
            name="adhesion_by_size",
            source_path=data_dir / "APL - Adhesión x tamaño.csv",
            output_path=output_dir / "adhesion_by_size.csv",
            transformations=[
                transformers.drop_completely_empty_columns,
                transformers.drop_completely_empty_rows,
                transformers.standardize_column_names,
                transformers.make_column_renamer(
                    {
                        "tamano_empresa": "company_size",
                        "empresas": "companies",
                        "instalacion": "installations",
                    }
                ),
                transformers.make_non_null_filter(["company_size"]),
                transformers.make_value_filter(
                    column="company_size",
                    allowed_values=["PEQUEÑA", "MICRO", "MEDIANA", "GRANDE", "SSPP"],
                ),
                transformers.make_integer_enforcer(["companies", "installations"]),
                transformers.make_sorter(column="companies", ascending=False),
            ],
        )

        dataset_configs["certification_by_year"] = DatasetConfig(
            name="certification_by_year",
            source_path=data_dir / "APL - Certificación x año.csv",
            output_path=output_dir / "certification_by_year.csv",
            transformations=[
                transformers.drop_completely_empty_columns,
                transformers.drop_completely_empty_rows,
                transformers.standardize_column_names,
                transformers.make_column_renamer(
                    {
                        "ano_certificacion_del_establecimiento": "year",
                        "instalaciones_certificadas": "installations",
                        "empresas_certificadas": "companies",
                    }
                ),
                transformers.make_numeric_row_filter(column="year"),
                transformers.make_integer_column(column="year"),
                transformers.make_integer_enforcer(["installations", "companies"]),
                transformers.make_sorter(column="year"),
            ],
        )

        dataset_configs["certification_by_sector"] = DatasetConfig(
            name="certification_by_sector",
            source_path=data_dir / "APL - Certificación x sector.csv",
            output_path=output_dir / "certification_by_sector.csv",
            transformations=[
                transformers.drop_completely_empty_columns,
                transformers.drop_completely_empty_rows,
                transformers.standardize_column_names,
                transformers.make_column_renamer(
                    {
                        "sector_economico": "sector",
                        "instalaciones_certificadas_por_sector": "installations",
                    }
                ),
                transformers.make_integer_column(column="installations"),
                transformers.make_sorter(column="installations", ascending=False),
            ],
        )

        return cls(
            base_path=project_root,
            output_dir=output_dir,
            dataset_configs=dataset_configs,
        )
