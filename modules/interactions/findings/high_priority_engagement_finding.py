from typing import List, Optional
import pandas as pd
from langchain.schema import HumanMessage

from modules.global_utils import get_llm, FindingResult
from modules.interactions import constants
from modules.interactions.findings.finding import Finding


class HighPriorityEngagementFinding(Finding):

    def generate(self, data: pd.DataFrame) -> Optional[List[FindingResult]]:
        data = data[data['indicator'] == constants.INDICATOR_HIGH_PRIORITY_ACCOUNT_DAYS_WITHOUT_INTERACTION]
        hcp_groups = data.groupby('hcp_uuid')

        findings = []
        for _, group in hcp_groups:
            account_uuid = data['account_uuid'].iloc[0]
            hcp_uuid = data['hcp_uuid'].iloc[0]
            employee_uuid = data['employee_uuid'].iloc[0]
            product_name = data['product_name'].iloc[0]

            if not group.empty:
                latest_interaction = group.sort_values(by='timestamp').iloc[-1]
                latest_date = latest_interaction['timestamp']
                hcp_info = f"High-priority engagement account due to lack of face-to-face and email interaction for over a year, with the last attempted contact on {latest_date}"
                #summary = self._generate_gpt_summary(hcp_info)
                findings.append(FindingResult(
                    account_uuid=account_uuid,
                    hcp_uuid=hcp_uuid,
                    employee_uuid=employee_uuid,
                    type=constants.FINDING_TYPE_HIGH_PRIORITY_ENGAGEMENT,
                    details=hcp_info,
                    product_name=product_name,
                    timestamp=latest_date
                ))

        return findings

    @staticmethod
    def _generate_gpt_summary(hcp_info: str) -> str:
        prompt = f"Provide a summary in one line about the high-priority engagement account: {hcp_info}"
        llm = get_llm()
        response = llm([HumanMessage(content=prompt)])
        return response.content.strip()