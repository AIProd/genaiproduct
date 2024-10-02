import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from modules import global_constants

import pandas as pd
from langchain_openai import AzureChatOpenAI




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
    def process_product_name(df: pd.DataFrame, dedup_columns: List[str]) -> pd.DataFrame:
        """
        Process 'product_name' column, handle list-like strings and simple strings, and remove duplicates.

        :param pd.DataFrame df Input DataFrame with 'product_name' column
        :param List[str] dedup_columns Columns to consider for deduplication
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
    def append_additional_metrics(
            df: pd.DataFrame,
            metric: str,
            metric_name: str,
            metric_type: str,
            indicator: str,
            period: str,
            group_by: List[str],
            new_df: pd.DataFrame,
    ):
        """
        Append additional metrics to the output data frame.
        """
        metrics_df = df.groupby(group_by).agg({metric: 'last'}).reset_index()
        date_formatter = _get_date_format(period)
        metrics_df.loc[:, 'timestamp'] = pd.to_datetime(date_formatter(metrics_df), errors='coerce')

        metrics_df = metrics_df.dropna(subset=['timestamp'])

        metrics_df['indicator'] = indicator
        metrics_df['type'] = metric_type
        metrics_df = metrics_df.rename(columns={metric: 'value'})
        metrics_df['metrics'] = metric_name
        metrics_df['period'] = period
        return pd.concat([new_df, metrics_df], ignore_index=True)

@dataclass
class FindingResult:
    account_uuid: str | None
    hcp_uuid: str | None
    employee_uuid: str | None
    type: str
    details: str
    product_name: Optional[str]
    timestamp: datetime = field(default_factory=lambda: datetime.now().isoformat())
