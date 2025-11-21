from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Dict

from src.etl.config import ETLConfig
from src.etl.pipeline import ETLPipeline, DatasetResult
from src.etl.post_processors import build_yearly_summary

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the CORFO APL ETL pipeline.")
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).parent,
        help="Path to the project root where raw data files are located.",
    )
    return parser.parse_args()


def run_etl(project_root: Path) -> Dict[str, DatasetResult]:
    """Runs the ETL pipeline and returns the processed datasets."""

    config = ETLConfig.build_default(project_root)
    pipeline = ETLPipeline(config)
    results = pipeline.run()

    logging.info("Processed %d datasets", len(results))

    yearly_summary_path = build_yearly_summary(
        adhesion_by_year=results["adhesion_by_year"].dataframe,
        certification_by_year=results["certification_by_year"].dataframe,
        output_dir=config.output_dir,
    )
    logging.info("Stored yearly summary at %s", yearly_summary_path)

    return results


def main() -> None:
    args = parse_args()
    run_etl(project_root=args.project_root)


if __name__ == "__main__":
    main()
