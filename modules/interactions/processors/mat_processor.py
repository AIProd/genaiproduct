from typing import Optional

import polars as pl

from modules import global_constants
from modules.global_utils import ProcessorHelper
from modules.interactions import constants
from modules.interactions.processors.timeseries_processor import TimeSeriesProcessor


class MATProcessor(TimeSeriesProcessor):

    def process(self) -> Optional[pl.LazyFrame]:
        lazy_frame = self.processing_lazy_frame.sort(constants.COLUMN_TIMESTAMP)

        lazy_frame = lazy_frame.group_by_dynamic(
            "timestamp",
            every='1mo',
            period='1y',
            group_by=constants.COMMON_GROUP_COLUMNS,
        ).agg(
            pl.lit('').alias(constants.COLUMN_SUBJECT),
            pl.col(constants.COLUMN_TOTAL_ACTIONS).count().alias(constants.MOVING_ANNUAL_TOTAL_COLUMN_TOTAL_ACTIONS),
        )

        lazy_frame = lazy_frame.with_columns(
            pl.col(constants.MOVING_ANNUAL_TOTAL_COLUMN_TOTAL_ACTIONS).shift(12, fill_value=0).over(constants.COMMON_GROUP_COLUMNS).alias(
                constants.MOVING_ANNUAL_TOTAL_COLUMN_LAST_YEAR_TOTAL_ACTIONS
            ),
        )

        lazy_frame = lazy_frame.with_columns(
            (
                    (
                            (pl.col(constants.MOVING_ANNUAL_TOTAL_COLUMN_TOTAL_ACTIONS).cast(pl.Float64) -
                             pl.col(constants.MOVING_ANNUAL_TOTAL_COLUMN_LAST_YEAR_TOTAL_ACTIONS).cast(pl.Float64)) /
                            pl.col(constants.MOVING_ANNUAL_TOTAL_COLUMN_LAST_YEAR_TOTAL_ACTIONS).cast(pl.Float64)
                    ).round(4) * 100
            ).alias(constants.PERCENTAGE_MOVING_ANNUAL_TOTAL_COLUMN_TOTAL_ACTIONS_CHANGE_LAST_YEAR)
        )

        lazy_frame = lazy_frame.with_columns(
            pl.when(pl.col(constants.PERCENTAGE_MOVING_ANNUAL_TOTAL_COLUMN_TOTAL_ACTIONS_CHANGE_LAST_YEAR).is_infinite() |
                    pl.col(constants.PERCENTAGE_MOVING_ANNUAL_TOTAL_COLUMN_TOTAL_ACTIONS_CHANGE_LAST_YEAR).is_null() |
                    pl.col(constants.PERCENTAGE_MOVING_ANNUAL_TOTAL_COLUMN_TOTAL_ACTIONS_CHANGE_LAST_YEAR).is_nan())
            .then(0)
            .otherwise(pl.col(constants.PERCENTAGE_MOVING_ANNUAL_TOTAL_COLUMN_TOTAL_ACTIONS_CHANGE_LAST_YEAR))
            .round(2).alias(constants.PERCENTAGE_MOVING_ANNUAL_TOTAL_COLUMN_TOTAL_ACTIONS_CHANGE_LAST_YEAR),
        )

        lazy_frame = lazy_frame.drop([
            constants.MOVING_ANNUAL_TOTAL_COLUMN_LAST_YEAR_TOTAL_ACTIONS,
        ])

        return ProcessorHelper.melt_lazy_frame(
            lazy_frame,
            [
                constants.MOVING_ANNUAL_TOTAL_COLUMN_TOTAL_ACTIONS,
                constants.PERCENTAGE_MOVING_ANNUAL_TOTAL_COLUMN_TOTAL_ACTIONS_CHANGE_LAST_YEAR,
            ],
            constants.COMMON_GROUP_COLUMNS + [constants.COLUMN_TIMESTAMP, constants.COLUMN_SUBJECT],
            {
                constants.MOVING_ANNUAL_TOTAL_COLUMN_TOTAL_ACTIONS: constants.INDICATOR_MOVING_ANNUAL_TOTAL,
                constants.PERCENTAGE_MOVING_ANNUAL_TOTAL_COLUMN_TOTAL_ACTIONS_CHANGE_LAST_YEAR: constants.INDICATOR_MOVING_ANNUAL_TOTAL_CHANGE_PREVIOUS_YEAR
            },
            {
                constants.MOVING_ANNUAL_TOTAL_COLUMN_TOTAL_ACTIONS: constants.METRIC_INTERACTIONS,
                constants.PERCENTAGE_MOVING_ANNUAL_TOTAL_COLUMN_TOTAL_ACTIONS_CHANGE_LAST_YEAR: constants.METRIC_PERCENTAGE,
            },
            {
                constants.MOVING_ANNUAL_TOTAL_COLUMN_TOTAL_ACTIONS: global_constants.PERIOD_MONTH,
                constants.PERCENTAGE_MOVING_ANNUAL_TOTAL_COLUMN_TOTAL_ACTIONS_CHANGE_LAST_YEAR: global_constants.PERIOD_MONTH,
            },
            constants.METRIC_TYPE_INTERACTIONS
        )
