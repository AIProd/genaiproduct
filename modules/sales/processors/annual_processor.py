from typing import Optional

import numpy as np
import pandas as pd

from modules import global_constants
from modules.global_utils import ProcessorHelper
from modules.sales import constants
from modules.sales.processors.timeseries_processor import TimeSeriesProcessor


class AnnualProcessor(TimeSeriesProcessor):

    def process(self) -> Optional[pd.DataFrame]:
        df = self.processing_data_frame.sort_values(by='timestamp')
        output_df = pd.DataFrame()

        df = df.groupby(constants.COMMON_GROUP_COLUMNS + ['year']).agg({
            constants.COLUMN_SALES: 'sum',
            constants.COLUMN_UNITS: 'sum',
            'timestamp': 'first'
        }).reset_index()

        df.loc[:, constants.COLUMN_LAST_YEAR_SALES] = df.groupby(
            constants.COMMON_GROUP_COLUMNS
        )[constants.COLUMN_SALES].shift(1)

        df.loc[:, constants.COLUMN_LAST_YEAR_UNITS] = df.groupby(
            constants.COMMON_GROUP_COLUMNS
        )[constants.COLUMN_UNITS].shift(1)

        df[[constants.COLUMN_LAST_YEAR_SALES, constants.COLUMN_LAST_YEAR_UNITS]] = (
            df[[constants.COLUMN_LAST_YEAR_SALES, constants.COLUMN_LAST_YEAR_UNITS]].fillna(0)
        )

        df.loc[:, constants.PERCENTAGE_COLUMN_SALES_CHANGE_LAST_YEAR] = (
            df.apply(lambda row: ProcessorHelper.calculate_percentage_change(
                row[constants.COLUMN_SALES],
                row[constants.COLUMN_LAST_YEAR_SALES]
            ), axis=1)
        )

        df.loc[:, constants.PERCENTAGE_COLUMN_UNITS_CHANGE_LAST_YEAR] = (
            df.apply(lambda row: ProcessorHelper.calculate_percentage_change(
                row[constants.COLUMN_UNITS],
                row[constants.COLUMN_LAST_YEAR_UNITS]
            ), axis=1)
        )

        df = df.replace([np.inf, -np.inf], 0)

        columns_to_fill = [
            constants.PERCENTAGE_COLUMN_SALES_CHANGE_LAST_YEAR,
            constants.PERCENTAGE_COLUMN_UNITS_CHANGE_LAST_YEAR
        ]
        df[columns_to_fill] = df[columns_to_fill].fillna(0)

        output_df = ProcessorHelper.append_additional_metrics(
            df=df,
            metric=constants.PERCENTAGE_COLUMN_SALES_CHANGE_LAST_YEAR,
            metric_name=constants.METRIC_PERCENTAGE,
            metric_type=constants.METRIC_TYPE_SALES,
            indicator=constants.INDICATOR_SALES_CHANGE_PREVIOUS_YEAR,
            period=global_constants.PERIOD_YEAR,
            group_by=constants.COMMON_GROUP_COLUMNS + ['year'],
            new_df=output_df
        )

        output_df = ProcessorHelper.append_additional_metrics(
            df=df,
            metric=constants.PERCENTAGE_COLUMN_UNITS_CHANGE_LAST_YEAR,
            metric_name=constants.METRIC_PERCENTAGE,
            metric_type=constants.METRIC_TYPE_SALES,
            indicator=constants.INDICATOR_UNITS_CHANGE_PREVIOUS_YEAR,
            period=global_constants.PERIOD_YEAR,
            group_by=constants.COMMON_GROUP_COLUMNS + ['year'],
            new_df=output_df
        )

        output_df = ProcessorHelper.append_additional_metrics(
            df=df,
            metric=constants.COLUMN_SALES,
            metric_name=constants.METRIC_CURRENCY,
            metric_type=constants.METRIC_TYPE_SALES,
            indicator=constants.INDICATOR_SALES,
            period=global_constants.PERIOD_YEAR,
            group_by=constants.COMMON_GROUP_COLUMNS + ['year'],
            new_df=output_df
        )

        output_df = ProcessorHelper.append_additional_metrics(
            df=df,
            metric=constants.COLUMN_UNITS,
            metric_name=constants.METRIC_UNIT,
            metric_type=constants.METRIC_TYPE_SALES,
            indicator=constants.INDICATOR_UNITS,
            period=global_constants.PERIOD_YEAR,
            group_by=constants.COMMON_GROUP_COLUMNS + ['year'],
            new_df=output_df
        )

        return output_df
