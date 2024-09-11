from typing import Optional

import pandas as pd

from modules.interactions import constants
from modules.interactions.processors.timeseries_processor import TimeSeriesProcessor
from modules.interactions.utils import _calculate_percentages


class PercentageProcessor(TimeSeriesProcessor):

    def process(self) -> Optional[pd.DataFrame]:
        df = self.processing_data_frame

        output_df = pd.DataFrame()

        for metric in constants.PERCENTAGE_METRICS:
            for period in [constants.PERIOD_MONTH, constants.PERIOD_YEAR]:
                group_columns = constants.COMMON_GROUP_COLUMNS + ['year',
                                                                  'month'] if period == constants.PERIOD_MONTH else constants.COMMON_GROUP_COLUMNS + [
                    'year']
                percentage_df = df.groupby(group_columns).apply(
                    lambda x: _calculate_percentages(x, metric)).reset_index()
                percentage_df.columns = group_columns + [f'{metric}_percentage']
                percentage_df['period'] = period
                if period == constants.PERIOD_MONTH:
                    percentage_df['timestamp'] = pd.to_datetime(percentage_df[['year', 'month']].assign(day=1),
                                                                errors='coerce').dt.strftime('%Y-%m-%d')
                else:
                    percentage_df['timestamp'] = pd.to_datetime(percentage_df['year'].astype(str) + '-01-01',
                                                                errors='coerce').dt.strftime('%Y-%m-%d')

                percentage_df = percentage_df.dropna(subset=['timestamp'])

                percentage_df['indicator'] = f'{metric}_percentage'
                percentage_df['type'] = constants.TYPE_INTERACTIONS
                percentage_df = percentage_df.rename(columns={f'{metric}_percentage': 'value'})
                percentage_df['metrics'] = constants.PERCENTAGE_METRIC

                output_df = pd.concat([output_df, percentage_df], ignore_index=True)

        return output_df