import ast
import os
import warnings
from dataclasses import dataclass, field, is_dataclass, fields
from datetime import datetime
from typing import List, Dict, TypeVar, Type, get_origin, get_args, Any, Union

import pandas as pd
import polars as pl
from langchain_openai import AzureChatOpenAI
from polars import LazyFrame

from modules import global_constants

T = TypeVar('T')


def deprecated(func):
    def wrapper(*args, **kwargs):
        warnings.warn(
            f"{func.__name__} is deprecated and will be removed in future versions.",
            DeprecationWarning,
            stacklevel=2
        )
        return func(*args, **kwargs)

    return wrapper


def remove_values_from_list(main_list, values_to_remove):
    return [x for x in main_list if x not in values_to_remove]


def safe_eval_string(data: Any) -> Union[Any, str]:
    """
    Safely evaluate a string that might contain a Python expression.
    Returns the evaluated result if possible, otherwise returns the original string.

    Args:
        data: Input data to evaluate

    Returns:
        Evaluated expression or original string if evaluation isn't possible/safe

    Examples:
        >>> safe_eval_string("{'a': 1}")  # Returns dict({'a': 1})
        >>> safe_eval_string("[1, 2, 3]") # Returns list([1, 2, 3])
        >>> safe_eval_string("hello")     # Returns "hello"
    """
    if not isinstance(data, str):
        return data

    data = data.strip().replace('nan', 'None')

    try:
        return ast.literal_eval(data)
    except (ValueError, SyntaxError):
        return data
    except Exception as e:
        print(f"Warning: Unexpected error during evaluation: {type(e).__name__}")
        return data


def get_type_origin(field_type: Any) -> Any:
    """
    Gets the origin type of a field, handling Union types.

    Args:
        field_type: The type to analyze

    Returns:
        The origin type
    """
    origin = get_origin(field_type)
    if origin is Union:
        # For Optional/Union types, get the first non-None type
        types = [t for t in get_args(field_type) if t is not type(None)]
        if types:
            return get_origin(types[0]) or types[0]
    return origin


def get_inner_type(field_type: Any) -> Any:
    """
    Gets the inner type of a collection or Union type.

    Args:
        field_type: The type to analyze

    Returns:
        The inner type
    """
    if get_origin(field_type) is Union:
        types = [t for t in get_args(field_type) if t is not type(None)]
        if types:
            return types[0]
    return get_args(field_type)[0] if get_args(field_type) else field_type


def convert_to_dataclass(cls: type[T], data: dict) -> T:
    """
    Recursively converts a dictionary into a dataclass instance.
    Handles nested dataclasses and Lists/Dicts of dataclasses.

    Args:
        cls: The target dataclass type
        data: Dictionary containing the data

    Returns:
        An instance of the specified dataclass
    """
    if data is None:
        return None

    data = safe_eval_string(data)

    if not is_dataclass(cls):
        return data

    if not isinstance(data, dict):
        raise ValueError(f"Expected dictionary, got {type(data)}")

    field_values = {}

    for field in fields(cls):
        field_name = field.name
        field_type = field.type

        if field_name not in data:
            continue

        value = data[field_name]
        value = safe_eval_string(value)
        if value is None:
            field_values[field_name] = None
            continue

        origin_type = get_type_origin(field_type)

        if origin_type == list:
            element_type = get_inner_type(field_type)
            if is_dataclass(element_type) and isinstance(value, list):
                field_values[field_name] = [
                    convert_to_dataclass(element_type, item)
                    for item in value
                ]
            else:
                field_values[field_name] = value
        elif origin_type == dict:
            key_type, value_type = get_args(field_type)
            if is_dataclass(value_type) and isinstance(value, dict):
                field_values[field_name] = {
                    k: convert_to_dataclass(value_type, v)
                    for k, v in value.items()
                }
            else:
                field_values[field_name] = value
        elif is_dataclass(get_inner_type(field_type)):
            field_values[field_name] = convert_to_dataclass(get_inner_type(field_type), value)
        else:
            field_values[field_name] = value

    return cls(**field_values)


def get_llm() -> AzureChatOpenAI:
    return AzureChatOpenAI(
        azure_endpoint=os.getenv("GP_TEAL_API"),
        openai_api_version=os.getenv("GP_TEAL_API_VERSION"),
        openai_api_key=os.getenv("GP_TEAL_API_KEY"),
        azure_deployment=os.getenv("GP_TEAL_DEPLOYMENT"),
        temperature=0,
        max_retries=1,
    )


def _safe_eval(value: str) -> List[str]:
    try:
        return eval(value)
    except (SyntaxError, NameError, TypeError):
        return []


def find_row_as_dict(df, column, value):
    matching_row = df[df[column] == value]

    if matching_row.empty:
        raise ValueError(f"No row found with {column}: {value}")

    row_dict = matching_row.iloc[0].to_dict()

    return row_dict


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
    def enforce_metrics_schema(lf: pl.LazyFrame) -> pl.LazyFrame:
        return ProcessorHelper.enforce_schema(lf, global_constants.ENFORCED_METRICS_SCHEMA)

    @staticmethod
    def enforce_schema(lf: pl.LazyFrame, schema_map: dict) -> pl.LazyFrame:
        """
        Enforce a schema on a Polars DataFrame by casting columns to specified types.
        If a column doesn't exist, create it with default values.

        Args:
        lf (pl.LazyFrame): Input DataFrame
        schema_map (dict): A dictionary mapping column names to their desired types

        Returns:
        pl.DataFrame: DataFrame with enforced schema
        """
        for col, dtype in schema_map.items():
            if col in lf.collect_schema().names():
                lf = lf.with_columns(pl.col(col).cast(dtype).alias(col))
            else:
                if dtype in [pl.Utf8, pl.String]:
                    default_value = ''
                elif dtype in [pl.Float32, pl.Float64]:
                    default_value = 0.0
                elif dtype in [pl.Int8, pl.Int16, pl.Int32, pl.Int64, pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64]:
                    default_value = 0
                else:
                    raise ValueError(f"Unsupported data type for column '{col}': {dtype}")

                lf = lf.with_columns(pl.lit(default_value).cast(dtype).alias(col))

        return lf

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
    product_name: str
    timestamp: datetime = field(default_factory=lambda: datetime.now().isoformat())
