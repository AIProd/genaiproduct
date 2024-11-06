import os
from dataclasses import dataclass
from typing import List, Dict

from langchain_openai import AzureChatOpenAI

from entities.entity_classes.account import Account
from entities.entity_classes.employee import Employee
from entities.entity_classes.hcp import HCP
from generation import constants


def get_first_row(df):
    if df.empty:
        return None
    else:
        return df.iloc[0]


def get_number_of_days_forward_for_planned_visits() -> int:
    import os
    return int(os.getenv("NUMBER_OF_DAYS_FORWARD_FOR_PLANNED_VISITS", str(constants.BUSINESS_DAYS_COUNT)))


def get_llm() -> AzureChatOpenAI:
    return AzureChatOpenAI(
        azure_endpoint=os.getenv("GP_TEAL_API"),
        openai_api_version=os.getenv("GP_TEAL_API_VERSION"),
        openai_api_key=os.getenv("GP_TEAL_API_KEY"),
        azure_deployment=os.getenv("GP_TEAL_DEPLOYMENT"),
        temperature=0,
        max_retries=1,
    )


from datetime import datetime, timedelta
import calendar


class DateUtility:
    @staticmethod
    def get_previous_month_info(reference_date: datetime = None) -> tuple[datetime, str]:
        """
        Get the first day and name of the previous month.

        Args:
            reference_date (datetime, optional): Reference date to calculate previous month.
                                               Defaults to current date if None.

        Returns:
            tuple: (first_day_of_previous_month: datetime, previous_month_name: str)
        """
        current_date = reference_date or datetime.now()

        first_day_current_month = current_date.replace(
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )

        last_day_previous_month = first_day_current_month - timedelta(days=1)
        first_day_previous_month = last_day_previous_month.replace(day=1)

        month_name = calendar.month_name[first_day_previous_month.month]

        return first_day_previous_month, month_name

    @staticmethod
    def format_date(date: datetime, format_str: str = "%Y-%m-%d") -> str:
        """
        Format a date according to the specified format string.

        Args:
            date (datetime): Date to format
            format_str (str): Format string (default: YYYY-MM-DD)

        Returns:
            str: Formatted date string
        """
        return date.strftime(format_str)


@dataclass
class SalesMetric:
    """Represents metrics for a product."""
    product_name: str
    mat: float
    mat_change: float
    rolq: float
    rolq_change: float


@dataclass
class InteractionsMetric:
    """Represents metrics for a channel."""
    channel: str
    mat: float
    mat_change: float
    rolq: float
    rolq_change: float


@dataclass
class ConsentMetric:
    """Represents metrics for a channel."""
    channel: str
    opt_in: bool
    opt_out: bool


@dataclass
class Finding:
    """Represents a finding or trend."""
    type: str
    text: str


@dataclass
class EmailCount:
    read: int
    clicked: int
    unread: int
    bounced: int
    total: int

@dataclass
class EmailCounts:
    approved: EmailCount
    marketing: EmailCount


@dataclass
class BouncedEmail:
    date: str
    email: str
    subject: str


@dataclass
class Insight:
    """Represents a finding or trend."""
    text: str


@dataclass
class SalesData:
    account_uuid: str
    hcp_uuid: str
    employee_uuid: str
    metrics: List[SalesMetric]
    trends: List[Finding]
    findings: List[Finding]
    insights: List[Insight]


@dataclass
class PreviousVisit:
    employee_name: str
    hcp_name: str
    date: str


@dataclass
class InteractionsData:
    account_uuid: str
    hcp_uuid: str
    employee_uuid: str
    metrics: List[InteractionsMetric]
    email_counts: EmailCounts
    email_summaries: List[Finding]
    bounced_data: Dict[str, List[BouncedEmail]]
    previous_visits: List[PreviousVisit]


@dataclass
class ConsentData:
    account_uuid: str
    hcp_uuid: str
    employee_uuid: str
    metrics: List[ConsentMetric]


@dataclass
class TemplateData:
    hcp: HCP
    account: Account
    employee: Employee
    other_hcps: List[HCP]
    visit_date: str
    report_month: str
    sales: SalesData
    interactions: InteractionsData
    consents: ConsentData

    def to_dict(self):
        return {
            'hcp': self.hcp,
            'account': self.account,
            'employee': self.employee,
            'other_hcps': self.other_hcps,
            'visit_date': self.visit_date,
            'report_month': self.report_month,
            'sales': self.sales,
            'interactions': self.interactions,
            'consents': self.consents,
        }


@dataclass
class VisitData:
    hcp: HCP
    account: Account
    date: str
    key_points: int


@dataclass
class EmailData:
    employee: Employee
    visits: List[VisitData]

    def to_dict(self):
        return {
            'employee': self.employee,
            'visits': self.visits
        }
