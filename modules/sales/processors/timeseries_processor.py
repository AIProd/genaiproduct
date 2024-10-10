from abc import ABC
from datetime import datetime

import polars as pl

from modules.global_utils import ProcessorHelper
from modules.sales import constants
from modules.sales.processors.processor import Processor
from modules.sales.utils import _resample_lazy_frame


class TimeSeriesProcessor(Processor, ABC):
    def _prepare_data_frame(self, lazy_frame: pl.LazyFrame):
        lazy_frame = lazy_frame.select([
            pl.col(old_name).alias(new_name)
            for old_name, new_name in constants.COLUMN_MAPPING.items()
        ])

        lazy_frame = lazy_frame.with_columns(
            pl.col('timestamp').str.to_datetime().dt.truncate('1mo'),
        )

        lazy_frame = lazy_frame.filter(pl.col('timestamp') < datetime.now().replace(day=1))

        lazy_frame = ProcessorHelper.explode_product_name(
            lazy_frame,
        )

        lazy_frame = _resample_lazy_frame(lazy_frame)

        # TODO: AIM-90 - check why we have null values in timestamp after resampling
        lazy_frame = lazy_frame.drop_nulls('timestamp')

        return ProcessorHelper.fix_grouping_none_values(lazy_frame, constants.COMMON_GROUP_COLUMNS)
