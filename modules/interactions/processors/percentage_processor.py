from typing import Optional

import polars as pl

from modules import global_constants
from modules.global_utils import ProcessorHelper
from modules.interactions import constants
from modules.interactions.processors.timeseries_processor import TimeSeriesProcessor


class PercentageProcessor(TimeSeriesProcessor):

    def process(self) -> Optional[pl.LazyFrame]:
        lazy_frame = self.processing_lazy_frame.sort(constants.COLUMN_TIMESTAMP)

        lazy_frame = lazy_frame.group_by_dynamic(
            constants.COLUMN_TIMESTAMP,
            every='1mo',
            group_by=constants.COMMON_GROUP_COLUMNS,
        ).agg(
            pl.lit('').alias(constants.COLUMN_SUBJECT),
            ((pl.col(constants.COLUMN_REACTION).cast(pl.Float64).sum() / pl.count()) * 100).alias(constants.PERCENTAGE_COLUMN_REACTION),
            ((pl.col(constants.COLUMN_ACCEPTATION).cast(pl.Float64).sum() / pl.count()) * 100).alias(constants.PERCENTAGE_COLUMN_ACCEPTATION),
            ((pl.col(constants.COLUMN_REJECTION).cast(pl.Float64).sum() / pl.count()) * 100).alias(constants.PERCENTAGE_COLUMN_REJECTION),
        )

        return ProcessorHelper.melt_lazy_frame(
            lazy_frame,
            [
                constants.PERCENTAGE_COLUMN_REACTION,
                constants.PERCENTAGE_COLUMN_ACCEPTATION,
                constants.PERCENTAGE_COLUMN_REJECTION,
            ],
            constants.COMMON_GROUP_COLUMNS + [constants.COLUMN_TIMESTAMP, constants.COLUMN_SUBJECT],
            {
                constants.PERCENTAGE_COLUMN_REACTION: constants.INDICATOR_REACTION_PERCENTAGE,
                constants.PERCENTAGE_COLUMN_ACCEPTATION: constants.INDICATOR_ACCEPTATION_PERCENTAGE,
                constants.PERCENTAGE_COLUMN_REJECTION: constants.INDICATOR_REJECTION_PERCENTAGE,
            },
            {
                constants.PERCENTAGE_COLUMN_REACTION: constants.METRIC_PERCENTAGE,
                constants.PERCENTAGE_COLUMN_ACCEPTATION: constants.METRIC_PERCENTAGE,
                constants.PERCENTAGE_COLUMN_REJECTION: constants.METRIC_PERCENTAGE,
            },
            {
                constants.PERCENTAGE_COLUMN_REACTION: global_constants.PERIOD_MONTH,
                constants.PERCENTAGE_COLUMN_ACCEPTATION: global_constants.PERIOD_MONTH,
                constants.PERCENTAGE_COLUMN_REJECTION: global_constants.PERIOD_MONTH,
            },
            constants.METRIC_TYPE_INTERACTIONS
        )
