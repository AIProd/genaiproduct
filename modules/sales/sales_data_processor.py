import numpy as np
import pandas as pd

from modules.sales import constants
from modules.sales.utils import _create_time_series


class SalesDataProcessor:

    def __init__(self, input_data_frame: pd.DataFrame):

        self.input_data_frame = input_data_frame
        self.processing_data_frame = pd.DataFrame()
        self.output_data_frame = pd.DataFrame()
        self._prepare_data_frame()

    def _prepare_data_frame(self):
        column_mapping = {
            'account_uuid': 'account_uuid',
            'hcp_uuid': 'hcp_uuid',
            'employee_uuid': 'employee_uuid',
            'brand_name': 'product_name',
            'ter_code': 'territory',
            'sales': 'sales',
            'units': 'units',
            'sales_channel': 'channel',
            'order_source': 'source',
            'order_category': 'category'
        }

        self.processing_data_frame = self.input_data_frame.rename(columns=column_mapping)[list(column_mapping.values())]

        self.processing_data_frame['cases_date'] = pd.to_datetime(
            self.input_data_frame['cases_date'].str.replace(' ', ''))

        self.processing_data_frame = self.processing_data_frame.sort_values(by='cases_date')

        dedup_columns = constants.COMMON_GROUP_COLUMNS + ['sales', 'units']
        self.processing_data_frame = self.processing_data_frame.drop_duplicates(subset=dedup_columns, keep='first')

        self.processing_data_frame = _create_time_series(self.processing_data_frame)

        self.processing_data_frame['month'] = self.processing_data_frame['cases_date'].dt.month
        self.processing_data_frame['year'] = self.processing_data_frame['cases_date'].dt.year



    def _calculate_rolling_metrics(self):
        """
        Calculate rolling metrics using a date-based window and preserving all columns.
        """
        df = self.processing_data_frame.copy()

        df['moving_annual_total'] = df.groupby(constants.COMMON_GROUP_COLUMNS[:-2])['sales'].transform(
            lambda x: x.rolling(window=12, min_periods=1).sum())
        df['rolling_quarter'] = df.groupby(constants.COMMON_GROUP_COLUMNS[:-2])['sales'].transform(
            lambda x: x.rolling(window=3, min_periods=1).sum())
        return df

    def _calculate_growth_metrics(self):

        self.processing_data_frame['prev_year'] = self.processing_data_frame['year'] - 1

        self.processing_data_frame['mat_prev_year'] = self.processing_data_frame.groupby(
            constants.COMMON_GROUP_COLUMNS
        )['moving_annual_total'].shift(12)

        self.processing_data_frame['mat_growth_change_previous_year'] = (
            (self.processing_data_frame['moving_annual_total'] - self.processing_data_frame['mat_prev_year']) /
            abs(self.processing_data_frame['mat_prev_year']) * 100
        ).replace([np.inf, -np.inf], np.nan).fillna(0)

        self.processing_data_frame['rolq_prev_year'] = self.processing_data_frame.groupby(
            constants.COMMON_GROUP_COLUMNS
        )['rolling_quarter'].shift(12)

        self.processing_data_frame['rolling_quarter_change_previous_year'] = (
            (self.processing_data_frame['rolling_quarter'] - self.processing_data_frame['rolq_prev_year']) /
            abs(self.processing_data_frame['rolq_prev_year']) * 100
        ).replace([np.inf, -np.inf], np.nan).fillna(0)

        self.processing_data_frame['month_sales_prev_year'] = self.processing_data_frame.groupby(
            constants.COMMON_GROUP_COLUMNS
        )['sales'].shift(12)

        self.processing_data_frame['sales_change_previous_year'] = (
            (self.processing_data_frame['sales'] - self.processing_data_frame['month_sales_prev_year']) /
            abs(self.processing_data_frame['month_sales_prev_year']) * 100
        ).replace([np.inf, -np.inf], np.nan).fillna(0)

        return self.processing_data_frame



    def _create_metrics_df(self, metric, indicator, period, metrics=constants.METRIC_TYPE_STATISTICS):

        metrics_df = self.processing_data_frame.groupby(constants.COMMON_GROUP_COLUMNS + ['year', 'month']).agg(
            {metric: 'last'}).reset_index()
        metrics_df['period'] = period
        metrics_df['timestamp'] = metrics_df.apply(
            lambda row: pd.to_datetime(f"{row['year']}-{row['month']:02d}-01").strftime('%Y-%m-%d')
            if period == constants.PERIOD_MONTH
            else pd.to_datetime(f"{row['year']}-01-01").strftime('%Y-%m-%d'),
            axis=1
        )
        metrics_df['indicator'] = indicator
        metrics_df['type'] = constants.METRIC_TYPE_STATISTICS
        metrics_df = metrics_df.rename(columns={metric: 'value'})
        metrics_df['metrics'] = metrics
        return metrics_df

    def _create_dataframe_copy(
            self,
            period: str,
            metrics: str,
            indicator: str,
            type: str,
            from_df: pd.DataFrame = None
    ) -> pd.DataFrame:
        if from_df is None:
            df = self.processing_data_frame.copy()
        elif isinstance(from_df, pd.DataFrame):
            df = from_df.copy()
        else:
            raise TypeError("from_df must be either None or a pandas DataFrame")

        df['period'] = period
        df['metrics'] = metrics
        df['indicator'] = indicator
        df['type'] = type
        df.rename(columns={indicator: 'value'}, inplace=True)

        df = self.process_timestamp(period, df)

        return df

    @staticmethod
    def process_timestamp(period, df: pd.DataFrame) -> pd.DataFrame:
        if 'cases_date' in df.columns:
            df['cases_date'] = pd.to_datetime(df['cases_date'])
            if period == constants.PERIOD_MONTH:
                df['timestamp'] = df['cases_date'].dt.to_period('M').dt.to_timestamp()
            elif period == constants.PERIOD_YEAR:
                df['timestamp'] = df['cases_date'].dt.to_period('Y').dt.to_timestamp()
        elif 'year' in df.columns:
            df['cases_date'] = pd.to_datetime(df['year'].astype(str) + '-01-01')
            df['timestamp'] = df['cases_date']
        else:
            raise ValueError("DataFrame must contain either 'cases_date' or 'year' column")

        df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%d')

        return df

    def calculate_sales_metrics(self):

        self.processing_data_frame = self._calculate_rolling_metrics()
        self.processing_data_frame = self._calculate_growth_metrics()

        monthly_df = self._create_dataframe_copy(
            constants.PERIOD_MONTH,
            constants.METRIC_CURRENCY,
            constants.INDICATOR_SALES,
            constants.METRIC_TYPE_STATISTICS,
        )

        mat_df = self._create_metrics_df(
            constants.METRIC_MOVING_ANNUAL_TOTAL,
            constants.INDICATOR_MOVING_ANNUAL_TOTAL,
            constants.PERIOD_MONTH,
            constants.METRIC_CURRENCY
        )

        rolq_df = self._create_metrics_df(
            constants.METRIC_ROLLING_QUARTER,
            constants.INDICATOR_ROLLING_QUARTER,
            constants.PERIOD_MONTH,
            constants.METRIC_CURRENCY
        )

        annual_df = self.processing_data_frame.groupby(
            constants.COMMON_GROUP_COLUMNS + ['year']
        ).agg({'sales': 'sum'}).reset_index()

        annual_df = self._create_dataframe_copy(
            constants.PERIOD_YEAR,
            constants.METRIC_CURRENCY,
            constants.INDICATOR_SALES,
            constants.METRIC_TYPE_STATISTICS,
            annual_df
        )

        mat_growth_df = self._create_metrics_df(
            constants.METRIC_MOVING_ANNUAL_TOTAL_CHANGE_PREVIOUS_YEAR,
            constants.INDICATOR_MOVING_ANNUAL_TOTAL_CHANGE_PREVIOUS_YEAR,
            constants.PERIOD_MONTH,
            metrics=constants.METRIC_CURRENCY
        )

        rolq_growth_df = self._create_metrics_df(
            constants.METRIC_ROLLING_QUARTER_CHANGE_PREVIOUS_YEAR,
            constants.INDICATOR_ROLLING_QUARTER_CHANGE_PREVIOUS_YEAR,
            constants.PERIOD_MONTH,
            metrics=constants.METRIC_CURRENCY
        )

        month_growth_df = self._create_metrics_df(
            constants.METRIC_SALES_CHANGE_PREVIOUS_YEAR,
            constants.INDICATOR_SALES_CHANGE_PREVIOUS_YEAR,
            constants.PERIOD_MONTH,
            metrics=constants.METRIC_CURRENCY
        )

        annual_units_df = self.processing_data_frame.groupby(
            constants.COMMON_GROUP_COLUMNS + ['year']
        ).agg({'units': 'sum'}).reset_index()

        annual_units_df = self._create_dataframe_copy(
            constants.PERIOD_YEAR,
            constants.METRIC_UNIT,
            constants.INDICATOR_UNITS,
            constants.METRIC_TYPE_STATISTICS,
            annual_units_df
        )

        monthly_units_df = self._create_metrics_df(
            constants.METRIC_UNIT,
            constants.INDICATOR_UNITS,
            constants.PERIOD_MONTH,
            constants.METRIC_UNIT
        )

        combined_df = pd.concat([
            annual_df, monthly_df, mat_df, rolq_df, mat_growth_df, rolq_growth_df,
            month_growth_df, annual_units_df, monthly_units_df
        ], ignore_index=True)

        self.output_data_frame = combined_df[[
            'timestamp', 'period', 'employee_uuid', 'hcp_uuid', 'account_uuid', 'product_name',
            'territory', 'channel', 'type', 'indicator',
            'value', 'metrics', 'source', 'category'
        ]]

    def get_processed_data(self) -> pd.DataFrame:

        return self.output_data_frame
