from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import pandas as pd

from modules.sales.constants import COMMON_GROUP_COLUMNS


def filter_data_by_date(sales_data_frame: pd.DataFrame, month: int, year: int) -> pd.DataFrame:
    return sales_data_frame[
        (sales_data_frame['cases_date'].dt.month == month) & (sales_data_frame['cases_date'].dt.year == year)
        ]


def calculate_percentage_growth(current: float, previous: float) -> Optional[float]:
    if previous == 0:
        return None
    return ((current - previous) / previous) * 100


def _create_time_series(df):
    all_groups = df.groupby(COMMON_GROUP_COLUMNS)
    all_time_series = []

    for name, group in all_groups:
        resampled_group = _resample_and_add_metadata(group, name)
        all_time_series.append(resampled_group)

    df = pd.concat(all_time_series).reset_index(drop=True)
    df = df.drop_duplicates(subset=COMMON_GROUP_COLUMNS + ['cases_date'])
    return df


def _resample_and_add_metadata(group, name):
    resampled = group.set_index('cases_date').resample('MS').sum().reset_index()
    resampled['employee_uuid'] = name[0]
    resampled['account_uuid'] = name[1]
    resampled['hcp_uuid'] = name[2]
    resampled['product_name'] = name[3]
    resampled['territory'] = name[4]
    resampled['channel'] = name[5]
    resampled['category'] = name[6]
    resampled['source'] = name[7]
    return resampled


@dataclass
class FindingResult:
    account_uuid: str | None
    hcp_uuid: str | None
    employee_uuid: str | None
    type: str
    details: str
    product_name: Optional[str]
    timestamp: datetime = field(default_factory=lambda: datetime.now())
