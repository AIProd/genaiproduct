from dataclasses import asdict
from itertools import chain
from typing import Any, List, Optional

import pandas as pd

from generation import constants
from generation.gpt_insights import GPTInsightsGenerator
from generation.utils import SalesMetric, Finding, Insight, DateUtility, SalesData


class SalesDataAssembler:
    def __init__(
            self,
            sales_df: pd.DataFrame,
            sales_findings_df: pd.DataFrame,
            planned_visits_df: pd.DataFrame,
            hcps_df: pd.DataFrame,
            accounts_df: pd.DataFrame,
            employees_df: pd.DataFrame,
    ):
        """Initialize SalesAssembler with sales and findings data."""
        self.sales_df = self._prepare_dataframe(sales_df)
        self.sales_findings_df = self._prepare_dataframe(sales_findings_df)
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
            return 0.0
        if len(filtered_df) > 1:
            raise ValueError(f"Found multiple rows for indicator {indicator}")

        return round(filtered_df['value'].iloc[0], 2)

    @staticmethod
    def _format_finding_text(details: Any, product_name: str = None) -> str:
        """Format finding text with optional product name."""
        if isinstance(details, (int, float)):
            text = f"{float(details):.2f}"
        else:
            text = str(details)

        return f"{product_name}: {text}" if product_name else text

    def _get_product_metrics(self, product_df: pd.DataFrame, product: str) -> SalesMetric:
        """Calculate metrics for a single product."""
        try:
            return SalesMetric(
                product_name=product,
                mat=self._get_indicator_value(
                    product_df,
                    constants.INDICATOR_MOVING_ANNUAL_TOTAL_SALES_UNGROUPED
                ),
                mat_change=self._get_indicator_value(
                    product_df,
                    constants.INDICATOR_MOVING_ANNUAL_TOTAL_CHANGE_PREVIOUS_YEAR_SALES_UNGROUPED
                ),
                rolq=self._get_indicator_value(
                    product_df,
                    constants.INDICATOR_ROLLING_QUARTER_SALES_UNGROUPED
                ),
                rolq_change=self._get_indicator_value(
                    product_df,
                    constants.INDICATOR_ROLLING_QUARTER_CHANGE_PREVIOUS_YEAR_SALES_UNGROUPED
                )
            )
        except ValueError as e:
            raise ValueError(f"Error calculating metrics for product {product}: {str(e)}")

    def _get_metrics(self, account_uuid: str, report_date: str) -> List[SalesMetric]:
        """Calculate sales metrics for all products for a given account and date."""
        sales_data = self._get_filtered_data(
            self.sales_df,
            report_date,
            account_uuid=account_uuid
        )

        metrics = []
        for product in sales_data['product_name'].unique():
            product_df = sales_data[sales_data['product_name'] == product]
            metrics.append(self._get_product_metrics(product_df, product))

        return metrics

    def _get_trends(self, account_uuid: str, hcp_uuid: str, report_date: str) -> List[Finding]:
        """Get sales trends for specific employee and HCP."""
        trends_data = self._get_filtered_data(
            self.sales_findings_df,
            report_date,
            account_uuid=account_uuid,
            hcp_uuid=hcp_uuid,
            type=constants.FINDING_TYPE_TRENDS
        )

        return [
            Finding(
                type=row['type'],
                text=self._format_finding_text(row['details'], row['product_name'])
            )
            for _, row in trends_data.iterrows()
        ]

    def _get_findings(self, account_uuid: str, hcp_uuid: str, report_date: str) -> List[Finding]:
        """Get sales findings for specific employee and HCP."""
        findings_data = self._get_filtered_data(
            self.sales_findings_df,
            report_date,
            account_uuid=account_uuid,
            hcp_uuid=hcp_uuid,
        )
        findings_data = findings_data[findings_data['type'] != constants.FINDING_TYPE_TRENDS]

        return [
            Finding(
                type=row['type'],
                text=self._format_finding_text(row['details'])
            )
            for _, row in findings_data.iterrows()
        ]

    def _get_insights(self, account_uuid: str, hcp_uuid: str, report_date: str) -> list[Insight]:
        """Get sales insights for specific employee and HCP."""
        insights_data = self._get_filtered_data(
            self.sales_findings_df,
            report_date,
            account_uuid=account_uuid,
            hcp_uuid=hcp_uuid
        )

        merged_insights_data = insights_data.merge(
            self.hcps_df.rename(columns={'name': 'hcp_name'})[['uuid', 'hcp_name']],
            left_on='hcp_uuid',
            right_on='uuid',
        ).merge(
            self.accounts_df.rename(columns={'name': 'account_name'})[['uuid', 'account_name']],
            left_on='account_uuid',
            right_on='uuid'
        ).merge(
            self.employees_df.rename(columns={'name': 'employee_name'})[['uuid', 'employee_name']],
            left_on='employee_uuid',
            right_on='uuid'
        )

        grouped_insights_data = merged_insights_data.groupby(
            ['hcp_name', 'account_name', 'employee_name']
        ).agg(
            finding=('type', lambda types: '; '.join(
                [f"{t} with details: {details} and product: {product}"
                 for t, details, product in zip(types, merged_insights_data.loc[types.index, 'details'],
                                                merged_insights_data.loc[types.index, 'product_name'])]
            ))
        ).reset_index()[['hcp_name', 'account_name', 'employee_name', 'finding']]

        insights = GPTInsightsGenerator().generate_insights_for_findings(grouped_insights_data)

        return [
            Insight(
                text=self._format_finding_text(row)
            )
            for row in insights
        ]

    def get_sales_data(
            self,
            account_uuid: str,
            hcp_uuid: str,
            employee_uuid: str,
            report_date: str
    ) -> SalesData:
        return SalesData(
            account_uuid=account_uuid,
            hcp_uuid=hcp_uuid,
            employee_uuid=employee_uuid,
            metrics=self._get_metrics(account_uuid, report_date),
            trends=self._get_trends(account_uuid, hcp_uuid, report_date),
            findings=self._get_findings(account_uuid, hcp_uuid, report_date),
            insights=self._get_insights(account_uuid, hcp_uuid, report_date)
        )

    def get_sales_data_for_employee(self, employee_uuid: str) -> List[SalesData]:
        employee_visits = self.planned_visits_df[self.planned_visits_df['employee_uuid'] == employee_uuid]
        first_day_last_month, last_month_name = DateUtility.get_previous_month_info()

        sales_data = []
        for _, visit in employee_visits.iterrows():
            sales_data.append(
                self.get_sales_data(
                    account_uuid=visit['account_uuid'],
                    hcp_uuid=visit['hcp_uuid'],
                    employee_uuid=visit['employee_uuid'],
                    report_date=first_day_last_month.isoformat()
                )
            )

        return sales_data

    def get_all_data_dataframe(self):
        unique_employees = self.planned_visits_df['employee_uuid'].unique()

        data = []
        for employee_uuid in unique_employees:
            sales_data = self.get_sales_data_for_employee(employee_uuid)
            if sales_data:
                df = pd.DataFrame(asdict(sales) for sales in sales_data)
                data.append(df)

        return pd.concat(data)
