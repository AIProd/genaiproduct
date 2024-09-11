from abc import ABC

import pandas as pd

from modules.interactions import constants
from modules.interactions.processors.processor import Processor
from modules.interactions.utils import _process_product_name, _create_time_series


class TimeSeriesProcessor(Processor, ABC):
    def _prepare_data_frame(self, data_frame: pd.DataFrame):
        data_frame = data_frame[constants.COLUMN_MAPPING.keys()].rename(columns=constants.COLUMN_MAPPING)

        data_frame['timestamp'] = pd.to_datetime(
            data_frame['timestamp'].str.replace(' ', '')
        )

        data_frame = _process_product_name(data_frame)

        data_frame['month'] = data_frame['timestamp'].dt.month
        data_frame['year'] = data_frame['timestamp'].dt.year
        data_frame[['month', 'year']] = data_frame[['month', 'year']].replace(0, None)
        data_frame = _create_time_series(data_frame)

        return data_frame
