from dataclasses import asdict
from typing import Any, List, Dict, Optional

import pandas as pd

from generation import constants
from generation.utils import InteractionsMetric, DateUtility, Finding, EmailCount, EmailCounts, BouncedEmail, \
    InteractionsData, PreviousVisit
from modules.global_utils import find_row_as_dict


class InteractionsDataAssembler:
    def __init__(
            self,
            interactions_df: pd.DataFrame,
            interactions_findings_df: pd.DataFrame,
            planned_visits_df: pd.DataFrame,
            hcps_df: pd.DataFrame,
            accounts_df: pd.DataFrame,
            employees_df: pd.DataFrame,
    ):
        """Initialize InteractionsDataAssembler with interactions and findings data."""
        self.interactions_df = self._prepare_dataframe(interactions_df)
        self.interactions_findings_df = self._prepare_dataframe(interactions_findings_df)
        self.planned_visits_df = planned_visits_df
        self.hcps_df = hcps_df
        self.accounts_df = accounts_df
        self.employees_df = employees_df

    @staticmethod
    def _prepare_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """Prepare the dataframe by handling timezone conversion."""
        df = df.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_localize(None)
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
    def _get_indicator_value(product_df: pd.DataFrame, indicator: str) -> float:
        """Extract and validate indicator value from product dataframe."""
        filtered_df = product_df[product_df['indicator'] == indicator]

        if len(filtered_df) == 0:
            return 0
        if len(filtered_df) > 1:
            raise ValueError(f"Found multiple rows for indicator {indicator}")

        return int(filtered_df['value'].iloc[0])

    def _get_channel_metrics(self, channel_df: pd.DataFrame, channel: str) -> InteractionsMetric:
        """Calculate metrics for a single product."""
        try:
            return InteractionsMetric(
                channel=channel,
                mat=self._get_indicator_value(
                    channel_df,
                    constants.INDICATOR_MOVING_ANNUAL_TOTAL_UNGROUPED
                ),
                mat_change=self._get_indicator_value(
                    channel_df,
                    constants.INDICATOR_MOVING_ANNUAL_TOTAL_CHANGE_PREVIOUS_YEAR_UNGROUPED
                ),
                rolq=self._get_indicator_value(
                    channel_df,
                    constants.INDICATOR_ROLLING_QUARTER_UNGROUPED
                ),
                rolq_change=self._get_indicator_value(
                    channel_df,
                    constants.INDICATOR_ROLLING_QUARTER_CHANGE_PREVIOUS_YEAR_UNGROUPED
                )
            )
        except ValueError as e:
            raise ValueError(f"Error calculating metrics for channel {channel}: {str(e)}")

    def _get_metrics(self, account_uuid: str, hcp_uuid: str, report_date: str) -> List[InteractionsMetric]:
        """Calculate interactions metrics for all products for a given account and date."""
        interactions_data = self._get_filtered_data(
            self.interactions_df,
            report_date,
            account_uuid=account_uuid,
            hcp_uuid=hcp_uuid
        )

        metrics = []
        for channel in interactions_data['channel'].unique():
            channel_df = interactions_data[interactions_data['channel'] == channel]
            metrics.append(self._get_channel_metrics(channel_df, channel))

        return metrics

    def _get_email_summaries(self, hcp_uuid: str,  report_date: str) -> List[Finding]:
        email_finding_types = [
            constants.FINDING_TYPE_CLICKED_EMAIL_AE,
            constants.FINDING_TYPE_READ_EMAIL_AE,
            constants.FINDING_TYPE_UNREAD_EMAIL_AE,
            constants.FINDING_TYPE_CLICKED_EMAIL_ME,
            constants.FINDING_TYPE_READ_EMAIL_ME,
            constants.FINDING_TYPE_UNREAD_EMAIL_ME,
        ]

        data = []
        for finding_type in email_finding_types:
            data.append(
                Finding(
                    type=finding_type,
                    text=self._get_email_summary(finding_type, hcp_uuid, report_date)
                )
            )

        return data

    def _get_email_summary(self, findings_type: str, hcp_uuid: str, report_date: str) -> str:
        """Get the summary for a specific email type (clicked, read, unread)"""
        email_findings = self._get_filtered_data(
            self.interactions_findings_df,
            report_date,
            hcp_uuid=hcp_uuid,
            type=findings_type
        )

        if not email_findings.empty:
            return email_findings['details'].values[0]
        else:
            return f"No {findings_type.replace('_summary', '')} emails in the past 6 months."

    def _get_email_counts_per_channel(self, hcp_uuid: str, channel: str, report_date: str) -> EmailCount:
        filtered_interactions = self._get_filtered_data(
            self.interactions_df,
            report_date,
            hcp_uuid=hcp_uuid,
            channel=channel
        )

        return EmailCount(
            read=len(
                filtered_interactions[filtered_interactions['indicator'] == constants.INDICATOR_READ_EMAIL]
            ),
            clicked=len(
                filtered_interactions[filtered_interactions['indicator'] == constants.INDICATOR_CLICKED_EMAIL]
            ),
            unread=len(
                filtered_interactions[filtered_interactions['indicator'] == constants.INDICATOR_UNREAD_EMAIL]
            ),
            bounced=len(
                filtered_interactions[filtered_interactions['indicator'] == constants.INDICATOR_REJECTED_EMAIL]
            ),
            total=len(filtered_interactions)
        )

    def _get_email_total_count(self, hcp_uuid: str, channels: List[str]) -> int:
        filtered_interactions = self._get_filtered_data(
            self.interactions_df,
            None,
            hcp_uuid=hcp_uuid,
            channel=channels
        )

        return len(filtered_interactions)

    def _get_email_counts(self, hcp_uuid: str, report_date: str) -> EmailCounts:
        return EmailCounts(
            approved=self._get_email_counts_per_channel(hcp_uuid, 'AE - Veeva', report_date),
            marketing=self._get_email_counts_per_channel(hcp_uuid, 'SFMC Marketing Email', report_date),
        )

    def _get_bounced_emails_data(self, account_uuid: str) -> Dict[str, List[BouncedEmail]]:
        filtered_interactions = self._get_filtered_data(
            self.interactions_df,
            None,
            account_uuid=account_uuid,
            channel=['AE - Veeva', 'SFMC Marketing Email'],
            indicator=constants.INDICATOR_REJECTED_EMAIL,
        )

        merged_df = filtered_interactions.merge(
            self.hcps_df,
            left_on='hcp_uuid',
            right_on='uuid',
        )

        unique_emails = merged_df['email'].unique()

        data = {}
        for email in unique_emails:
            email_data = []
            for _, row in merged_df[merged_df['email'] == email].iterrows():
                email_data.append(
                    BouncedEmail(
                        email=row['email'],
                        subject=row['subject'],
                        date=row['timestamp']
                    )
                )

            data[email] = email_data

        return data

    def get_interactions_data(
            self,
            account_uuid: str,
            hcp_uuid: str,
            employee_uuid: str,
            visit_date: str,
            report_date: str
    ) -> InteractionsData:
        return InteractionsData(
            account_uuid=account_uuid,
            hcp_uuid=hcp_uuid,
            employee_uuid=employee_uuid,
            metrics=self._get_metrics(account_uuid, hcp_uuid, report_date),
            email_counts=self._get_email_counts(hcp_uuid, report_date),
            email_summaries=self._get_email_summaries(hcp_uuid, report_date),
            bounced_data=self._get_bounced_emails_data(account_uuid),
            previous_visits=self._get_previous_visits(account_uuid, visit_date)
        )

    def get_interactions_data_for_employee(self, employee_uuid: str) -> List[InteractionsData]:
        employee_visits = self.planned_visits_df[self.planned_visits_df['employee_uuid'] == employee_uuid]
        first_day_last_month, last_month_name = DateUtility.get_previous_month_info()

        interactions_data = []
        for _, visit in employee_visits.iterrows():
            interactions_data.append(
                self.get_interactions_data(
                    account_uuid=visit['account_uuid'],
                    hcp_uuid=visit['hcp_uuid'],
                    employee_uuid=visit['employee_uuid'],
                    visit_date=visit['timestamp'],
                    report_date=first_day_last_month.isoformat()
                )
            )

        return interactions_data

    def get_all_data_dataframe(self):
        unique_employees = self.planned_visits_df['employee_uuid'].unique()

        data = []
        for employee_uuid in unique_employees:
            interaction_data = self.get_interactions_data_for_employee(employee_uuid)
            if interaction_data:
                df = pd.DataFrame(asdict(interaction) for interaction in interaction_data)
                data.append(df)

        return pd.concat(data)

    def _get_previous_visits(self, account_uuid: str, visit_date: str) -> List[PreviousVisit]:
        filtered_interactions = self._get_filtered_data(
            self.interactions_df,
            None,
            account_uuid=account_uuid,
            indicator=constants.INDICATOR_CALL
        )

        filtered_interactions = filtered_interactions[
            filtered_interactions['timestamp'] < pd.to_datetime(visit_date).to_datetime64()
        ]

        prev_visits = []
        for _, row in filtered_interactions.iterrows():
            employee_data = find_row_as_dict(self.employees_df, 'uuid', row['employee_uuid'])
            hcp_data = find_row_as_dict(self.hcps_df, 'uuid', row['hcp_uuid'])
            prev_visits.append(PreviousVisit(
                employee_name=employee_data['name'],
                hcp_name=hcp_data['name'],
                date=row['timestamp'].isoformat()
            ))

        return prev_visits




