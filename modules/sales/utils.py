from datetime import datetime

import polars as pl
from dateutil.relativedelta import relativedelta

from modules.sales import constants


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
        pl.col(constants.COLUMN_SALES).sum(),
        pl.col(constants.COLUMN_UNITS).sum(),
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
