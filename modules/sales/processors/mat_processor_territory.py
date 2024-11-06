from typing import Optional

import polars as pl

from modules import global_constants
from modules.global_utils import ProcessorHelper
from modules.sales import constants
from modules.sales.processors.timeseries_processor import TimeSeriesProcessor


class MATProcessorTerritory(TimeSeriesProcessor):

    def process(self) -> Optional[pl.LazyFrame]:
        lazy_frame = self.processing_lazy_frame.sort('timestamp')

        lazy_frame = lazy_frame.group_by_dynamic(
            "timestamp",
            every='1mo',
            period='1y',
            group_by=constants.TERRITORY_GROUP_COLUMNS,
        ).agg(
            pl.col(constants.COLUMN_SALES).sum().alias(constants.MOVING_ANNUAL_TOTAL_COLUMN_SALES),
            pl.col(constants.COLUMN_UNITS).sum().alias(constants.MOVING_ANNUAL_TOTAL_COLUMN_UNITS),
        )

        lazy_frame = lazy_frame.with_columns(
            pl.col(constants.MOVING_ANNUAL_TOTAL_COLUMN_SALES).shift(12, fill_value=0).over(constants.TERRITORY_GROUP_COLUMNS).alias(
                constants.MOVING_ANNUAL_TOTAL_COLUMN_LAST_YEAR_SALES
            ),
            pl.col(constants.MOVING_ANNUAL_TOTAL_COLUMN_UNITS).shift(12, fill_value=0).over(constants.TERRITORY_GROUP_COLUMNS).alias(
                constants.MOVING_ANNUAL_TOTAL_COLUMN_LAST_YEAR_UNITS
            ),
        )

        uuid_columns = {
            'employee_uuid': pl.lit(None).alias('employee_uuid'),
            'account_uuid': pl.lit(None).alias('account_uuid'),
            'hcp_uuid': pl.lit(None).alias('hcp_uuid')
        }
        lazy_frame = lazy_frame.with_columns(list(uuid_columns.values()))

        lazy_frame = lazy_frame.with_columns(
            (
                    (
                            pl.col(constants.MOVING_ANNUAL_TOTAL_COLUMN_SALES) - pl.col(
                                constants.MOVING_ANNUAL_TOTAL_COLUMN_LAST_YEAR_SALES
                            )
                    ) / pl.col(constants.MOVING_ANNUAL_TOTAL_COLUMN_LAST_YEAR_SALES) * 100
            ).alias(constants.PERCENTAGE_MOVING_ANNUAL_TOTAL_COLUMN_SALES_CHANGE_LAST_YEAR),
            (
                    (
                            pl.col(constants.MOVING_ANNUAL_TOTAL_COLUMN_UNITS) - pl.col(
                                constants.MOVING_ANNUAL_TOTAL_COLUMN_LAST_YEAR_UNITS
                            )
                    ) / pl.col(constants.MOVING_ANNUAL_TOTAL_COLUMN_LAST_YEAR_UNITS) * 100
            ).alias(constants.PERCENTAGE_MOVING_ANNUAL_TOTAL_COLUMN_UNITS_CHANGE_LAST_YEAR),
        )

        lazy_frame = lazy_frame.with_columns(
            pl.when(pl.col(constants.PERCENTAGE_MOVING_ANNUAL_TOTAL_COLUMN_SALES_CHANGE_LAST_YEAR).is_infinite() |
                    pl.col(constants.PERCENTAGE_MOVING_ANNUAL_TOTAL_COLUMN_SALES_CHANGE_LAST_YEAR).is_null() |
                    pl.col(constants.PERCENTAGE_MOVING_ANNUAL_TOTAL_COLUMN_SALES_CHANGE_LAST_YEAR).is_nan())
            .then(0)
            .otherwise(pl.col(constants.PERCENTAGE_MOVING_ANNUAL_TOTAL_COLUMN_SALES_CHANGE_LAST_YEAR))
            .round(2).alias(constants.PERCENTAGE_MOVING_ANNUAL_TOTAL_COLUMN_SALES_CHANGE_LAST_YEAR),

            pl.when(pl.col(constants.PERCENTAGE_MOVING_ANNUAL_TOTAL_COLUMN_UNITS_CHANGE_LAST_YEAR).is_infinite() |
                    pl.col(constants.PERCENTAGE_MOVING_ANNUAL_TOTAL_COLUMN_UNITS_CHANGE_LAST_YEAR).is_null() |
                    pl.col(constants.PERCENTAGE_MOVING_ANNUAL_TOTAL_COLUMN_UNITS_CHANGE_LAST_YEAR).is_nan())
            .then(0)
            .otherwise(pl.col(constants.PERCENTAGE_MOVING_ANNUAL_TOTAL_COLUMN_UNITS_CHANGE_LAST_YEAR))
            .round(2).alias(constants.PERCENTAGE_MOVING_ANNUAL_TOTAL_COLUMN_UNITS_CHANGE_LAST_YEAR),
        )

        lazy_frame = lazy_frame.drop([
            constants.MOVING_ANNUAL_TOTAL_COLUMN_LAST_YEAR_SALES,
            constants.MOVING_ANNUAL_TOTAL_COLUMN_LAST_YEAR_UNITS
        ])

        return ProcessorHelper.melt_lazy_frame(
            lazy_frame,
            [
                constants.MOVING_ANNUAL_TOTAL_COLUMN_SALES,
                constants.MOVING_ANNUAL_TOTAL_COLUMN_UNITS,
                constants.PERCENTAGE_MOVING_ANNUAL_TOTAL_COLUMN_SALES_CHANGE_LAST_YEAR,
                constants.PERCENTAGE_MOVING_ANNUAL_TOTAL_COLUMN_UNITS_CHANGE_LAST_YEAR,
            ],
            constants.COMMON_GROUP_COLUMNS + [constants.COLUMN_TIMESTAMP],
            {
                constants.MOVING_ANNUAL_TOTAL_COLUMN_SALES: constants.INDICATOR_MOVING_ANNUAL_TOTAL_SALES_TERRITORY,
                constants.MOVING_ANNUAL_TOTAL_COLUMN_UNITS: constants.INDICATOR_MOVING_ANNUAL_TOTAL_UNITS_TERRITORY,
                constants.PERCENTAGE_MOVING_ANNUAL_TOTAL_COLUMN_SALES_CHANGE_LAST_YEAR: constants.INDICATOR_MOVING_ANNUAL_TOTAL_CHANGE_PREVIOUS_YEAR_SALES_TERRITORY,
                constants.PERCENTAGE_MOVING_ANNUAL_TOTAL_COLUMN_UNITS_CHANGE_LAST_YEAR: constants.INDICATOR_MOVING_ANNUAL_TOTAL_CHANGE_PREVIOUS_YEAR_UNITS_TERRITORY,
            },
            {
                constants.MOVING_ANNUAL_TOTAL_COLUMN_SALES: constants.METRIC_CURRENCY,
                constants.MOVING_ANNUAL_TOTAL_COLUMN_UNITS: constants.METRIC_UNIT,
                constants.PERCENTAGE_MOVING_ANNUAL_TOTAL_COLUMN_SALES_CHANGE_LAST_YEAR: constants.METRIC_PERCENTAGE,
                constants.PERCENTAGE_MOVING_ANNUAL_TOTAL_COLUMN_UNITS_CHANGE_LAST_YEAR: constants.METRIC_PERCENTAGE
            },
            {
                constants.MOVING_ANNUAL_TOTAL_COLUMN_SALES: global_constants.PERIOD_MONTH,
                constants.MOVING_ANNUAL_TOTAL_COLUMN_UNITS: global_constants.PERIOD_MONTH,
                constants.PERCENTAGE_MOVING_ANNUAL_TOTAL_COLUMN_SALES_CHANGE_LAST_YEAR: global_constants.PERIOD_MONTH,
                constants.PERCENTAGE_MOVING_ANNUAL_TOTAL_COLUMN_UNITS_CHANGE_LAST_YEAR: global_constants.PERIOD_MONTH
            },
            constants.METRIC_TYPE_SALES
        )
