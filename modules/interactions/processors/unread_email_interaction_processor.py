from datetime import datetime
from typing import Optional
from dateutil.relativedelta import relativedelta

import polars as pl

from modules import global_constants
from modules.global_utils import ProcessorHelper
from modules.interactions import constants
from modules.interactions.processors.processor import Processor


class UnreadEmailInteractionProcessor(Processor):
    def __init__(self, input_data_frame, days: int = 6 * 30):
        self.days = days
        super().__init__(input_data_frame)

    def _prepare_data_frame(self, lazy_frame: pl.LazyFrame) -> pl.LazyFrame:
        start_date = datetime.now() - relativedelta(days=self.days)
        lazy_frame = lazy_frame.select([
            pl.col(old_name).alias(new_name)
            for old_name, new_name in constants.COLUMN_MAPPING.items()
        ])

        lazy_frame = lazy_frame.with_columns(
            pl.col(constants.COLUMN_TIMESTAMP).str.to_datetime(),
        )

        lazy_frame = lazy_frame.filter(
            (pl.col(constants.COLUMN_TIMESTAMP) >= start_date)
            & (pl.col('channel').is_in(constants.EMAIL_CHANNELS))
            & (pl.col('acceptation') == 0)
        )

        return lazy_frame

    def process(self) -> Optional[pl.LazyFrame]:
        lazy_frame = self.processing_lazy_frame

        lazy_frame = lazy_frame.select([
            *[pl.col(new_name)
              for new_name in constants.COMMON_GROUP_COLUMNS],
            pl.col(constants.COLUMN_TIMESTAMP),
            pl.col(constants.COLUMN_SUBJECT),
            pl.lit(constants.INDICATOR_UNREAD_EMAIL).alias('indicator'),
            pl.col(constants.COLUMN_TIMESTAMP).sub(datetime.now()).dt.total_days().alias('value').cast(pl.Float64),
            pl.lit(constants.METRIC_DAYS).alias('metric'),
            pl.lit(global_constants.PERIOD_DAY).alias('period'),
            pl.lit(constants.METRIC_TYPE_INTERACTIONS).alias('metric_type'),
        ])

        return ProcessorHelper.select_metric_columns(
            lazy_frame,
            constants.COMMON_GROUP_COLUMNS + [constants.COLUMN_TIMESTAMP, constants.COLUMN_SUBJECT]
        )

