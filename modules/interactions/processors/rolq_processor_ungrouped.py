from typing import Optional

import polars as pl

from modules import global_constants
from modules.global_utils import ProcessorHelper, remove_values_from_list
from modules.interactions import constants
from modules.interactions.processors.timeseries_processor import TimeSeriesProcessor


class ROLQProcessorUngrouped(TimeSeriesProcessor):

    def process(self) -> Optional[pl.LazyFrame]:
        group_columns = remove_values_from_list(constants.COMMON_GROUP_COLUMNS, constants.UNGROUPING_COLUMNS)
        ungrouping_columns = [pl.lit('').alias(column) for column in constants.UNGROUPING_COLUMNS]
        lazy_frame = self.processing_lazy_frame.sort(constants.COLUMN_TIMESTAMP)

        lazy_frame = lazy_frame.group_by_dynamic(
            "timestamp",
            every='1mo',
            period='1q',
            group_by=group_columns,
        ).agg(
            pl.lit('').alias(constants.COLUMN_SUBJECT),
            pl.col(constants.COLUMN_TOTAL_ACTIONS).count().alias(constants.ROLLING_QUARTER_COLUMN_TOTAL_ACTIONS),
            *ungrouping_columns,
        )

        lazy_frame = lazy_frame.with_columns(
            pl.col(constants.ROLLING_QUARTER_COLUMN_TOTAL_ACTIONS).shift(12, fill_value=0).over(group_columns).alias(
                constants.ROLLING_QUARTER_COLUMN_LAST_YEAR_TOTAL_ACTIONS
            ),
        )

        lazy_frame = lazy_frame.with_columns(
            (
                    (
                            (
                                    pl.col(
                                        constants.ROLLING_QUARTER_COLUMN_TOTAL_ACTIONS
                                    ).cast(pl.Float64)
                                    - pl.col(
                                        constants.ROLLING_QUARTER_COLUMN_LAST_YEAR_TOTAL_ACTIONS
                                    ).cast(pl.Float64)
                            ) / pl.col(
                                constants.ROLLING_QUARTER_COLUMN_LAST_YEAR_TOTAL_ACTIONS
                                ).cast(pl.Float64)
                    ).round(4) * 100
            ).alias(constants.PERCENTAGE_ROLLING_QUARTER_COLUMN_TOTAL_ACTIONS_CHANGE_LAST_YEAR),
        )

        lazy_frame = lazy_frame.with_columns(
            pl.when(
                pl.col(constants.PERCENTAGE_ROLLING_QUARTER_COLUMN_TOTAL_ACTIONS_CHANGE_LAST_YEAR).is_infinite() |
                pl.col(constants.PERCENTAGE_ROLLING_QUARTER_COLUMN_TOTAL_ACTIONS_CHANGE_LAST_YEAR).is_null() |
                pl.col(constants.PERCENTAGE_ROLLING_QUARTER_COLUMN_TOTAL_ACTIONS_CHANGE_LAST_YEAR).is_nan())
            .then(0)
            .otherwise(pl.col(constants.PERCENTAGE_ROLLING_QUARTER_COLUMN_TOTAL_ACTIONS_CHANGE_LAST_YEAR))
            .round(2).alias(constants.PERCENTAGE_ROLLING_QUARTER_COLUMN_TOTAL_ACTIONS_CHANGE_LAST_YEAR),
        )

        lazy_frame = lazy_frame.drop([
            constants.ROLLING_QUARTER_COLUMN_LAST_YEAR_TOTAL_ACTIONS,
        ])

        return ProcessorHelper.melt_lazy_frame(
            lazy_frame,
            [
                constants.ROLLING_QUARTER_COLUMN_TOTAL_ACTIONS,
                constants.PERCENTAGE_ROLLING_QUARTER_COLUMN_TOTAL_ACTIONS_CHANGE_LAST_YEAR,
            ],
            constants.COMMON_GROUP_COLUMNS + [constants.COLUMN_TIMESTAMP, constants.COLUMN_SUBJECT],
            {
                constants.ROLLING_QUARTER_COLUMN_TOTAL_ACTIONS: constants.INDICATOR_ROLLING_QUARTER_UNGROUPED,
                constants.PERCENTAGE_ROLLING_QUARTER_COLUMN_TOTAL_ACTIONS_CHANGE_LAST_YEAR: constants.INDICATOR_ROLLING_QUARTER_CHANGE_PREVIOUS_YEAR_UNGROUPED
            },
            {
                constants.ROLLING_QUARTER_COLUMN_TOTAL_ACTIONS: constants.METRIC_INTERACTIONS,
                constants.PERCENTAGE_ROLLING_QUARTER_COLUMN_TOTAL_ACTIONS_CHANGE_LAST_YEAR: constants.METRIC_PERCENTAGE,
            },
            {
                constants.ROLLING_QUARTER_COLUMN_TOTAL_ACTIONS: global_constants.PERIOD_MONTH,
                constants.PERCENTAGE_ROLLING_QUARTER_COLUMN_TOTAL_ACTIONS_CHANGE_LAST_YEAR: global_constants.PERIOD_MONTH,
            },
            constants.METRIC_TYPE_INTERACTIONS
        )