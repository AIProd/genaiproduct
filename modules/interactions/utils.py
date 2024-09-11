from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, TypedDict, List

import pandas as pd

from modules.interactions import constants


def _create_time_series(df):
    if df.empty:
        return df

    all_groups = df.groupby(constants.COMMON_GROUP_COLUMNS)
    all_time_series = []

    for name, group in all_groups:
        resampled_group = _resample_and_add_metadata(group, name)
        all_time_series.append(resampled_group)

    df = pd.concat(all_time_series).reset_index(drop=True)
    df = df.drop_duplicates(subset=constants.COMMON_GROUP_COLUMNS + ['timestamp'])
    return df


def _resample_and_add_metadata(group, name):
    resampled = group.set_index('timestamp').resample('MS').sum().reset_index()
    resampled['employee_uuid'] = name[0]
    resampled['account_uuid'] = name[1]
    resampled['hcp_uuid'] = name[2]
    resampled['product_name'] = name[3]
    resampled['territory'] = name[4]
    resampled['channel'] = name[5]
    resampled['category'] = name[6]
    resampled['source'] = name[7]
    return resampled


class MetricResult(TypedDict):
    timestamp: pd.Series  # datetime
    period: pd.Series  # string, but treated as category
    employee_uuid: pd.Series  # Optional[str]
    hcp_uuid: pd.Series  # Optional[str]
    account_uuid: pd.Series  # Optional[str]
    product_name: pd.Series  # List[str]
    territory: pd.Series  # str
    channel: pd.Series  # str
    type: pd.Series  # str
    indicator: pd.Series  # str
    value: pd.Series  # float
    metrics: pd.Series  # str


def _process_product_name(df: pd.DataFrame) -> pd.DataFrame:
    mask: pd.Series[bool] = df['product_name'].astype(str).str.startswith('[')
    df.loc[mask, 'product_name'] = df.loc[mask, 'product_name'].apply(_safe_eval)
    df['product_name'] = df['product_name'].apply(lambda x: x if isinstance(x, list) else [])
    df = df.explode('product_name').fillna('')
    dedup_columns = constants.COMMON_GROUP_COLUMNS + [
        'rejection',
        'acceptation',
        'reaction',
        'total_opens',
        'total_actions'
    ]
    df = df.drop_duplicates(subset=dedup_columns, keep='first')

    return df


def _safe_eval(value: str) -> List[str]:
    try:
        return eval(value)
    except (SyntaxError, NameError, TypeError):
        return []


def _determine_read_status(row):
    if row['int_acceptation'] != 0 or row['int_reaction'] != 0 or row['total_opens'] != 0 or row['total_actions'] != 0:
        return 'Read'
    return 'Not Read'


def _calculate_percentages(group, numerator):
    """
    Calculate percentages for interaction metrics.
    """
    total_records = len(group)
    numerator_sum = group[numerator].sum()
    return (numerator_sum / total_records) * 100 if total_records > 0 else 0


def _append_additional_metrics(df, metric, indicator, period, new_df):
    """
    Append additional metrics to the output data frame.
    """
    metrics_df = df.groupby(constants.COMMON_GROUP_COLUMNS + ['year', 'month']).agg({metric: 'last'}).reset_index()
    metrics_df['period'] = period
    if period == constants.PERIOD_MONTH:
        metrics_df['timestamp'] = pd.to_datetime(metrics_df[['year', 'month']].assign(day=1),
                                                 errors='coerce').dt.strftime('%Y-%m-%d')
    else:
        metrics_df['timestamp'] = pd.to_datetime(metrics_df['year'].astype(str) + '-01-01',
                                                 errors='coerce').dt.strftime('%Y-%m-%d')

    metrics_df = metrics_df.dropna(subset=['timestamp'])

    metrics_df['indicator'] = indicator
    metrics_df['type'] = constants.TYPE_INTERACTIONS
    metrics_df = metrics_df.rename(columns={metric: 'value'})
    metrics_df['metrics'] = constants.METRIC_COUNT

    return pd.concat([new_df, metrics_df], ignore_index=True)


@dataclass
class FindingResult:
    account_uuid: str | None
    hcp_uuid: str | None
    employee_uuid: str | None
    type: str
    details: str
    product_name: Optional[str]
    timestamp: datetime = field(default_factory=lambda: datetime.now())
