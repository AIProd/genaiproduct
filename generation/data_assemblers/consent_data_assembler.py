from dataclasses import asdict
from typing import List, Optional

import pandas as pd

from generation import constants
from generation.utils import ConsentMetric, ConsentData


class ConsentDataAssembler:
    def __init__(
            self,
            consent_df: pd.DataFrame,
            consent_findings_df: pd.DataFrame,
            planned_visits_df: pd.DataFrame,
            hcps_df: pd.DataFrame,
            accounts_df: pd.DataFrame,
            employees_df: pd.DataFrame,
    ):
        """Initialize ConsentDataAssembler with interactions and findings data."""
        self.consent_df = self._prepare_dataframe(consent_df)
        self.consent_findings_df = self._prepare_dataframe(consent_findings_df)
        self.planned_visits_df = planned_visits_df
        self.hcps_df = hcps_df
        self.accounts_df = accounts_df
        self.employees_df = employees_df

    @staticmethod
    def _prepare_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """Prepare the dataframe by handling timezone conversion."""
        df = df.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_localize(None)
        df = df.sort_values(by='timestamp', ascending=False)
        return df

    @staticmethod
    def _get_filtered_data(
            df: pd.DataFrame,
            report_date: Optional[str],
            **filters
    ) -> pd.DataFrame:
        """Filter dataframe by date and any additional filters."""
        mask = pd.Series(True, index=df.index)

        if report_date is not None:
            try:
                mask &= df['timestamp'] >= pd.Timestamp(report_date)
            except (ValueError, TypeError) as e:
                raise ValueError(f"Invalid report_date format: {report_date}") from e

        for column, value in filters.items():
            if column not in df.columns:
                raise ValueError(f"Column '{column}' not found in DataFrame")

            if isinstance(value, list):
                mask &= df[column].isin(value)
            else:
                mask &= df[column] == value

        return df[mask]

    @staticmethod
    def _get_metric_value(product_df: pd.DataFrame, metric: str) -> bool:
        """Extract and validate indicator value from product dataframe."""

        if len(product_df) == 0:
            return False

        return product_df['metric'].iloc[0] == metric

    def _get_indicator_metrics(self, indicator_df: pd.DataFrame, indicator: str) -> ConsentMetric:
        """Calculate metrics for a single product."""
        try:
            return ConsentMetric(
                channel=indicator,
                opt_in=self._get_metric_value(
                    indicator_df,
                    constants.METRIC_OPT_IN
                ),
                opt_out=self._get_metric_value(
                    indicator_df,
                    constants.METRIC_OPT_OUT
                ),
            )
        except ValueError as e:
            raise ValueError(f"Error calculating metrics for indicator {indicator}: {str(e)}")

    def _get_metrics(self, hcp_uuid: str) -> List[ConsentMetric]:
        """Calculate interactions metrics for all products for a given account and date."""
        consent_data = self._get_filtered_data(
            self.consent_df,
            None,
            hcp_uuid=hcp_uuid
        )

        metrics = []
        for indicator in [
            constants.INDICATOR_APPROVED_EMAIL,
            constants.INDICATOR_MARKETING_EMAIL,
            constants.INDICATOR_PHONE,
            constants.INDICATOR_POSTAL
        ]:
            indicator_df = consent_data[consent_data['indicator'] == indicator]
            metrics.append(self._get_indicator_metrics(indicator_df, indicator))

        return metrics

    def get_consent_data(
            self,
            account_uuid: str,
            hcp_uuid: str,
            employee_uuid: str,
    ) -> ConsentData:
        return ConsentData(
            account_uuid=account_uuid,
            hcp_uuid=hcp_uuid,
            employee_uuid=employee_uuid,
            metrics=self._get_metrics(hcp_uuid),
        )

    def get_consent_data_for_employee(self, employee_uuid: str) -> List[ConsentData]:
        employee_visits = self.planned_visits_df[self.planned_visits_df['employee_uuid'] == employee_uuid]

        consent_data = []
        for _, visit in employee_visits.iterrows():
            consent_data.append(
                self.get_consent_data(
                    account_uuid=visit['account_uuid'],
                    hcp_uuid=visit['hcp_uuid'],
                    employee_uuid=visit['employee_uuid'],
                )
            )

        return consent_data

    def get_all_data_dataframe(self):
        unique_employees = self.planned_visits_df['employee_uuid'].unique()

        data = []
        for employee_uuid in unique_employees:
            consent_data = self.get_consent_data_for_employee(employee_uuid)
            if consent_data:
                df = pd.DataFrame(asdict(consent) for consent in consent_data)
                data.append(df)

        return pd.concat(data)
