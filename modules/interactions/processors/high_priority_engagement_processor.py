import pandas as pd
from datetime import datetime, timedelta
from modules.interactions.processors.processor import Processor
from modules.interactions import constants


class HighPriorityEngagementDataProcessor(Processor):
    def __init__(self, input_data_frame, days: int = 365):
        self.days = days
        super().__init__(input_data_frame)

    def _prepare_data_frame(self, data_frame: pd.DataFrame) -> pd.DataFrame:

        start_date = datetime.now() - timedelta(days=self.days)

        data_frame = data_frame[constants.COLUMN_MAPPING.keys()].rename(columns=constants.COLUMN_MAPPING)
        data_frame['timestamp'] = pd.to_datetime(data_frame['timestamp'].str.replace(' ', ''))
        data_frame = data_frame[data_frame['timestamp'] >= start_date]

        data_frame = data_frame[(data_frame['ter_target'].isin(['A', 'B'])) &
                                (data_frame['channel']!="Face to Face")]

        data_frame = data_frame[
            (data_frame['total_opens'] == 0) &
            (data_frame['total_actions'] == 0) &
            (data_frame['acceptation'] == 0) &
            (data_frame['reaction'] == 0)
            ]

        return data_frame

    def process(self) -> pd.DataFrame:

        df = self.processing_data_frame

        df['value'] = (pd.Timestamp.now() - pd.to_datetime(df['timestamp'])).dt.days
        df['metrics'] = 'days_passed_no_interaction'
        df['indicator'] = 'high_priority_engagements'
        df['period'] = 'days'

        return df






