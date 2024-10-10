from datetime import datetime

import pandas as pd
import polars as pl
from dateutil.relativedelta import relativedelta

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
    columns_to_replace = ['total_actions', 'total_opens', 'acceptation', 'reaction']
    df[columns_to_replace] = df[columns_to_replace].fillna(0)
    df = df.drop_duplicates(subset=constants.COMMON_GROUP_COLUMNS + ['timestamp'])
    return df


def _resample_lazy_frame(lazy_frame: pl.LazyFrame) -> pl.LazyFrame:
    previous_month_first_day = (datetime.now() - relativedelta(months=1)).replace(day=1)

    lazy_frame = lazy_frame.group_by(
        constants.COMMON_GROUP_COLUMNS + [
            pl.col('timestamp').dt.year().alias('year'),
            pl.col('timestamp').dt.month().alias('month')
        ],
        maintain_order=True
    ).agg(
        pl.col('timestamp').first(),
        pl.col(constants.COLUMN_TOTAL_ACTIONS).sum(),
        pl.col(constants.COLUMN_REJECTION).sum(),
        pl.col(constants.COLUMN_ACCEPTATION).sum(),
        pl.col(constants.COLUMN_REACTION).sum(),
    ).drop('month', 'year')

    date_ranges = (
        lazy_frame.group_by(constants.COMMON_GROUP_COLUMNS, maintain_order=True)
        .agg(pl.datetime_range(pl.col("timestamp").min(), previous_month_first_day, interval="1mo"))
        .explode("timestamp")
        .with_columns(
            pl.col('timestamp').dt.truncate('1mo'),
        )
    )

    return (
        date_ranges.join(lazy_frame, on=constants.COMMON_GROUP_COLUMNS + ['timestamp'], how="left").fill_null(0)
    )

def _resample_and_add_metadata(group, name):
    today = pd.Timestamp.today()
    last_month_end = (today - pd.offsets.MonthBegin(1)) - pd.Timedelta(days=1)

    resampled = group.set_index('timestamp').resample('MS').sum()
    resampled = (
        resampled.reindex(pd.date_range(start=resampled.index.min(), end=last_month_end, freq='MS')).reset_index()
    )

    resampled = resampled.rename(columns={'index': 'timestamp'})

    resampled['employee_uuid'] = name[0]
    resampled['account_uuid'] = name[1]
    resampled['hcp_uuid'] = name[2]
    resampled['product_name'] = name[3]
    resampled['territory'] = name[4]
    resampled['channel'] = name[5]
    resampled['category'] = name[6]
    resampled['source'] = name[7]

    return resampled


def _determine_read_status(row):
    if row['int_acceptation'] != 0 or row['int_reaction'] != 0 or row['total_opens'] != 0 or row['total_actions'] != 0:
        return 'Read'
    return 'Not Read'


