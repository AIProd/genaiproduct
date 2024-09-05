import calendar
from itertools import chain

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any

from generation.daily_report import template





class VisitReportGenerator:
    IMPORTANT_SALES_METRICS = [
        'MATGrowthPY', 'ROLQGrowthPY', 'moving_annual_total',
        'rolling_quarterly', 'sales', 'units'
    ]
    INTERACTION_CHANNEL = 'CALLS - Veeva'
    IMPORTANT_INTERACTION_METRICS = ['total_actions_counts', 'MonthGrowthPY']

    def __init__(
            self,
            planned_visits_df: pd.DataFrame,
            sales_df: pd.DataFrame,
            sales_findings: pd.DataFrame,
            interaction_df: pd.DataFrame,
            consent_findings: pd.DataFrame,
            hcps_df: pd.DataFrame,
            accounts_df: pd.DataFrame,
            employees_df: pd.DataFrame,
    ):
        """
        :param planned_visits_df:
        :param sales_df: Already prefiltered for planned visits
        :param sales_findings: Already prefiltered for planned visits
        :param interaction_df: Already prefiltered for planned visits
        :param consent_findings: Already prefiltered for planned visits
        """
        self.planned_visits_df = planned_visits_df

        self.sales_df = sales_df
        self.sales_findings = sales_findings

        self.sales_df = sales_df

        self.interaction_df = interaction_df
        self.consent_findings = consent_findings

        self.hcps = hcps_df
        self.accounts = accounts_df
        self.employees = employees_df

    @staticmethod
    def _find_row_as_dict(df, uuid_value):
        matching_row = df[df['uuid'] == uuid_value]

        if matching_row.empty:
            raise ValueError(f"No row found with uuid: {uuid_value}")

        row_dict = matching_row.iloc[0].to_dict()

        return row_dict

    @staticmethod
    def _get_previous_month_info():
        current_date = datetime.now()
        first_day_current_month = current_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_day_previous_month = first_day_current_month - timedelta(days=1)
        first_day_previous_month = last_day_previous_month.replace(day=1)
        first_day_two_months_ago = first_day_previous_month - timedelta(days=1)
        first_day_two_months_ago = first_day_two_months_ago.replace(day=1)
        month_name = calendar.month_name[first_day_previous_month.month]

        return first_day_two_months_ago, month_name

    def generate_report_for_employee(self, employee_uuid: str) -> list[Any]:
        employee_visits = self.planned_visits_df[self.planned_visits_df['employee_uuid'] == employee_uuid]
        html_reports = []

        for _, visit in employee_visits.iterrows():
            hcp_uuid = visit['hcp_uuid']
            account_uuid = visit['account_uuid']

            report_date, report_month_name = self._get_previous_month_info()

            pd_timestamp = pd.to_datetime(visit['timestamp'])
            formatted_date = pd_timestamp.strftime("%A, %d %B")

            try:
                hcp_data = self._find_row_as_dict(self.hcps, hcp_uuid)
                account_data = self._find_row_as_dict(self.accounts, account_uuid)
            except ValueError as e:
                print(e)
                continue

            template_data = {
                "hcp_name": hcp_data['name'],
                "planed_visit_date": formatted_date,
                "account_name": account_data['name'],
                # TODO: AIM-31 replace with correct value when becomes available
                "google_map_url": "https://maps.app.goo.gl/g73xJUfpJwh2UtVQ6",
                # TODO: AIM-31 replace with correct value when becomes available
                "contact_address": "Schönenbergstrasse 6 · 8820 Wädenswil",
                # TODO: AIM-31 replace with correct value when becomes available
                "contact_phone": "+41 44 780 00 03",
                # TODO: AIM-31 replace with correct value when becomes available
                "contact_web": "kinderpraxis-waedi.ch",
                "findings": self._get_findings(employee_uuid, hcp_uuid, report_date),
                # TODO: AIM-31 replace with correct value when becomes available
                "qlik_sense_url": "https://ghh.qlikeurss.merck.com/sense/app/9183f2cc-33c6-4b01-85da-aea707c65733/sheet/72512643-9503-4b68-b202-796417d1c5b2/analysis/options/clearselections/select/hcp_id/CH-3130036/select/HCP%20Territory%20Business%20Unit/",
                "report_data_month": report_month_name,
                "sales": self._get_sales_metrics(employee_uuid, account_uuid, report_date),
                "interactions": self._get_interaction_metrics(employee_uuid, account_uuid, report_date),
                "trends": self._get_trends(employee_uuid, hcp_uuid, report_date),
                # TODO: AIM-31 replace with correct value when becomes available
                "insights": [],
                "other_hcps": self._get_all_hcps_in_account(account_uuid, hcp_uuid),
                "current_date": datetime.now().strftime("%d.%m.%Y"),
            }

            html_string = template.render(template_data)

            html_reports.append({"hcp": hcp_data['name'], "html": html_string})

        return html_reports

    def _get_sales_metrics(self, employee_uuid: str, account_uuid: str, report_date) -> List[Dict[str, Any]]:
        report_date_ts = pd.Timestamp(report_date)
        self.sales_df['timestamp'] = pd.to_datetime(self.sales_df['timestamp']).dt.tz_localize(None)
        sales_data = self.sales_df[
            (self.sales_df['employee_uuid'] == employee_uuid)
            & (self.sales_df['account_uuid'] == account_uuid)
            & (self.sales_df['timestamp'] >= report_date_ts)
            ]

        unique_products = sales_data['product_name'].unique()

        sales = []
        for product in unique_products:
            product_df = sales_data[sales_data['product_name'] == product]

            mat = product_df[product_df['indicator'] == 'MAT']['value'].sum()
            mat_change = product_df[product_df['indicator'] == 'mat_growth_change_previous_year']['value'].sum()
            rolq = product_df[product_df['indicator'] == 'ROLQ']['value'].sum()
            rolq_change = product_df[product_df['indicator'] == 'rolling_quarter_change_previous_year']['value'].sum()

            sales.append(
                {
                    "product_name": product,
                    "mat": mat,
                    "mat_change": mat_change,
                    "rolq": rolq,
                    "rolq_change": rolq_change,
                }
            )

        return sales

    def _get_trends(self, employee_uuid: str, hcp_uuid: str, report_date) -> List:
        report_date_ts = pd.Timestamp(report_date)
        self.sales_findings['timestamp'] = pd.to_datetime(self.sales_findings['timestamp']).dt.tz_localize(None)
        sales_finding_data = self.sales_findings[
            (self.sales_findings['employee_uuid'] == employee_uuid)
            & (self.sales_findings['hcp_uuid'] == hcp_uuid)
            & (self.sales_findings['timestamp'] >= report_date_ts)
            & (self.sales_findings['type'] == 'trends')
            ]

        trends = []
        for _, row in sales_finding_data.iterrows():
            trends.append(
                {
                    "type": row['type'],
                    "text": row['details']
                }
            )

        return trends

    def _get_findings(self, employee_uuid: str, hcp_uuid: str, report_date) -> List:
        report_date_ts = pd.Timestamp(report_date)
        self.sales_findings['timestamp'] = pd.to_datetime(self.sales_findings['timestamp']).dt.tz_localize(None)

        sales_finding_data = self.sales_findings[
            (self.sales_findings['employee_uuid'] == employee_uuid)
            & (self.sales_findings['hcp_uuid'] == hcp_uuid)
            & (self.sales_findings['timestamp'] >= report_date_ts)
            & (self.sales_findings['type'] != 'trends')
            ]

        findings = []
        for _, row in sales_finding_data.iterrows():
            findings.append(
                {
                    "type": row["type"],
                    "text": row['details']
                }
            )

        return findings

    def _get_interaction_metrics(self, employee_uuid: str, account_uuid: str, report_date) -> List[Dict[str, Any]]:
        report_date_ts = pd.Timestamp(report_date)
        self.interaction_df['timestamp'] = pd.to_datetime(self.interaction_df['timestamp']).dt.tz_localize(None)
        interactions_data = self.interaction_df[
            (self.interaction_df['employee_uuid'] == employee_uuid)
            & (self.interaction_df['account_uuid'] == account_uuid)
            & (self.interaction_df['timestamp'] >= report_date_ts)
            ]

        unique_channels = interactions_data['channel'].unique()

        interactions = []

        for channel in unique_channels:
            channel_df = interactions_data[interactions_data['channel'] == channel]

            mat = channel_df[channel_df['indicator'] == 'MAT']['value'].sum()
            mat_change = channel_df[channel_df['indicator'] == 'MATGrowthPY']['value'].sum()
            rolq = channel_df[channel_df['indicator'] == 'ROLQ']['value'].sum()
            rolq_change = channel_df[channel_df['indicator'] == 'ROLQGrowthPY']['value'].sum()

            interactions.append(
                {
                    "channel": channel,
                    "mat": mat,
                    "mat_change": mat_change,
                    "rolq": rolq,
                    "rolq_change": rolq_change,
                }
            )

        return interactions

    def _get_all_hcps_in_account(self, account_uuid: str, hcp_uuid: str) -> List[Dict[str, str]]:
        hcps = self.hcps[
            (self.hcps['account_uuid'] == account_uuid)
            & (self.hcps['uuid'] != hcp_uuid)
            & (self.hcps['franchise'] == 'CH_VACC_A_001')
            ]

        return [
            {"name": row['name'], "specialty": row['specialty']}
            for _, row in hcps.iterrows()
        ]

    def generate_reports_for_all_employees(self) -> List[Any]:
        unique_employees = self.planned_visits_df['employee_uuid'].unique()
        return list(chain.from_iterable(
            self.generate_report_for_employee(employee)
            for employee in unique_employees
        ))