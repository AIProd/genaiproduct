import pandas as pd

from modules import global_constants
from modules.global_utils import ProcessorHelper
from modules.interactions import constants
from modules.interactions.processors.processor import Processor


class CallProcessor(Processor):
    def _prepare_data_frame(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        data_frame = data_frame[
            (data_frame['int_channel'] == 'CALLS - Veeva') &
            (data_frame['int_type'] == 'In Person') &
            (data_frame['int_acceptation'] == 1)
        ]

        data_frame = data_frame[constants.COLUMN_MAPPING.keys()].rename(columns=constants.COLUMN_MAPPING)
        data_frame['timestamp'] = pd.to_datetime(
            data_frame['timestamp'].str.replace(' ', '')
        )

        return data_frame

    def process(self) -> pd.DataFrame:
        df = self.processing_data_frame.sort_values(by='timestamp')

        df['type'] = constants.METRIC_TYPE_INTERACTIONS
        df['indicator'] = constants.INDICATOR_CALL
        df['value'] = df['timestamp'].apply(lambda x: x.isoformat())
        df['metrics'] = constants.METRIC_DATE
        df['period'] = global_constants.PERIOD_DAY

        return df[constants.COMMON_GROUP_COLUMNS + ['timestamp', 'value', 'metrics', 'indicator', 'period', 'type', 'subject']]
