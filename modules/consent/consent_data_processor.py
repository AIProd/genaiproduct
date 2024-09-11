import pandas as pd

from modules.consent import constants


class ConsentDataProcessor:
    """
    Class to process consent data and calculate various consent metrics.
    """

    def __init__(self, input_data_frame: pd.DataFrame):
        """
        Initialize with input data frame.

        Parameters:
        input_data_frame (pd.DataFrame): The input consent data.
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
            'ter_code': 'territory',
            'int_title': 'title',
            'cust_ae_consent_flag': 'ae_consent',
            'cust_me_consent_flag': 'me_consent',
        }

        self.processing_data_frame = self.input_data_frame.rename(columns=column_mapping)[list(column_mapping.values())]

        self.processing_data_frame['cases_date'] = pd.to_datetime(
            self.input_data_frame['cases_date'].str.replace(' ', '')
        )

        # Sorting to ensure the latest date is taken
        self.processing_data_frame = self.processing_data_frame.sort_values(by='cases_date')

    def calculate_consent_metrics(self):
        """
        Calculate consent metrics.
        """
        # Group by the necessary columns and get the latest date for each title
        consent_groups = self.processing_data_frame.groupby(
            constants.COMMON_GROUP_COLUMNS + ['title']
        )

        consent_df = consent_groups.agg({'cases_date': 'max'}).reset_index()

        # Mapping consent types and status
        consent_df['metrics'] = consent_df['title'].map(constants.CONSENT_TYPES).fillna('None')
        consent_df['value'] = consent_df['title'].map(constants.CONSENT_STATUS).fillna('None')

        # Adding other necessary columns
        consent_df['type'] = 'consent'
        consent_df['indicator'] = constants.INDICATOR_CONSENT

        # Formatting the timestamp
        consent_df['timestamp'] = consent_df['cases_date'].dt.strftime('%Y-%m-%d')
        consent_df['period'] = constants.PERIOD_DATE

        consent_flag_df = self._add_consent_flag_data()

        self.output_data_frame = pd.concat([consent_df[[
            'timestamp', 'period', 'employee_uuid', 'hcp_uuid', 'account_uuid',
            'type', 'indicator', 'value', 'metrics'
        ]], consent_flag_df], ignore_index=True)

    def _add_consent_flag_data(self):
        """
        Add consent flag data to the output data frame.
        """
        for flag, metric in constants.CONSENT_FLAGS.items():
            consent_flag_df = (self.processing_data_frame[['employee_uuid', 'hcp_uuid', 'account_uuid', flag]]
                               .drop_duplicates())
            consent_flag_df['value'] = consent_flag_df[flag].map(constants.CONSENT_FLAG_STATUS).fillna('None')
            consent_flag_df['indicator'] = flag
            consent_flag_df['type'] = 'consent'
            consent_flag_df['metrics'] = metric
            consent_flag_df['period'] = constants.PERIOD_DATE
            consent_flag_df['timestamp'] = pd.NA

            # Ensure only the required columns are present and others are set to empty
            required_columns = [
                'timestamp', 'period', 'employee_uuid', 'hcp_uuid', 'account_uuid',
                'territory', 'type', 'indicator', 'value', 'metrics'
            ]
            for col in required_columns:
                if col not in consent_flag_df.columns:
                    consent_flag_df[col] = ''

            return consent_flag_df[required_columns]

    def get_processed_data(self) -> pd.DataFrame:
        """
        Get the processed data with calculated consent metrics.

        Returns:
        pd.DataFrame: The processed data frame.
        """
        return self.output_data_frame