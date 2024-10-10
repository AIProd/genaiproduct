import os
from dataclasses import dataclass, field
from datetime import datetime
from functools import wraps
from typing import Optional, List, Dict

import polars as pl
from polars import LazyFrame

from modules import global_constants

import pandas as pd
from langchain_openai import AzureChatOpenAI
import warnings


def deprecated(func):
    def wrapper(*args, **kwargs):
        warnings.warn(
            f"{func.__name__} is deprecated and will be removed in future versions.",
            DeprecationWarning,
            stacklevel=2
        )
        return func(*args, **kwargs)

    return wrapper


def get_llm() -> AzureChatOpenAI:
    return AzureChatOpenAI(
        azure_endpoint=os.getenv("GP_TEAL_API"),
        openai_api_version=os.getenv("GP_TEAL_API_VERSION"),
        openai_api_key=os.getenv("GP_TEAL_API_KEY"),
        azure_deployment=os.getenv("GP_TEAL_DEPLOYMENT"),
        max_retries=1,
    )


def _safe_eval(value: str) -> List[str]:
    try:
        return eval(value)
    except (SyntaxError, NameError, TypeError):
        return []


def _get_date_format(period):
    return {
        global_constants.PERIOD_DAY: lambda df: df['timestamp'].dt.isoformat(),
        global_constants.PERIOD_MONTH: lambda df: df[['year', 'month']].assign(day=1),
        global_constants.PERIOD_YEAR: lambda df: df['year'].astype(str) + '-01-01'
    }.get(period, lambda df: df['year'].astype(str) + '-01-01')


class ProcessorHelper:
    @staticmethod
    def calculate_percentages(group, numerator):
        """
        Calculate percentages for interaction metrics.

        :param group: Group of records to calculate percentage for
        :param numerator: Column name to use as numerator in calculation
        :return: Calculated percentage or 0 if no records
        """
        total_records = len(group)
        numerator_sum = group[numerator].sum()
        return (numerator_sum / total_records) * 100 if total_records > 0 else 0

    @staticmethod
    def calculate_percentage_change(current, previous):
        if previous == 0:
            return 100 if current > 0 else 0
        else:
            return ((current - previous) / previous) * 100

    @staticmethod
    @deprecated
    def process_product_name(df: pd.DataFrame, dedup_columns: List[str]) -> pd.DataFrame:
        """
        Process 'product_name' column, handle list-like strings and simple strings, and remove duplicates.

        :param df: pd.DataFrame df Input DataFrame with 'product_name' column
        :param dedup_columns: List[str] dedup_columns Columns to consider for deduplication
        :return pd.DataFrame Processed DataFrame with exploded and deduplicated product names
        """

        def process_name(x):
            if isinstance(x, str):
                if x.startswith('['):
                    try:
                        return _safe_eval(x)
                    except:
                        return [x]
                else:
                    return [x]
            elif isinstance(x, list):
                return x
            else:
                return []

        df['product_name'] = df['product_name'].apply(process_name)
        df = df.explode('product_name').fillna('')
        df = df.drop_duplicates(subset=dedup_columns, keep='first')

        return df

    @staticmethod
    def explode_product_name(lazy_frame: pl.LazyFrame) -> LazyFrame:
        """
        Process 'product_name' column, handle list-like strings and simple strings, and remove duplicates.

        :param lazy_frame: pl.LazyFrame Input LazyFrame with 'product_name' column
        :return pl.LazyFrame Processed LazyFrame with exploded  product names
        """

        return lazy_frame.with_columns(
            pl.col('product_name').str.replace_many({'[': '', ']': '', ' ': '', '\'': ''}).str.split(','),
        ).explode('product_name')

    @staticmethod
    def fix_grouping_none_values(lazy_frame: pl.LazyFrame, group_by_columns: List[str]) -> pl.LazyFrame:
        return lazy_frame.with_columns(
            pl.col(group_by_column).fill_null('') for group_by_column in group_by_columns
        )

    @staticmethod
    def melt_lazy_frame(
            lf: pl.LazyFrame,
            value_columns: List[str],
            columns_to_keep: List[str],
            indicator_mapping: Dict[str, str],
            metric_mapping: Dict[str, str],
            period_mapping: Dict[str, str],
            metric_type: str,
    ) -> pl.LazyFrame:
        """
        Transform a Polars LazyFrame into a specific format.

        :param columns_to_keep:
        :param metric_type:
        :param period_mapping:
        :param lf: (pl.LazyFrame): Input LazyFrame
        :param value_columns: (List[str]): List of column names to be transformed
        :param indicator_mapping: (Dict[str, str]): Mapping of original column names to new indicator names
        :param metric_mapping: (Dict[str, str]): Mapping of indicators to their corresponding metric values

        Returns:
        :return pl.LazyFrame: Transformed LazyFrame
        """
        melted = lf.melt(
            id_vars=columns_to_keep,
            value_vars=value_columns,
            variable_name="indicator",
            value_name="value"
        )

        unique_indicators = list(set(indicator_mapping.keys()) | set(value_columns))
        mapping_data = {
            "original_indicator": unique_indicators,
            "new_indicator": [indicator_mapping.get(col, col) for col in unique_indicators],
            "metric": [metric_mapping.get(col, "unknown") for col in unique_indicators],
            "period": [period_mapping.get(col, "unknown") for col in unique_indicators],
            "metric_type": metric_type
        }
        mapping_lf = pl.LazyFrame(mapping_data)

        result = (
            melted.join(
                mapping_lf,
                left_on="indicator",
                right_on="original_indicator",
                how="left"
            )
            .with_columns([
                pl.col("new_indicator").alias("indicator"),
                pl.col("metric"),
                pl.col("period"),
                pl.col('metric_type')
            ])
            .drop(["new_indicator"])
        )

        return ProcessorHelper.select_metric_columns(result, columns_to_keep)

    @staticmethod
    def select_metric_columns(ldf: pl.LazyFrame, columns_to_keep: list[str]) -> pl.LazyFrame:
        return ldf.select(columns_to_keep + global_constants.METRIC_VALUE_COLUMNS)

@dataclass
class FindingResult:
    account_uuid: str | None
    hcp_uuid: str | None
    employee_uuid: str | None
    type: str
    details: str
    product_name: Optional[str]
    timestamp: datetime = field(default_factory=lambda: datetime.now().isoformat())
