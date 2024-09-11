from typing import Optional

import numpy as np
import pandas as pd

from modules.interactions import constants
from modules.interactions.processors.timeseries_processor import TimeSeriesProcessor
from modules.interactions.utils import _append_additional_metrics


class ROLQProcessor(TimeSeriesProcessor):

    def process(self) -> Optional[pd.DataFrame]:
        df = self.processing_data_frame.sort_values(by='timestamp')
        output_df = pd.DataFrame()
        df['rolling_quarterly'] = df.groupby(constants.COMMON_GROUP_COLUMNS)['total_actions'].transform(
            lambda x: x.rolling(window=3, min_periods=1).sum())

        df['rolq_prev_year'] = df.groupby(constants.COMMON_GROUP_COLUMNS)['rolling_quarterly'].shift(12)
        df['ROLQGrowthPY'] = (df['rolling_quarterly'] - df['rolq_prev_year']) / df['rolq_prev_year'] * 100
        df['ROLQGrowthPY'] = df['ROLQGrowthPY'].replace([np.inf, -np.inf], np.nan).fillna(0)

        output_df = _append_additional_metrics(df, 'rolling_quarterly', 'ROLQ', constants.PERIOD_MONTH, output_df)
        output_df = _append_additional_metrics(df, 'ROLQGrowthPY', 'ROLQGrowthPY', constants.PERIOD_MONTH, output_df)

        return output_df
