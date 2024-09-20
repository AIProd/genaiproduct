from typing import Optional, List

import pandas as pd

from modules.global_utils import FindingResult
from modules.sales import constants
from modules.sales.findings.finding import Finding


class UnderperformingAccounts(Finding):
    def generate(self, data: pd.DataFrame) -> Optional[List[FindingResult]]:
        findings = []
        account_uuid = data['account_uuid'].iloc[0]
        hcp_uuid = data['hcp_uuid'].iloc[0]
        employee_uuid = data['employee_uuid'].iloc[0]

        mat_growth_df = data[data['indicator'] == constants.INDICATOR_MOVING_ANNUAL_TOTAL_CHANGE_PREVIOUS_YEAR].copy()
        rolq_growth_df = data[data['indicator'] == constants.INDICATOR_ROLLING_QUARTER_CHANGE_PREVIOUS_YEAR].copy()

        if mat_growth_df.empty or rolq_growth_df.empty:
            return None

        mat_growth_df = mat_growth_df.sort_values(by='timestamp', ascending=False)
        rolq_growth_df = rolq_growth_df.sort_values(by='timestamp', ascending=False)

        most_recent_month = mat_growth_df['timestamp'].iloc[0]

        recent_mat_growth = mat_growth_df[mat_growth_df['timestamp'] == most_recent_month]
        recent_rolq_growth = rolq_growth_df[rolq_growth_df['timestamp'] == most_recent_month]

        for _, row in recent_mat_growth.iterrows():
            product_name = row['product_name']
            mat_growth_value = float(row['value'])
            rolq_growth_value = float(
                recent_rolq_growth[recent_rolq_growth['product_name'] == product_name]['value'].iloc[0])

            if mat_growth_value < 0 and rolq_growth_value < 0:
                findings.append(FindingResult(
                    account_uuid=account_uuid,
                    hcp_uuid=hcp_uuid,
                    employee_uuid=employee_uuid,
                    type="Underperforming Account",
                    details=f"Underperforming in {product_name} with MAT growth {mat_growth_value:.2f}% and ROLQ growth {rolq_growth_value:.2f}%",
                    product_name=product_name
                ))

        return findings if findings else None
