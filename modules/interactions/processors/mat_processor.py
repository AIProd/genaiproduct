from typing import Optional

import numpy as np
import pandas as pd

from modules import global_constants
from modules.global_utils import ProcessorHelper
from modules.interactions import constants
from modules.interactions.processors.timeseries_processor import TimeSeriesProcessor


class MATProcessor(TimeSeriesProcessor):

    def process(self) -> Optional[pd.DataFrame]:
        df = self.processing_data_frame.sort_values(by='timestamp')
        output_df = pd.DataFrame()

        df.loc[:, constants.MOVING_ANNUAL_TOTAL_COLUMN_TOTAL_ACTIONS] = df.groupby(
            constants.COMMON_GROUP_COLUMNS
        )[constants.COLUMN_TOTAL_ACTIONS].transform(
            lambda x: x.rolling(window=12, min_periods=1).sum()
        )

        df.loc[:, constants.MOVING_ANNUAL_TOTAL_COLUMN_LAST_YEAR_TOTAL_ACTIONS] = df.groupby(
            constants.COMMON_GROUP_COLUMNS
        )[constants.MOVING_ANNUAL_TOTAL_COLUMN_TOTAL_ACTIONS].shift(12)

        df[[
            constants.MOVING_ANNUAL_TOTAL_COLUMN_TOTAL_ACTIONS,
            constants.MOVING_ANNUAL_TOTAL_COLUMN_LAST_YEAR_TOTAL_ACTIONS,
        ]] = (
            df[[
                constants.MOVING_ANNUAL_TOTAL_COLUMN_TOTAL_ACTIONS,
                constants.MOVING_ANNUAL_TOTAL_COLUMN_LAST_YEAR_TOTAL_ACTIONS,
            ]].fillna(0)
        )

        df.loc[:, constants.PERCENTAGE_MOVING_ANNUAL_TOTAL_COLUMN_TOTAL_ACTIONS_CHANGE_LAST_YEAR] = (
            df.apply(lambda row: ProcessorHelper.calculate_percentage_change(
                row[constants.MOVING_ANNUAL_TOTAL_COLUMN_TOTAL_ACTIONS],
                row[constants.MOVING_ANNUAL_TOTAL_COLUMN_LAST_YEAR_TOTAL_ACTIONS]
            ), axis=1)
        )

        df = df.replace([np.inf, -np.inf], 0)

        columns_to_fill = [
            constants.PERCENTAGE_MOVING_ANNUAL_TOTAL_COLUMN_TOTAL_ACTIONS_CHANGE_LAST_YEAR,
        ]
        df[columns_to_fill] = df[columns_to_fill].fillna(0)

        output_df = ProcessorHelper.append_additional_metrics(
            df=df,
            metric=constants.MOVING_ANNUAL_TOTAL_COLUMN_TOTAL_ACTIONS,
            metric_name=constants.METRIC_INTERACTIONS,
            metric_type=constants.METRIC_TYPE_INTERACTIONS,
            indicator=constants.INDICATOR_MOVING_ANNUAL_TOTAL,
            period=global_constants.PERIOD_MONTH,
            group_by=constants.COMMON_GROUP_COLUMNS + ['year', 'month'],
            new_df=output_df
        )

        output_df = ProcessorHelper.append_additional_metrics(
            df=df,
            metric=constants.PERCENTAGE_MOVING_ANNUAL_TOTAL_COLUMN_TOTAL_ACTIONS_CHANGE_LAST_YEAR,
            metric_name=constants.METRIC_PERCENTAGE,
            metric_type=constants.METRIC_TYPE_INTERACTIONS,
            indicator=constants.INDICATOR_MOVING_ANNUAL_TOTAL_CHANGE_PREVIOUS_YEAR,
            period=global_constants.PERIOD_MONTH,
            group_by=constants.COMMON_GROUP_COLUMNS + ['year', 'month'],
            new_df=output_df
        )

        return output_df
