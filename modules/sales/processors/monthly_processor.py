from typing import Optional

import numpy as np
import polars as pl

from modules import global_constants
from modules.global_utils import ProcessorHelper
from modules.sales import constants
from modules.sales.processors.timeseries_processor import TimeSeriesProcessor


class MonthlyProcessor(TimeSeriesProcessor):

    def process(self) -> Optional[pl.LazyFrame]:
        lazy_frame = self.processing_lazy_frame.sort('timestamp')

        lazy_frame = lazy_frame.with_columns(
            pl.col(constants.COLUMN_SALES).shift(12, fill_value=0).over(constants.COMMON_GROUP_COLUMNS).alias(constants.COLUMN_LAST_YEAR_SALES),
            pl.col(constants.COLUMN_UNITS).shift(12, fill_value=0).over(constants.COMMON_GROUP_COLUMNS).alias(constants.COLUMN_LAST_YEAR_UNITS),
        )

        lazy_frame = lazy_frame.with_columns(
            (
                    (
                            pl.col(constants.COLUMN_SALES) - pl.col(constants.COLUMN_LAST_YEAR_SALES)
                    ) / pl.col(constants.COLUMN_LAST_YEAR_SALES) * 100
            ).alias(constants.PERCENTAGE_COLUMN_SALES_CHANGE_LAST_YEAR),
            (
                    (
                            pl.col(constants.COLUMN_UNITS) - pl.col(constants.COLUMN_LAST_YEAR_UNITS)
                    ) / pl.col(constants.COLUMN_LAST_YEAR_UNITS) * 100
            ).alias(constants.PERCENTAGE_COLUMN_UNITS_CHANGE_LAST_YEAR),
        )

        lazy_frame = lazy_frame.with_columns(
            pl.when(pl.col(constants.PERCENTAGE_COLUMN_SALES_CHANGE_LAST_YEAR).is_infinite() |
                    pl.col(constants.PERCENTAGE_COLUMN_SALES_CHANGE_LAST_YEAR).is_null() |
                    pl.col(constants.PERCENTAGE_COLUMN_SALES_CHANGE_LAST_YEAR).is_nan())
            .then(0)
            .otherwise(pl.col(constants.PERCENTAGE_COLUMN_SALES_CHANGE_LAST_YEAR))
            .round(2).alias(constants.PERCENTAGE_COLUMN_SALES_CHANGE_LAST_YEAR),

            pl.when(pl.col(constants.PERCENTAGE_COLUMN_UNITS_CHANGE_LAST_YEAR).is_infinite() |
                    pl.col(constants.PERCENTAGE_COLUMN_UNITS_CHANGE_LAST_YEAR).is_null() |
                    pl.col(constants.PERCENTAGE_COLUMN_UNITS_CHANGE_LAST_YEAR).is_nan())
            .then(0)
            .otherwise(pl.col(constants.PERCENTAGE_COLUMN_UNITS_CHANGE_LAST_YEAR))
            .round(2).alias(constants.PERCENTAGE_COLUMN_UNITS_CHANGE_LAST_YEAR),
        )

        lazy_frame = lazy_frame.drop([constants.COLUMN_LAST_YEAR_UNITS, constants.COLUMN_LAST_YEAR_SALES])

        return ProcessorHelper.melt_lazy_frame(
            lazy_frame,
            [
                constants.COLUMN_SALES,
                constants.COLUMN_UNITS,
                constants.PERCENTAGE_COLUMN_SALES_CHANGE_LAST_YEAR,
                constants.PERCENTAGE_COLUMN_UNITS_CHANGE_LAST_YEAR
            ],
            constants.COMMON_GROUP_COLUMNS,
            {
                constants.COLUMN_SALES: constants.INDICATOR_SALES,
                constants.COLUMN_UNITS: constants.INDICATOR_UNITS,
                constants.PERCENTAGE_COLUMN_SALES_CHANGE_LAST_YEAR: constants.INDICATOR_SALES_CHANGE_PREVIOUS_YEAR,
                constants.PERCENTAGE_COLUMN_UNITS_CHANGE_LAST_YEAR: constants.INDICATOR_UNITS_CHANGE_PREVIOUS_YEAR
            },
            {
                constants.COLUMN_SALES: constants.METRIC_CURRENCY,
                constants.COLUMN_UNITS: constants.METRIC_UNIT,
                constants.PERCENTAGE_COLUMN_SALES_CHANGE_LAST_YEAR: constants.METRIC_PERCENTAGE,
                constants.PERCENTAGE_COLUMN_UNITS_CHANGE_LAST_YEAR: constants.METRIC_PERCENTAGE
            },
            {
                constants.COLUMN_SALES: global_constants.PERIOD_MONTH,
                constants.COLUMN_UNITS: global_constants.PERIOD_MONTH,
                constants.PERCENTAGE_COLUMN_SALES_CHANGE_LAST_YEAR: global_constants.PERIOD_MONTH,
                constants.PERCENTAGE_COLUMN_UNITS_CHANGE_LAST_YEAR: global_constants.PERIOD_MONTH
            },
            constants.METRIC_TYPE_SALES
        )

