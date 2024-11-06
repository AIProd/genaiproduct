import polars as pl

PERIOD_DAY = 'day'
PERIOD_MONTH = 'month'
PERIOD_YEAR = 'year'

METRIC_VALUE_COLUMNS = ["indicator", "value", "metric", "period", "metric_type"]

ENFORCED_METRICS_SCHEMA = {
    'employee_uuid': pl.Utf8,
    'account_uuid': pl.Utf8,
    'hcp_uuid': pl.Utf8,
    'product_name': pl.Utf8,
    'territory': pl.Utf8,
    'channel': pl.Utf8,
    'type': pl.Utf8,
    'category': pl.Utf8,
    'source': pl.Utf8,
    'timestamp': pl.Datetime,
    'subject': pl.Utf8,
    'indicator': pl.Utf8,
    'value': pl.Float64,
    'metric': pl.Utf8,
    'period': pl.Utf8,
    'metric_type': pl.Utf8,
}