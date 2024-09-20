from typing import Optional, List

import pandas as pd

from modules.global_utils import FindingResult
from modules.sales import constants
from modules.sales.findings.finding import Finding


class MATTrends(Finding):

    def generate(self, data: pd.DataFrame) -> Optional[List[FindingResult]]:
        mat_df = data[data['indicator'] == constants.INDICATOR_MOVING_ANNUAL_TOTAL_CHANGE_PREVIOUS_YEAR].copy()
        rolq_df = data[data['indicator'] == constants.INDICATOR_ROLLING_QUARTER_CHANGE_PREVIOUS_YEAR].copy()

        if mat_df.empty or rolq_df.empty:
            return None

        findings = []

        merged_df = (
            pd.merge(mat_df, rolq_df, on=[
                'timestamp',
                'period',
                'employee_uuid',
                'hcp_uuid',
                'account_uuid',
                'product_name',
                'territory',
                'channel',
                'type',
                'metrics',
                'source',
                'category',
            ], suffixes=('_mat', '_rolq'))
            .sort_values(by='timestamp', ascending=False).reset_index())

        product_names = merged_df['product_name'].unique()

        account_uuid = data['account_uuid'].iloc[0]
        hcp_uuid = data['hcp_uuid'].iloc[0]
        employee_uuid = data['employee_uuid'].iloc[0]

        for product_name in product_names:
            product_df = merged_df[merged_df['product_name'] == product_name]

            if product_df.empty:
                continue

            if len(product_df) < 2:
                continue

            row = product_df.iloc[0]
            last_row = product_df.iloc[1]

            description = self._analyze_metrics(row, last_row)

            if not description:
                continue

            findings.append(FindingResult(
                account_uuid=account_uuid,
                hcp_uuid=hcp_uuid,
                employee_uuid=employee_uuid,
                type=constants.FINDING_TYPE_TRENDS,
                details=description,
                product_name=product_name
            ))

        return findings

    def _analyze_metrics(self, row, last_row):
        delta_rolling_quarter_previous_month = float(last_row['value_rolq'])
        delta_rolling_quarter_change_current_month = float(row['value_rolq'])
        delta_mat_change_previous_month = float(last_row['value_mat'])
        delta_mat_change_current_month = float(row['value_mat'])

        conditions = (
            delta_mat_change_previous_month < 0,
            delta_rolling_quarter_previous_month < 0,
            delta_mat_change_current_month < 0,
            delta_rolling_quarter_change_current_month < 0
        )

        status_dict = {
            (True, True, True, True): "Long-term decline persists with no recent improvements.",
            (True, True, True, False): "Long-term decline persists, but recent improvements are noticeable.",
            (True, True, False, False): "Shift from long-term decline to consistent growth.",
            (True, True, False, True): "Despite long-term decline, recent downturns overshadow initial growth.",
            (False, True, True, True): "Recent improvements could not prevent continued long-term decline.",
            (False, True, False, False): "Long-term decline remains but recent improvements persist.",
            (False, True, False, True): "Complete shift from long-term decline to consistent growth.",
            (False, True, True, False): "Recent growth trends decline in spite of long-term growth.",
            (False, False, True, True): "Transition from consistent growth to long-term decline.",
            (False, False, False, True): "Despite recent growth, long-term growth turns into decline.",
            (False, False, False, False): "Consistent growth continues both in the long term and recently.",
            (False, False, False, True): "Long-term growth persists despite recent downturns.",
            (True, False, True, True): "Decline in recent growth trends leads to overall long-term decline.",
            (True, False, False, True): "Long-term growth turns into decline despite recent growth.",
            (False, False, True, False): "Recent downturns are replaced by persistent growth.",
            (False, False, False, True): "Long-term growth continues despite a persistent downturn recently."
        }

        return status_dict.get(conditions, None)
