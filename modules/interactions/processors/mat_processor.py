from typing import Optional

import numpy as np
import pandas as pd

from modules.interactions import constants
from modules.interactions.processors.timeseries_processor import TimeSeriesProcessor
from modules.interactions.utils import _append_additional_metrics


class MATProcessor(TimeSeriesProcessor):

    def process(self) -> Optional[pd.DataFrame]:
        df = self.processing_data_frame.sort_values(by='timestamp')
        output_df = pd.DataFrame()
        df['moving_annual_total'] = df.groupby(constants.COMMON_GROUP_COLUMNS)['total_actions'].transform(
            lambda x: x.rolling(window=12, min_periods=1).sum())

        df['mat_prev_year'] = df.groupby(constants.COMMON_GROUP_COLUMNS)['moving_annual_total'].shift(12)
        df['MATGrowthPY'] = (df['moving_annual_total'] - df['mat_prev_year']) / df['mat_prev_year'] * 100
        df['MATGrowthPY'] = df['MATGrowthPY'].replace([np.inf, -np.inf], np.nan).fillna(0)

        output_df = _append_additional_metrics(df, 'moving_annual_total', 'MAT', constants.PERIOD_MONTH, output_df)
        output_df = _append_additional_metrics(df, 'MATGrowthPY', 'MATGrowthPY', constants.PERIOD_MONTH, output_df)

        return output_df
