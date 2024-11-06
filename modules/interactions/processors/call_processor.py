import polars as pl

from modules import global_constants
from modules.global_utils import ProcessorHelper, remove_values_from_list
from modules.interactions import constants
from modules.interactions.processors.processor import Processor


class CallProcessor(Processor):
    def _prepare_data_frame(self, lazy_frame: pl.LazyFrame) -> pl.LazyFrame:
        lazy_frame = lazy_frame.select([
            pl.col(old_name).alias(new_name)
            for old_name, new_name in constants.COLUMN_MAPPING.items()
        ])

        lazy_frame = lazy_frame.with_columns(
            pl.col(constants.COLUMN_TIMESTAMP).str.to_datetime(),
        )

        lazy_frame = lazy_frame.filter(
            (pl.col('channel') == constants.INTERACTION_CHANNEL_CALL)
            & (pl.col('type') == constants.INTERACTION_TYPE_IN_PERSON)
            & (pl.col('acceptation') == 1)
        )

        return lazy_frame

    def process(self) -> pl.LazyFrame:
        lazy_frame = self.processing_lazy_frame.sort(constants.COLUMN_TIMESTAMP)
        group_columns = remove_values_from_list(constants.COMMON_GROUP_COLUMNS, constants.UNGROUPING_COLUMNS)
        ungrouping_columns = [
            pl.lit('').alias(column) for column in
                              remove_values_from_list(constants.UNGROUPING_COLUMNS, ['employee_uuid'])
        ]

        lazy_frame = lazy_frame.group_by(group_columns).agg(
            pl.lit('').alias(constants.COLUMN_SUBJECT),
            pl.col('employee_uuid').first(),
            pl.col(constants.COLUMN_TIMESTAMP).first(),
            *ungrouping_columns,
        )

        lazy_frame = lazy_frame.select([
            *[pl.col(new_name)
              for new_name in constants.COMMON_GROUP_COLUMNS],
            pl.col(constants.COLUMN_TIMESTAMP),
            pl.col(constants.COLUMN_SUBJECT),
            pl.lit(constants.INDICATOR_CALL).alias('indicator'),
            pl.lit(1.0).alias('value'),
            pl.lit(constants.METRIC_DATE).alias('metric'),
            pl.lit(global_constants.PERIOD_DAY).alias('period'),
            pl.lit(constants.METRIC_TYPE_INTERACTIONS).alias('metric_type'),
        ])

        return ProcessorHelper.select_metric_columns(
            lazy_frame,
            constants.COMMON_GROUP_COLUMNS + [constants.COLUMN_TIMESTAMP, constants.COLUMN_SUBJECT]
        )
