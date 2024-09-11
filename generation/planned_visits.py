import pandas as pd
from datetime import datetime

from generation.constants import BUSINESS_DAYS_COUNT, PERIOD_DAILY


class PlannedVisitsProcessor:
    def __init__(self, input_data_frame: pd.DataFrame):
        self.input_data_frame = input_data_frame
        self.processing_data_frame = pd.DataFrame()
        self.output_data_frame = pd.DataFrame()

    def process(self) -> pd.DataFrame:
        self._prepare_data_frame()
        self._filter_for_upcoming_visits()
        self._calculate_planned_visits()
        return self.output_data_frame

    def _prepare_data_frame(self) -> None:
        columns = ['hcp_uuid', 'employee_uuid', 'account_uuid', 'timestamp']
        self.processing_data_frame = self.input_data_frame[
            (self.input_data_frame['indicator'] == 'call_date')
        ][columns]

    def _filter_for_upcoming_visits(self) -> None:
        now = datetime.now()
        business_days = pd.date_range(start=now, periods=BUSINESS_DAYS_COUNT, freq='B')
        self.output_data_frame = self.processing_data_frame[
            pd.to_datetime(self.processing_data_frame['timestamp']).dt.date.isin(business_days.date)
        ]

        self.output_data_frame = self.output_data_frame.drop_duplicates(subset=['hcp_uuid', 'employee_uuid', 'account_uuid', 'timestamp'])

    def _calculate_planned_visits(self) -> None:
        self.output_data_frame['period'] = PERIOD_DAILY
        self._reorder_columns()

    def _reorder_columns(self) -> None:
        columns = [
            'account_uuid', 'hcp_uuid', 'employee_uuid', 'timestamp', 'period',
        ]
        self.output_data_frame = self.output_data_frame[columns]