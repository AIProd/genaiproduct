from typing import Optional

import polars as pl

from modules import global_constants
from modules.global_utils import ProcessorHelper, remove_values_from_list
from modules.sales import constants
from modules.sales.processors.timeseries_processor import TimeSeriesProcessor


class MATProcessorUngrouped(TimeSeriesProcessor):

    def process(self) -> Optional[pl.LazyFrame]:
        group_columns = remove_values_from_list(constants.COMMON_GROUP_COLUMNS, constants.UNGROUPING_COLUMNS)
        ungrouping_columns = [pl.lit('').alias(column) for column in constants.UNGROUPING_COLUMNS]

        lazy_frame = self.processing_lazy_frame.sort('timestamp')

        lazy_frame = lazy_frame.group_by_dynamic(
            "timestamp",
            every='1mo',
            period='1y',
            group_by=group_columns,
        ).agg(
            pl.col(constants.COLUMN_SALES).sum().alias(constants.MOVING_ANNUAL_TOTAL_COLUMN_SALES),
            *ungrouping_columns
        )

        lazy_frame = lazy_frame.with_columns(
            pl.col(constants.MOVING_ANNUAL_TOTAL_COLUMN_SALES).shift(12, fill_value=0).over(group_columns).alias(
                constants.MOVING_ANNUAL_TOTAL_COLUMN_LAST_YEAR_SALES
            ),
        )

        lazy_frame = lazy_frame.with_columns(
            (
                    (
                            pl.col(constants.MOVING_ANNUAL_TOTAL_COLUMN_SALES) - pl.col(
                                constants.MOVING_ANNUAL_TOTAL_COLUMN_LAST_YEAR_SALES
                            )
                    ) / pl.col(constants.MOVING_ANNUAL_TOTAL_COLUMN_LAST_YEAR_SALES) * 100
            ).alias(constants.PERCENTAGE_MOVING_ANNUAL_TOTAL_COLUMN_SALES_CHANGE_LAST_YEAR),
        )

        lazy_frame = lazy_frame.with_columns(
            pl.when(pl.col(constants.PERCENTAGE_MOVING_ANNUAL_TOTAL_COLUMN_SALES_CHANGE_LAST_YEAR).is_infinite() |
                    pl.col(constants.PERCENTAGE_MOVING_ANNUAL_TOTAL_COLUMN_SALES_CHANGE_LAST_YEAR).is_null() |
                    pl.col(constants.PERCENTAGE_MOVING_ANNUAL_TOTAL_COLUMN_SALES_CHANGE_LAST_YEAR).is_nan())
            .then(0)
            .otherwise(pl.col(constants.PERCENTAGE_MOVING_ANNUAL_TOTAL_COLUMN_SALES_CHANGE_LAST_YEAR))
            .round(2).alias(constants.PERCENTAGE_MOVING_ANNUAL_TOTAL_COLUMN_SALES_CHANGE_LAST_YEAR),
        )

        lazy_frame = lazy_frame.drop([
            constants.MOVING_ANNUAL_TOTAL_COLUMN_LAST_YEAR_SALES,
        ])

        return ProcessorHelper.melt_lazy_frame(
            lazy_frame,
            [
                constants.MOVING_ANNUAL_TOTAL_COLUMN_SALES,
                constants.PERCENTAGE_MOVING_ANNUAL_TOTAL_COLUMN_SALES_CHANGE_LAST_YEAR,
            ],
            constants.COMMON_GROUP_COLUMNS + [constants.COLUMN_TIMESTAMP],
            {
                constants.MOVING_ANNUAL_TOTAL_COLUMN_SALES: constants.INDICATOR_MOVING_ANNUAL_TOTAL_SALES_UNGROUPED,
                constants.PERCENTAGE_MOVING_ANNUAL_TOTAL_COLUMN_SALES_CHANGE_LAST_YEAR: constants.INDICATOR_MOVING_ANNUAL_TOTAL_CHANGE_PREVIOUS_YEAR_SALES_UNGROUPED,
            },
            {
                constants.MOVING_ANNUAL_TOTAL_COLUMN_SALES: constants.METRIC_CURRENCY,
                constants.PERCENTAGE_MOVING_ANNUAL_TOTAL_COLUMN_SALES_CHANGE_LAST_YEAR: constants.METRIC_PERCENTAGE,
            },
            {
                constants.MOVING_ANNUAL_TOTAL_COLUMN_SALES: global_constants.PERIOD_MONTH,
                constants.PERCENTAGE_MOVING_ANNUAL_TOTAL_COLUMN_SALES_CHANGE_LAST_YEAR: global_constants.PERIOD_MONTH,
            },
            constants.METRIC_TYPE_SALES
        )
