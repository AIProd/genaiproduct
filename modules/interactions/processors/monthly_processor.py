from typing import Optional

import pandas as pd

from modules.interactions import constants
from modules.interactions.processors.timeseries_processor import TimeSeriesProcessor
from modules.interactions.utils import _append_additional_metrics


class MonthlyProcessor(TimeSeriesProcessor):

    def process(self) -> Optional[pd.DataFrame]:
        df = self.processing_data_frame.sort_values(by='timestamp')
        output_df = pd.DataFrame()

        df['month_actions_prev_year'] = df.groupby(constants.COMMON_GROUP_COLUMNS)[
            'total_actions'].shift(12)

        df['MonthGrowthPY'] = (df['total_actions'] - df['month_actions_prev_year']) / df[
            'month_actions_prev_year'] * 100

        output_df = _append_additional_metrics(df, 'month_actions_prev_year', 'month_actions_prev_year', constants.PERIOD_MONTH, output_df)
        output_df = _append_additional_metrics(df, 'MonthGrowthPY', 'MonthGrowthPY', constants.PERIOD_MONTH, output_df)

        return output_df

