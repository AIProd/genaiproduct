from dataclasses import asdict
from datetime import datetime
from typing import TypeVar, Type, Dict, List, Any

import pandas as pd

from entities.entity_classes.account import Account
from entities.entity_classes.employee import Employee
from entities.entity_classes.hcp import HCP
from generation import constants
from generation.templates.daily_report import daily_report
from generation.templates.mail import daily_email
from generation.utils import DateUtility, TemplateData, SalesData, InteractionsData, ConsentData, VisitData, EmailData
from modules.global_utils import find_row_as_dict, convert_to_dataclass

T = TypeVar('T')


class ReportAssembler:
    def __init__(
            self,
            planned_visits_df: pd.DataFrame,
            hcps_df: pd.DataFrame,
            accounts_df: pd.DataFrame,
            employees_df: pd.DataFrame,
            sales_data: pd.DataFrame,
            interactions_data: pd.DataFrame,
            consent_data: pd.DataFrame
    ):
        self.planned_visits_df = planned_visits_df
        self.hcps_df = hcps_df
        self.accounts_df = accounts_df
        self.employees_df = employees_df
        self.sales_data = sales_data
        self.interactions_data = interactions_data
        self.consent_data = consent_data

    def generate_report_data_for_visit(self, visit: pd.DataFrame) -> TemplateData:
        employee_data = find_row_as_dict(self.employees_df, 'uuid', visit['employee_uuid'])
        hcp_data = find_row_as_dict(self.hcps_df, 'uuid', visit['hcp_uuid'])
        account_data = find_row_as_dict(self.accounts_df, 'uuid', visit['account_uuid'])

        pd_timestamp = pd.to_datetime(visit['timestamp'])
        formatted_date = pd_timestamp.strftime(constants.DISPLAY_DATE_TIME_FORMAT_LONG)

        report_month, _ = DateUtility.get_previous_month_info()

        return TemplateData(
            hcp=HCP(**hcp_data),
            account=Account(**account_data),
            employee=Employee(**employee_data),
            other_hcps=self._get_other_hcps_in_accounts(account_data, hcp_data),
            visit_date=formatted_date,
            report_month=DateUtility.format_date(report_month, '%B'),
            sales=self._transform_sales_data(
                account_data['uuid'],
                hcp_data['uuid'],
                employee_data['uuid']
            ),
            interactions=self._transform_interactions_data(
                account_data['uuid'],
                hcp_data['uuid'],
                employee_data['uuid']
            ),
            consents=self._transform_consent_data(
                account_data['uuid'],
                hcp_data['uuid'],
                employee_data['uuid']
            ),
        )

    @staticmethod
    def generate_report(report_data: Dict):
        return daily_report.render(report_data).replace('\n', '')

    def generate_report_for_employee(self, employee_uuid: str) -> list[dict[str, Any]]:
        employee_visits = self.planned_visits_df[self.planned_visits_df['employee_uuid'] == employee_uuid]

        reports = []
        for _, visit in employee_visits.iterrows():
            hcp_data = find_row_as_dict(self.hcps_df, 'uuid', visit['hcp_uuid'])
            account_data = find_row_as_dict(self.accounts_df, 'uuid', visit['account_uuid'])
            reports.append({
                'hcp_name': hcp_data['name'],
                'account_name': account_data['name'],
                'visit_date': visit['timestamp'],
                'report': self.generate_report(self.generate_report_data_for_visit(visit).to_dict())
            })

        return reports

    def generate_report_for_all_employees(self):
        unique_employees = self.planned_visits_df['employee_uuid'].unique()

        data = []
        for employee_uuid in unique_employees:
            data.append({
                'employee_uuid': employee_uuid,
                'reports': self.generate_report_for_employee(employee_uuid)
            })

        return data

    def generate_report_data_for_employee(self, employee_uuid: str) -> List[Dict[str, Any]]:
        employee_visits = self.planned_visits_df[self.planned_visits_df['employee_uuid'] == employee_uuid]

        reports = []
        for _, visit in employee_visits.iterrows():
            reports.append(
                asdict(self.generate_report_data_for_visit(visit))
            )

        return reports

    def generate_report_data_all_employees(self) -> List[Dict[str, List[TemplateData]]]:
        unique_employees = self.planned_visits_df['employee_uuid'].unique()

        data = []
        for employee_uuid in unique_employees:
            data.append({
                'employee_uuid': employee_uuid,
                'data': self.generate_report_data_for_employee(employee_uuid)
            })

        return data

    def get_email_data_for_employee(self, employee_uuid: str) -> EmailData:
        employee_visits = self.planned_visits_df[self.planned_visits_df['employee_uuid'] == employee_uuid]

        employee_data = find_row_as_dict(self.employees_df, 'uuid', employee_uuid)

        visit_data = []
        for _, visit in employee_visits.iterrows():
            hcp_data = find_row_as_dict(self.hcps_df, 'uuid', visit['hcp_uuid'])
            account_Data = find_row_as_dict(self.accounts_df, 'uuid', visit['account_uuid'])

            gathered_visit_data = self.generate_report_data_for_visit(visit)
            key_points = len(gathered_visit_data.sales.findings)

            visit_data.append(
                VisitData(
                    hcp=HCP(**hcp_data),
                    account=Account(**account_Data),
                    date=DateUtility.format_date(
                        datetime.fromisoformat(visit['timestamp']
                    ), constants.DISPLAY_DATE_TIME_FORMAT_LONG),
                    key_points=key_points
                )
            )

        return EmailData(
            employee=Employee(**employee_data),
            visits=visit_data
        )

    def generate_email_for_employee(self, employee_uuid: str):
        return daily_email.render(self.get_email_data_for_employee(employee_uuid).to_dict()).replace('\n', '')

    @staticmethod
    def _transform_dataframe_to_single_row(
            df: pd.DataFrame,
            account_uuid: str,
            hcp_uuid: str,
            employee_uuid: str,
            target_class: Type[T]
    ) -> T:
        """
        Common method to transform a filtered dataframe into a single row dataclass instance.

        Args:
            df: Input DataFrame to filter and transform
            account_uuid: Account identifier
            hcp_uuid: HCP identifier
            employee_uuid: Employee identifier
            target_class: Target dataclass type

        Returns:
            Instance of target_class containing the transformed data

        Raises:
            ValueError: If no matching row or multiple matching rows are found
        """
        filtered_df = df[
            (df['account_uuid'] == account_uuid) &
            (df['hcp_uuid'] == hcp_uuid) &
            (df['employee_uuid'] == employee_uuid)
            ]

        if len(filtered_df) == 0:
            raise ValueError("No matching row found")
        if len(filtered_df) > 1:
            raise ValueError("Multiple matching rows found")

        row_dict = filtered_df.iloc[0].to_dict()
        return convert_to_dataclass(target_class, row_dict)

    def _transform_sales_data(self, account_uuid: str, hcp_uuid: str, employee_uuid: str) -> SalesData:
        return self._transform_dataframe_to_single_row(
            self.sales_data,
            account_uuid,
            hcp_uuid,
            employee_uuid,
            SalesData
        )

    def _transform_interactions_data(self, account_uuid: str, hcp_uuid: str, employee_uuid: str) -> InteractionsData:
        return self._transform_dataframe_to_single_row(
            self.interactions_data,
            account_uuid,
            hcp_uuid,
            employee_uuid,
            InteractionsData
        )

    def _transform_consent_data(self, account_uuid: str, hcp_uuid: str, employee_uuid: str) -> ConsentData:
        return self._transform_dataframe_to_single_row(
            self.consent_data,
            account_uuid,
            hcp_uuid,
            employee_uuid,
            ConsentData
        )

    def _get_other_hcps_in_accounts(self, account_data: dict, hcp_data: dict):
        other_hcps = self.hcps_df[
            (self.hcps_df['account_uuid'] == account_data['uuid']) &
            (self.hcps_df['name'] != hcp_data['name']) &
            (self.hcps_df['name'] != account_data['name'])
            ]

        unique_names = other_hcps['name'].unique()

        data = []

        for name in unique_names:
            filtered_hcp_df = other_hcps[other_hcps['name'] == name]
            row = filtered_hcp_df.iloc[0].to_dict()
            data.append(
                HCP(**row)
            )

        return data
