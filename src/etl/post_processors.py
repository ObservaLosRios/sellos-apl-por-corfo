from __future__ import annotations

from pathlib import Path

import pandas as pd


def build_yearly_summary(
    adhesion_by_year: pd.DataFrame,
    certification_by_year: pd.DataFrame,
    output_dir: Path,
) -> Path:
    """Creates a consolidated yearly summary and stores it as CSV."""

    merged = adhesion_by_year.merge(
        certification_by_year,
        on="year",
        how="outer",
        suffixes=("_adhesion", "_certification"),
    )

    int_columns = [
        "year",
        "installations_adhesion",
        "companies_adhesion",
        "installations_certification",
        "companies_certification",
    ]
    for column in int_columns:
        merged[column] = pd.to_numeric(merged[column], errors="coerce").fillna(0).astype(int)

    merged = merged.sort_values(by="year").reset_index(drop=True)

    output_path = output_dir / "yearly_summary.csv"
    output_dir.mkdir(parents=True, exist_ok=True)
    merged.to_csv(output_path, index=False)
    return output_path
