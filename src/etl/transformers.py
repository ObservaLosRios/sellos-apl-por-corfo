from __future__ import annotations

from typing import Callable, Iterable, Sequence

import pandas as pd


def drop_completely_empty_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Removes columns that are entirely empty."""

    return dataframe.dropna(axis=1, how="all")


def drop_completely_empty_rows(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Removes rows where all values are missing."""

    return dataframe.dropna(axis=0, how="all")


def standardize_column_names(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Creates snake_case column names without leading or trailing spaces."""

    def to_snake(value: str) -> str:
        clean_value = value.strip().lower().replace(" ", "_")
        clean_value = clean_value.replace("-", "_")
        clean_value = clean_value.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
        clean_value = clean_value.replace("ñ", "n")
        while "__" in clean_value:
            clean_value = clean_value.replace("__", "_")
        return clean_value.strip("_")

    renamed_dataframe = dataframe.rename(columns={column: to_snake(str(column)) for column in dataframe.columns})
    return renamed_dataframe


def filter_rows_with_numeric_column(dataframe: pd.DataFrame, column: str) -> pd.DataFrame:
    """Keeps rows where the provided column can be converted to a number."""

    numeric_mask = pd.to_numeric(dataframe[column], errors="coerce").notna()
    return dataframe.loc[numeric_mask]


def enforce_integer_columns(dataframe: pd.DataFrame, columns: Iterable[str]) -> pd.DataFrame:
    """Casts the selected columns to integer while treating missing values as zero."""

    result = dataframe.copy()
    for column in columns:
        result[column] = pd.to_numeric(result[column], errors="coerce").fillna(0).astype(int)
    return result


def sort_by_column(dataframe: pd.DataFrame, column: str, ascending: bool = True) -> pd.DataFrame:
    """Sorts the dataframe by the provided column."""

    return dataframe.sort_values(by=column, ascending=ascending).reset_index(drop=True)


def make_column_renamer(mapping: dict[str, str]) -> Callable[[pd.DataFrame], pd.DataFrame]:
    """Factory that returns a dataframe renamer transformation."""

    def rename(dataframe: pd.DataFrame) -> pd.DataFrame:
        return dataframe.rename(columns=mapping)

    return rename


def make_numeric_row_filter(column: str) -> Callable[[pd.DataFrame], pd.DataFrame]:
    """Factory that returns a transformation keeping rows with numeric values in the target column."""

    def filter_rows(dataframe: pd.DataFrame) -> pd.DataFrame:
        return filter_rows_with_numeric_column(dataframe, column=column)

    return filter_rows


def make_integer_enforcer(columns: Iterable[str]) -> Callable[[pd.DataFrame], pd.DataFrame]:
    """Factory that returns a transformation enforcing integer dtype for the selected columns."""

    selected_columns = tuple(columns)

    def enforce(dataframe: pd.DataFrame) -> pd.DataFrame:
        return enforce_integer_columns(dataframe, columns=selected_columns)

    return enforce


def make_sorter(column: str, ascending: bool = True) -> Callable[[pd.DataFrame], pd.DataFrame]:
    """Factory that returns a transformation sorting by the column."""

    def sort(dataframe: pd.DataFrame) -> pd.DataFrame:
        return sort_by_column(dataframe, column=column, ascending=ascending)

    return sort


def make_integer_column(column: str) -> Callable[[pd.DataFrame], pd.DataFrame]:
    """Factory that casts a single column to integer."""

    def cast(dataframe: pd.DataFrame) -> pd.DataFrame:
        result = dataframe.copy()
        result[column] = pd.to_numeric(result[column], errors="coerce").fillna(0).astype(int)
        return result

    return cast


def make_non_null_filter(columns: Sequence[str]) -> Callable[[pd.DataFrame], pd.DataFrame]:
    """Factory that drops rows containing nulls for the selected columns."""

    required_columns = tuple(columns)

    def drop_nulls(dataframe: pd.DataFrame) -> pd.DataFrame:
        return dataframe.dropna(subset=required_columns, how="any")

    return drop_nulls


def make_value_filter(column: str, allowed_values: Sequence[str]) -> Callable[[pd.DataFrame], pd.DataFrame]:
    """Factory that keeps rows where the column matches allowed values."""

    allowed = {value.lower(): value for value in allowed_values}

    def filter_values(dataframe: pd.DataFrame) -> pd.DataFrame:
        mask = dataframe[column].astype(str).str.lower().isin(allowed)
        return dataframe.loc[mask]

    return filter_values
