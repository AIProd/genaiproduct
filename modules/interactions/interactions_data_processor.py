import ast

import numpy as np
import pandas as pd
from pandas import DataFrame

from modules.interactions import constants
from modules.interactions.utils import _create_time_series


class InteractionDataProcessor:
    """
    Class to process interaction data and calculate various interaction metrics.
    """

    def __init__(self, input_data_frame: pd.DataFrame):
        """
        Initialize with input data frame.

        Parameters:
        input_data_frame (pd.DataFrame): The input interaction data.
        """
        self.input_data_frame = input_data_frame
        self.processing_data_frame = pd.DataFrame()
        self.output_data_frame = pd.DataFrame()
        self._prepare_data_frame()

    def _prepare_data_frame(self):
        """
        Prepare data frame by extracting necessary columns.
        """
        column_mapping = {
            'account_uuid': 'account_uuid',
            'hcp_uuid': 'hcp_uuid',
            'employee_uuid': 'employee_uuid',
            'brand_name': 'product_name',
            'ter_code': 'territory',
            'sales': 'sales',
            'units': 'units',
            'int_channel': 'channel',
            'int_rejection': 'rejection',
            'int_acceptation': 'acceptation',
            'int_reaction': 'reaction',
            'total_opens': 'total_opens',
            'total_actions': 'total_actions',
            'planned_call_flag': 'planned_call',
            'order_source': 'source',
            'order_category': 'category'
        }

        # Rename columns and select only necessary ones
        self.processing_data_frame = self.input_data_frame.rename(columns=column_mapping)[list(column_mapping.values())]

        # Convert cases_date to datetime
        self.processing_data_frame['cases_date'] = pd.to_datetime(
            self.input_data_frame['cases_date'].str.replace(' ', ''), errors='coerce')

        self._process_product_name()

        dedup_columns = constants.COMMON_GROUP_COLUMNS + ['rejection', 'acceptation', 'reaction', 'total_opens',
                                                          'total_actions']
        self.processing_data_frame.drop_duplicates(subset=dedup_columns, keep='first', inplace=True)

        self.processing_data_frame['month'] = self.processing_data_frame['cases_date'].dt.month
        self.processing_data_frame['year'] = self.processing_data_frame['cases_date'].dt.year
        self.processing_data_frame[['month', 'year']] = self.processing_data_frame[['month', 'year']].replace(0, None)

    def _process_product_name(self):
        mask = self.processing_data_frame['product_name'].astype(str).str.startswith('[')
        self.processing_data_frame.loc[mask, 'product_name'] = (
            self.processing_data_frame.loc[mask, 'product_name']
            .apply(self._safe_eval)
        )

        self.processing_data_frame['product_name'] = (
            self.processing_data_frame['product_name']
            .apply(lambda x: x if isinstance(x, list) else [])
        )

        self.processing_data_frame = self.processing_data_frame.explode('product_name').fillna('')

        dedup_columns = constants.COMMON_GROUP_COLUMNS + [
            'rejection',
            'acceptation',
            'reaction',
            'total_opens',
            'total_actions'
        ]
        self.processing_data_frame = self.processing_data_frame.drop_duplicates(subset=dedup_columns, keep='first')

        self.processing_data_frame = _create_time_series(self.processing_data_frame)

        self.processing_data_frame['month'] = self.processing_data_frame['cases_date'].dt.month.replace(0, np.nan)
        self.processing_data_frame['year'] = self.processing_data_frame['cases_date'].dt.year.replace(0, np.nan)

    @staticmethod
    def _safe_eval(value):
        """
        Safely evaluate a string containing a Python literal expression.
        """
        try:
            return ast.literal_eval(value)
        except (ValueError, SyntaxError):
            return []

    @staticmethod
    def _calculate_percentages(group, numerator):
        """
        Calculate percentages for interaction metrics.
        """
        total_records = len(group)
        numerator_sum = group[numerator].sum()
        return (numerator_sum / total_records) * 100 if total_records > 0 else 0

    def _create_total_df(self, df, metric, period, group_columns):
        """
        Create DataFrame for total interaction metrics.
        """
        total_df = df.groupby(group_columns).agg({metric: 'sum'}).reset_index()
        total_df['period'] = period
        if period == constants.PERIOD_MONTH:
            total_df['timestamp'] = pd.to_datetime(total_df[['year', 'month']].assign(day=1),
                                                   errors='coerce').dt.strftime('%Y-%m-%d')
        else:
            total_df['timestamp'] = pd.to_datetime(total_df['year'].astype(str) + '-01-01',
                                                   errors='coerce').dt.strftime('%Y-%m-%d')

        total_df = total_df.dropna(subset=['timestamp'])

        total_df['indicator'] = f'{metric}_counts'
        total_df['type'] = constants.TYPE_INTERACTIONS
        total_df = total_df.rename(columns={metric: 'value'})
        total_df['metrics'] = constants.COUNT_METRIC

        return total_df

    def _create_percentage_df(self, df, metric, period, group_columns):
        """
        Create DataFrame for percentage interaction metrics.
        """
        percentage_df = df.groupby(group_columns).apply(lambda x: self._calculate_percentages(x, metric)).reset_index()
        percentage_df.columns = group_columns + [f'{metric}_percentage']
        percentage_df['period'] = period
        if period == constants.PERIOD_MONTH:
            percentage_df['timestamp'] = pd.to_datetime(percentage_df[['year', 'month']].assign(day=1),
                                                        errors='coerce').dt.strftime('%Y-%m-%d')
        else:
            percentage_df['timestamp'] = pd.to_datetime(percentage_df['year'].astype(str) + '-01-01',
                                                        errors='coerce').dt.strftime('%Y-%m-%d')

        percentage_df = percentage_df.dropna(subset=['timestamp'])

        percentage_df['indicator'] = f'{metric}_percentage'
        percentage_df['type'] = constants.TYPE_INTERACTIONS
        percentage_df = percentage_df.rename(columns={f'{metric}_percentage': 'value'})
        percentage_df['metrics'] = constants.PERCENTAGE_METRIC

        return percentage_df

    def calculate_interaction_metrics(self):
        """
        Calculate interaction metrics.
        """
        combined_df = pd.DataFrame()

        for metric in constants.METRICS:
            for period in [constants.PERIOD_MONTH, constants.PERIOD_YEAR]:
                group_columns = constants.COMMON_GROUP_COLUMNS + ['year', 'month'] if period == constants.PERIOD_MONTH else constants.COMMON_GROUP_COLUMNS + ['year']

                total_df = self._create_total_df(self.processing_data_frame, metric, period, group_columns)
                combined_df = pd.concat([combined_df, total_df], ignore_index=True)

                del total_df

                if metric in ['int_rejection', 'int_acceptation', 'int_reaction', 'planned_call']:
                    percentage_df = self._create_percentage_df(self.processing_data_frame, metric, period,
                                                               group_columns)
                    combined_df = pd.concat([combined_df, percentage_df], ignore_index=True)
                    del percentage_df

        calls_df = self._process_call_dates()

        combined_df = pd.concat([combined_df, calls_df], ignore_index=True)
        self.output_data_frame = combined_df[[
            'timestamp', 'period', 'employee_uuid', 'hcp_uuid', 'account_uuid', 'product_name',
            'territory', 'channel', 'type', 'indicator',
            'value', 'metrics'
        ]]

        del combined_df

        for employee_uuid, employee_group in self.processing_data_frame.groupby('employee_uuid'):
            self._calculate_additional_metrics(employee_group)

    def _calculate_additional_metrics(self, df):
        """
        Calculate additional metrics like MAT, ROLQ, and other growth metrics.
        """
        df = _create_time_series(df)

        df = df.sort_values(by='cases_date')

        df['moving_annual_total'] = df.groupby(constants.COMMON_GROUP_COLUMNS)[
            'total_actions'].transform(
            lambda x: x.rolling(window=12, min_periods=1).sum())
        df['rolling_quarterly'] = df.groupby(constants.COMMON_GROUP_COLUMNS)[
            'total_actions'].transform(
            lambda x: x.rolling(window=3, min_periods=1).sum())

        df['prev_year'] = df['year'] - 1

        df['mat_prev_year'] = df.groupby(constants.COMMON_GROUP_COLUMNS)[
            'moving_annual_total'].shift(12)
        df['MATGrowthPY'] = (df['moving_annual_total'] - df['mat_prev_year']) / df['mat_prev_year'] * 100

        df['rolq_prev_year'] = df.groupby(constants.COMMON_GROUP_COLUMNS)[
            'rolling_quarterly'].shift(12)
        df['ROLQGrowthPY'] = (df['rolling_quarterly'] - df['rolq_prev_year']) / df['rolq_prev_year'] * 100

        df['month_actions_prev_year'] = df.groupby(constants.COMMON_GROUP_COLUMNS)[
            'total_actions'].shift(12)
        df['MonthGrowthPY'] = (df['total_actions'] - df['month_actions_prev_year']) / df[
            'month_actions_prev_year'] * 100

        df['MATGrowthPY'] = df['MATGrowthPY'].replace([np.inf, -np.inf], np.nan).fillna(0)
        df['ROLQGrowthPY'] = df['ROLQGrowthPY'].replace([np.inf, -np.inf], np.nan).fillna(0)
        df['MonthGrowthPY'] = df['MonthGrowthPY'].replace([np.inf, -np.inf], np.nan).fillna(0)

        self._append_additional_metrics(df, 'moving_annual_total', 'MAT', constants.PERIOD_MONTH)
        self._append_additional_metrics(df, 'rolling_quarterly', 'ROLQ', constants.PERIOD_MONTH)
        self._append_additional_metrics(df, 'MATGrowthPY', 'MATGrowthPY', constants.PERIOD_MONTH)
        self._append_additional_metrics(df, 'ROLQGrowthPY', 'ROLQGrowthPY', constants.PERIOD_MONTH)
        self._append_additional_metrics(df, 'MonthGrowthPY', 'MonthGrowthPY', constants.PERIOD_MONTH)

        del df

    def _append_additional_metrics(self, df, metric, indicator, period):
        """
        Append additional metrics to the output data frame.
        """
        metrics_df = df.groupby(constants.COMMON_GROUP_COLUMNS + ['year', 'month']).agg({metric: 'last'}).reset_index()
        metrics_df['period'] = period
        if period == constants.PERIOD_MONTH:
            metrics_df['timestamp'] = pd.to_datetime(metrics_df[['year', 'month']].assign(day=1),
                                                     errors='coerce').dt.strftime('%Y-%m-%d')
        else:
            metrics_df['timestamp'] = pd.to_datetime(metrics_df['year'].astype(str) + '-01-01',
                                                     errors='coerce').dt.strftime('%Y-%m-%d')

        metrics_df = metrics_df.dropna(subset=['timestamp'])

        metrics_df['indicator'] = indicator
        metrics_df['type'] = constants.TYPE_INTERACTIONS
        metrics_df = metrics_df.rename(columns={metric: 'value'})
        metrics_df['metrics'] = constants.CURRENCY_METRIC

        self.output_data_frame = pd.concat([self.output_data_frame, metrics_df], ignore_index=True)

    def _calculate_call_dates(self) -> pd.DataFrame:
        """
        Calculate all future call dates for each unique combination of main grouper columns,
        focusing on dates later than today.

        Returns:
        pd.DataFrame: DataFrame with all future call dates and related information.
        """

        column_mapping = {
            'account_uuid': 'account_uuid',
            'hcp_uuid': 'hcp_uuid',
            'employee_uuid': 'employee_uuid',
            'ter_code': 'territory',
            'sales': 'sales',
            'units': 'units',
            'int_channel': 'channel',
            'int_rejection': 'rejection',
            'int_acceptation': 'acceptation',
            'int_reaction': 'reaction',
            'int_type': 'int_type',
            'total_opens': 'total_opens',
            'total_actions': 'total_actions',
            'planned_call_flag': 'planned_call',
            'order_source': 'source',
            'order_category': 'category',
            'cases_date': 'timestamp'
        }

        df = self.input_data_frame.copy()[column_mapping.keys()].rename(columns=column_mapping)
        df['timestamp'] = pd.to_datetime(
            df['timestamp'].str.replace(' ', ''))

        calls = df[
            (df['channel'] == 'CALLS - Veeva') &
            (df['int_type'] == 'In Person') &
            (df['acceptation'] == 1)
            ].copy()

        return calls

    def _process_call_dates(self) -> DataFrame:
        """
        Process the data to get next call dates and update the output_data_frame.
        """
        call_dates = self._calculate_call_dates()

        call_dates['type'] = constants.TYPE_INTERACTIONS
        call_dates['indicator'] = 'call_date'
        call_dates['value'] = call_dates['timestamp']
        call_dates['metrics'] = constants.DATE_METRIC
        return call_dates

    def get_processed_data(self) -> pd.DataFrame:
        """
        Get the processed data with calculated interaction metrics.

        Returns:
        pd.DataFrame: The processed data frame.
        """
        # Drop year and month from the final output
        self.output_data_frame = self.output_data_frame.drop(columns=['year', 'month'])
        return self.output_data_frame
