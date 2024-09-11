import pandas as pd

from modules.interactions import constants
from modules.interactions.processors.processor import Processor


class NextCallsProcessor(Processor):
    def _prepare_data_frame(self, data_frame: pd.DataFrame) -> pd.DataFrame:
        data_frame = data_frame[
            (data_frame['int_channel'] == 'CALLS - Veeva') &
            (data_frame['int_type'] == 'In Person') &
            (data_frame['int_acceptation'] == 1)
        ].copy()

        data_frame = data_frame[constants.COLUMN_MAPPING.keys()].rename(columns=constants.COLUMN_MAPPING)
        data_frame['timestamp'] = pd.to_datetime(
            data_frame['timestamp'].str.replace(' ', '')
        )

        return data_frame

    def process(self) -> pd.DataFrame:
        self.processing_data_frame['type'] = constants.TYPE_INTERACTIONS
        self.processing_data_frame['indicator'] = 'call_date'
        self.processing_data_frame['value'] = self.processing_data_frame['timestamp']
        self.processing_data_frame['metrics'] = constants.DATE_METRIC
        return self.processing_data_frame
