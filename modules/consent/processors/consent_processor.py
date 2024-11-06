import polars as pl

from modules import global_constants
from modules.consent.processors.processor import Processor
from modules.consent import constants
from modules.global_utils import ProcessorHelper


class ConsentProcessor(Processor):
    def _prepare_data_frame(self, lazy_frame: pl.LazyFrame) -> pl.LazyFrame:
        lazy_frame = lazy_frame.select([
            pl.col(old_name).alias(new_name)
            for old_name, new_name in constants.COLUMN_MAPPING.items()
        ])

        lazy_frame = lazy_frame.with_columns(
            pl.col(constants.COLUMN_TIMESTAMP).str.to_datetime(),
        )

        return lazy_frame

    def process(self) -> pl.LazyFrame:
        lazy_frame = self.processing_lazy_frame.sort(constants.COLUMN_TIMESTAMP)

        lazy_frame = lazy_frame.with_columns(
            pl.col('title').replace(constants.CONSENT_TYPES).alias('indicator'),
            pl.col('title').replace(constants.CONSENT_STATUS).alias('metric'),
            pl.lit(global_constants.PERIOD_DAY).alias('period'),
            pl.lit(constants.METRIC_TYPE_CONSENT).alias('metric_type'),
        )

        lazy_frame = lazy_frame.with_columns(
            pl.when(
                pl.col('indicator') == constants.INDICATOR_MARKETING_EMAIL,
            ).then(pl.col('me_consent'))
            .when(
                pl.col('indicator') == constants.INDICATOR_APPROVED_EMAIL,
            ).then(pl.col('ae_consent'))
            .otherwise(
                pl.when(pl.col('metric') == constants.METRIC_OPT_IN).then(pl.lit(1))
                .otherwise(pl.lit(0)
                           )
            ).alias('value').cast(pl.Float64)
        )

        return ProcessorHelper.select_metric_columns(lazy_frame, constants.COMMON_GROUP_COLUMNS + [constants.COLUMN_TIMESTAMP])