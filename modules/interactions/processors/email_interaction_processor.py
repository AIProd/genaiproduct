from datetime import datetime, timedelta
from typing import Optional

import pandas as pd

from modules import global_constants
from modules.interactions import constants
from modules.interactions.processors.processor import Processor


class EmailInteractionProcessor(Processor):
    def __init__(self, input_data_frame, days: int = 3 * 30):
        self.days = days
        super().__init__(input_data_frame)

    def _prepare_data_frame(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        start_date = datetime.now() - timedelta(days=self.days)
        data_frame = data_frame[constants.COLUMN_MAPPING.keys()].rename(columns=constants.COLUMN_MAPPING)
        data_frame['timestamp'] = pd.to_datetime(
            data_frame['timestamp'].str.replace(' ', '')
        )
        data_frame = data_frame[data_frame['timestamp'] >= start_date]
        data_frame = data_frame[data_frame['channel'].isin(constants.EMAIL_CHANNELS)]

        return data_frame

    def process(self) -> Optional[pd.DataFrame]:
        df = self.processing_data_frame
        df['value'] = (pd.Timestamp.now() - pd.to_datetime(df['timestamp'])).dt.days
        df['metrics'] = constants.METRIC_DAYS
        df['indicator'] = constants.INDICATOR_MARKETING_EMAIL
        df['period'] = global_constants.PERIOD_DAY
        df['type'] = constants.METRIC_TYPE_INTERACTIONS

        return df[constants.COMMON_GROUP_COLUMNS + ['timestamp', 'value', 'metrics', 'indicator', 'period', 'type', 'subject']]
