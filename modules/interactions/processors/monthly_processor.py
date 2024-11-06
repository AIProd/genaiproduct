from typing import Optional

import polars as pl

from modules import global_constants
from modules.global_utils import ProcessorHelper
from modules.interactions import constants
from modules.interactions.processors.timeseries_processor import TimeSeriesProcessor


class MonthlyProcessor(TimeSeriesProcessor):

    def process(self) -> Optional[pl.LazyFrame]:
        lazy_frame = self.processing_lazy_frame.sort(constants.COLUMN_TIMESTAMP)
        lazy_frame = lazy_frame.with_columns(
            pl.col(constants.COLUMN_TOTAL_ACTIONS).shift(12, fill_value=0).over(constants.COMMON_GROUP_COLUMNS).alias(
                constants.COLUMN_LAST_YEAR_TOTAL_ACTIONS),
        )

        lazy_frame = lazy_frame.with_columns(
            (
                    (
                            pl.col(constants.COLUMN_TOTAL_ACTIONS) - pl.col(constants.COLUMN_LAST_YEAR_TOTAL_ACTIONS)
                    ) / pl.col(constants.COLUMN_LAST_YEAR_TOTAL_ACTIONS) * 100
            ).alias(constants.PERCENTAGE_COLUMN_TOTAL_ACTIONS_CHANGE_LAST_YEAR),
        )

        lazy_frame = lazy_frame.with_columns(
            pl.when(pl.col(constants.PERCENTAGE_COLUMN_TOTAL_ACTIONS_CHANGE_LAST_YEAR).is_infinite() |
                    pl.col(constants.PERCENTAGE_COLUMN_TOTAL_ACTIONS_CHANGE_LAST_YEAR).is_null() |
                    pl.col(constants.PERCENTAGE_COLUMN_TOTAL_ACTIONS_CHANGE_LAST_YEAR).is_nan())
            .then(0)
            .otherwise(pl.col(constants.PERCENTAGE_COLUMN_TOTAL_ACTIONS_CHANGE_LAST_YEAR))
            .round(2).alias(constants.PERCENTAGE_COLUMN_TOTAL_ACTIONS_CHANGE_LAST_YEAR),
        )

        lazy_frame = lazy_frame.drop([constants.COLUMN_LAST_YEAR_TOTAL_ACTIONS])

        return ProcessorHelper.melt_lazy_frame(
            lazy_frame,
            [
                constants.COLUMN_TOTAL_ACTIONS,
                constants.PERCENTAGE_COLUMN_TOTAL_ACTIONS_CHANGE_LAST_YEAR,
            ],
            constants.COMMON_GROUP_COLUMNS + [constants.COLUMN_TIMESTAMP, constants.COLUMN_SUBJECT],
            {
                constants.COLUMN_TOTAL_ACTIONS: constants.INDICATOR_TOTAL_ACTIONS,
                constants.PERCENTAGE_COLUMN_TOTAL_ACTIONS_CHANGE_LAST_YEAR: constants.INDICATOR_TOTAL_ACTIONS_CHANGE_PREVIOUS_YEAR,
            },
            {
                constants.COLUMN_TOTAL_ACTIONS: constants.METRIC_INTERACTIONS,
                constants.PERCENTAGE_COLUMN_TOTAL_ACTIONS_CHANGE_LAST_YEAR: constants.METRIC_PERCENTAGE
            },
            {
                constants.COLUMN_TOTAL_ACTIONS: global_constants.PERIOD_MONTH,
                constants.PERCENTAGE_COLUMN_TOTAL_ACTIONS_CHANGE_LAST_YEAR: global_constants.PERIOD_MONTH
            },
            constants.METRIC_TYPE_INTERACTIONS
        )
