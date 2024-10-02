import calendar
from itertools import chain

import pandas as pd
from datetime import datetime, timedelta, date
from typing import Dict, List, Any

from generation import constants
from generation.templates import daily_report, daily_email
from generation.google_maps_url_generator import GoogleMapsURLGenerator
from generation.qlikurlgenerator import QlikSenseURLGenerator
from generation.gpt_insights import GPTInsightsGenerator



class VisitReportGenerator:
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

        # TODO: Quickfix address later
        self.filtered_hcps_uuids = hcps_df[hcps_df['franchise'] == constants.FRANCHISE_VACC]['uuid'].unique()

        self.sales_df = sales_df[sales_df['hcp_uuid'].isin(self.filtered_hcps_uuids)]
        self.sales_findings = sales_findings[sales_findings['hcp_uuid'].isin(self.filtered_hcps_uuids)]

        self.interaction_df = interaction_df[interaction_df['hcp_uuid'].isin(self.filtered_hcps_uuids)]
        self.consent_findings = consent_findings

        self.hcps = hcps_df
        self.accounts = accounts_df
        self.employees = employees_df
        self.qlik_url_generator = QlikSenseURLGenerator()
        self.gpt_generator = GPTInsightsGenerator()

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
        month_name = calendar.month_name[first_day_previous_month.month]

        return first_day_previous_month, month_name

    def _get_previous_visits(self, hcp_uuid: str, account_uuid: str) -> List[
        Dict[str, Any]
    ]:
        previous_visits = self.interaction_df[
            (self.interaction_df['hcp_uuid'] == hcp_uuid)
            & (self.interaction_df['account_uuid'] == account_uuid)
            & (self.interaction_df['indicator'] == constants.INDICATOR_CALL)
        ]

        previous_visits.loc[:, 'timestamp'] = pd.to_datetime(previous_visits['timestamp'])
        today = pd.Timestamp.today().normalize()
        previous_visits = previous_visits[previous_visits['timestamp'] < today]

        if previous_visits.empty:
            return []

        previous_visits_sorted = previous_visits.sort_values(by='timestamp', ascending=False)

        latest_visits = previous_visits_sorted.drop_duplicates(subset='employee_uuid', keep='first')
        visits = []
        for _, visit in latest_visits.iterrows():
            employee = self._find_row_as_dict(self.employees, visit['employee_uuid'])
            visits.append({
                "date": visit['timestamp'].strftime(constants.DISPLAY_DATE_TIME_FORMAT_LONG),
                "employee_name": employee['name'],
                "employee_email": employee['email'],
            })

        return visits



    def _create_grouped_sales_findings(self, hcp_uuid: str, employee_uuid: str):

        filtered_sales_findings = self.sales_findings[
            (self.sales_findings['hcp_uuid'] == hcp_uuid) &
            (self.sales_findings['employee_uuid'] == employee_uuid)
            ]
        if filtered_sales_findings.empty:
            return pd.DataFrame()

        merged_findings = filtered_sales_findings.merge(
            self.hcps[['uuid', 'name']], left_on='hcp_uuid', right_on='uuid', how='left'
        ).rename(columns={'name': 'hcp_name'}).drop(columns=['uuid'])

        merged_findings = merged_findings.merge(
            self.accounts[['uuid', 'name']], left_on='account_uuid', right_on='uuid', how='left'
        ).rename(columns={'name': 'account_name'}).drop(columns=['uuid'])

        merged_findings = merged_findings.merge(
            self.employees[['uuid', 'name']], left_on='employee_uuid', right_on='uuid', how='left'
        ).rename(columns={'name': 'employee_name'}).drop(columns=['uuid'])


        grouped_findings_combined = merged_findings.groupby(
            ['hcp_name', 'account_name', 'employee_name']
        ).agg(
            finding=('type', lambda types: '; '.join(
                [f"{t} with details: {details} and product: {product}"
                 for t, details, product in zip(types, merged_findings.loc[types.index, 'details'],
                                                merged_findings.loc[types.index, 'product_name'])]
            ))
        ).reset_index()

        grouped_findings_combined = grouped_findings_combined[
            ['hcp_name', 'account_name', 'employee_name', 'finding']
        ]

        return grouped_findings_combined

    def generate_report_data_for_employee(self, employee_uuid: str) -> list[Any]:
        employee_visits = self.planned_visits_df[self.planned_visits_df['employee_uuid'] == employee_uuid]
        data = []

        for _, visit in employee_visits.iterrows():
            hcp_uuid = visit['hcp_uuid']
            account_uuid = visit['account_uuid']

            grouped_sales_findings = self._create_grouped_sales_findings(hcp_uuid, employee_uuid)

            report_date, report_month_name = self._get_previous_month_info()

            pd_timestamp = pd.to_datetime(visit['timestamp'])
            formatted_date = pd_timestamp.strftime(constants.DISPLAY_DATE_TIME_FORMAT_LONG)

            try:
                hcp_data = self._find_row_as_dict(self.hcps, hcp_uuid)
                account_data = self._find_row_as_dict(self.accounts, account_uuid)

            except ValueError as e:
                print(e)
                continue
            previous_visits = self._get_previous_visits(hcp_uuid, account_uuid)

            account_id = str(int(account_data['id']))

            ter_target = hcp_data['ter_target']
            hcp_id = str(hcp_data['id'])
            qlik_customer360_url = self.qlik_url_generator.generate_customer_360_insights_url()
            account_360_url = self.qlik_url_generator.generate_account_page_url(account_id)
            hcp_360_url = self.qlik_url_generator.generate_hcp_page_url(hcp_id)

            template_data = {
                "hcp_name": hcp_data['name'],
                "planed_visit_date": formatted_date,
                "account_name": account_data['name'],
                "google_map_url": GoogleMapsURLGenerator.generate_url(
                    account_name=str(account_data['name']),
                    street=str(account_data['street']),
                    city=str(account_data['city']),
                    zip_code=str(account_data['zip'])
                ),
                "contact_address": f"{account_data['street']} · {account_data['zip']} {account_data['city']}",
                # TODO: AIM-31 replace with correct value when becomes available
                "contact_phone": "N/A",
                "contact_web": hcp_data['email'],
                "findings": self._get_findings(employee_uuid, hcp_uuid, report_date),
                "report_data_month": report_month_name,
                "sales": self._get_sales_metrics(employee_uuid, account_uuid, report_date),
                "interactions": self._get_interaction_metrics(employee_uuid, account_uuid, report_date),
                "trends": self._get_trends(employee_uuid, hcp_uuid, report_date),
                # TODO: AIM-31 replace with correct value when becomes available
                "insights": self.gpt_generator.generate_insights_for_findings(grouped_sales_findings),
                "other_hcps": self._get_all_hcps_in_account(account_uuid, hcp_uuid),
                "current_date": datetime.now().strftime(constants.DISPLAY_DATE_TIME_FORMAT_SHORT),
                "qlik_customer360_url": qlik_customer360_url,
                "account_360_url": account_360_url,
                "hcp_360_url": hcp_360_url,
                "previous_visits": previous_visits,
                "qlik_sense_url": account_360_url,
                'ter_target':ter_target
            }

            data.append(template_data)

        return data

    def generate_report_for_employee(self, employee_uuid: str) -> list[Any]:
        data = self.generate_report_data_for_employee(employee_uuid)
        html_reports = []
        for template_data in data:
            html_string = daily_report.render(template_data)
            html_reports.append({"hcp": template_data['hcp_name'], "html": html_string})

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

            mat = round(
                product_df[product_df['indicator'] == constants.INDICATOR_MOVING_ANNUAL_TOTAL]['value'].sum(),
                2
            ).astype(float)

            mat_change = round(
                product_df[
                    product_df['indicator'] == constants.INDICATOR_MOVING_ANNUAL_TOTAL_CHANGE_PREVIOUS_YEAR
                ]['value'].sum(),
                2
            ).astype(float)

            rolq = round(
                product_df[
                    product_df['indicator'] == constants.INDICATOR_ROLLING_QUARTER]['value'].sum(),
                2,
            ).astype(float)
            rolq_change = round(
                product_df[
                    product_df['indicator'] == constants.INDICATOR_ROLLING_QUARTER_CHANGE_PREVIOUS_YEAR
                ]['value'].sum(),
                2,
            ).astype(float)
            product_priority = product_df['product_priority'].iloc[
                0] if 'product_priority' in product_df.columns else 'Not Available'

            if pd.isna(product_priority) or product_priority in ['', 0, None]:
                product_priority = 'Not Available'

            product_name_with_priority = f"{product} ({product_priority})"

            sales.append(
                {
                    "product_name": product_name_with_priority,
                    "mat": mat,
                    "mat_change": mat_change,
                    "rolq": rolq,
                    "rolq_change": rolq_change,
                    "product_priority":product_priority
                }
            )

            sales.sort(key=lambda x: x['product_priority'])

        return sales

    def _get_trends(self, employee_uuid: str, hcp_uuid: str, report_date) -> List:
        report_date_ts = pd.Timestamp(report_date)
        self.sales_findings['timestamp'] = pd.to_datetime(self.sales_findings['timestamp']).dt.tz_localize(None)
        sales_finding_data = self.sales_findings[
            (self.sales_findings['employee_uuid'] == employee_uuid)
            & (self.sales_findings['hcp_uuid'] == hcp_uuid)
            & (self.sales_findings['timestamp'] >= report_date_ts)
            & (self.sales_findings['type'] == constants.FINDING_TYPE_TRENDS)
        ]

        trends = []
        for _, row in sales_finding_data.iterrows():
            trends.append({
                "type": row['type'],
                "text": f"{row['product_name']}: {float(row['details']):.2f}" if isinstance(row['details'], (
                int, float)) else f"{row['product_name']}: {row['details']}"
            })

        return trends

    def _get_findings(self, employee_uuid: str, hcp_uuid: str, report_date) -> List:
        report_date_ts = pd.Timestamp(report_date)
        self.sales_findings['timestamp'] = pd.to_datetime(self.sales_findings['timestamp']).dt.tz_localize(None)

        sales_finding_data = self.sales_findings[
            (self.sales_findings['employee_uuid'] == employee_uuid)
            & (self.sales_findings['hcp_uuid'] == hcp_uuid)
            & (self.sales_findings['timestamp'] >= report_date_ts)
            & (self.sales_findings['type'] != constants.FINDING_TYPE_TRENDS)
        ]

        findings = []
        for _, row in sales_finding_data.iterrows():
            findings.append(
                {
                    "type": row["type"],
                    "text": f"{float(row['details']):.2f}" if isinstance(row['details'], (int, float)) else row[
                        'details']
                }
            )

        return findings

    def _get_interaction_metrics(self, employee_uuid: str, account_uuid: str, report_date) -> List[Dict[str, Any]]:
        report_date_ts = pd.Timestamp(report_date)

        self.interaction_df['timestamp'] = pd.to_datetime(self.interaction_df['timestamp'],
                                                          errors="coerce").dt.tz_localize(None)
        interactions_data = self.interaction_df[
            (self.interaction_df['employee_uuid'] == employee_uuid)
            & (self.interaction_df['account_uuid'] == account_uuid)
            & (self.interaction_df['timestamp'] >= report_date_ts)
            ]

        unique_channels = interactions_data['channel'].unique()

        interactions = []

        for channel in unique_channels:
            channel_df = interactions_data[interactions_data['channel'] == channel]

            mat = round(
                channel_df[channel_df['indicator'] == constants.INDICATOR_MOVING_ANNUAL_TOTAL]['value'].apply(lambda x: float(x) if isinstance(x, str) else x).sum(),
                2
            )

            mat_change = round(
                channel_df[
                    channel_df['indicator'] == constants.INDICATOR_MOVING_ANNUAL_TOTAL_CHANGE_PREVIOUS_YEAR
                    ]['value'].apply(lambda x: float(x) if isinstance(x, str) else x).sum(),
                2
            )

            rolq = round(
                channel_df[
                    channel_df['indicator'] == constants.INDICATOR_ROLLING_QUARTER]['value'].
                    apply(lambda x: float(x) if isinstance(x, str) else x).sum(),
                2,
            )
            rolq_change = round(
                channel_df[
                    channel_df['indicator'] == constants.INDICATOR_ROLLING_QUARTER_CHANGE_PREVIOUS_YEAR
                    ]['value'].apply(lambda x: float(x) if isinstance(x, str) else x).sum(),
                2,
            )

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
            & (self.hcps['franchise'] == constants.FRANCHISE_VACC)
        ]

        return [
            {"name": row['name'], "specialty": row['specialty']}
            for _, row in hcps.iterrows()
        ]

    def generate_email_html_body(self, employee_uuid: str) -> str:
        employee_visits = self.planned_visits_df[self.planned_visits_df['employee_uuid'] == employee_uuid]
        employee_data = self._find_row_as_dict(self.employees, employee_uuid)

        report_date, report_month_name = self._get_previous_month_info()

        visits = []
        for _, visit in employee_visits.iterrows():
            hcp_uuid = visit['hcp_uuid']
            account_uuid = visit['account_uuid']

            try:
                hcp_data = self._find_row_as_dict(self.hcps, hcp_uuid)
                account_data = self._find_row_as_dict(self.accounts, account_uuid)
            except ValueError as e:
                print(e)
                continue
            pd_timestamp = pd.Timestamp(visit['timestamp'])

            visits.append({
                "hcp_name": hcp_data['name'],
                "meeting_date_time": pd_timestamp.strftime("%A, %d %B %I:%M %p"),
                "address": f"{account_data['street']}, {account_data['city']}, {account_data['zip']}",
                "number_of_key_points": len(self._get_findings(employee_uuid, hcp_uuid, report_date))
            })

        template_data = {
            "employee_name": employee_data['name'],
            "report_date": date.today() + timedelta(days=1),
            "planned_visits": visits
        }

        return daily_email.render(template_data)

    def generate_reports_for_all_employees(self) -> List[Any]:
        unique_employees = self.planned_visits_df['employee_uuid'].unique()
        return list(chain.from_iterable(
            self.generate_report_for_employee(employee)
            for employee in unique_employees
        ))