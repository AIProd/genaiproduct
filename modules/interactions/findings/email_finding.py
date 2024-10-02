from typing import List, Optional

import pandas as pd
from langchain.schema import HumanMessage

from modules.global_utils import get_llm, FindingResult
from modules.interactions import constants
from modules.interactions.findings.finding import Finding


class EmailFinding(Finding):

    def generate(self, data: pd.DataFrame) -> Optional[List[FindingResult]]:

        data = data[data['indicator'] == constants.INDICATOR_MARKETING_EMAIL]

        hcp_groups = data.groupby('hcp_uuid')

        findings = []
        for _, group in hcp_groups:
            account_uuid = data['account_uuid'].iloc[0]
            hcp_uuid = data['hcp_uuid'].iloc[0]
            employee_uuid = data['employee_uuid'].iloc[0]
            product_name = data['product_name'].iloc[0]

            if not group.empty:
                subjects = ";".join(group['subject'].tolist())
                summary = self._generate_gpt_summary(subjects)

                latest_email = group.sort_values(by='timestamp').iloc[-1]
                latest_date_sent = latest_email['timestamp']

                findings.append(FindingResult(
                    account_uuid=account_uuid,
                    hcp_uuid=hcp_uuid,
                    employee_uuid=employee_uuid,
                    type=constants.FINDING_TYPE_EMAIL_FINDINGS,
                    details=summary,
                    product_name=product_name,
                    timestamp=latest_date_sent
                ))

        return findings

    @staticmethod
    def _generate_gpt_summary(subjects: str) -> str:

        if not subjects:
            return f"No emails."
        prompt = f"Ingest and combine all the emails subjects together and output just a concise one line in english : {subjects}."
        llm = get_llm()
        response = llm.invoke(
            [
                HumanMessage(
                    content=prompt
                ),

            ])

        summary = response.content
        return summary.strip()
