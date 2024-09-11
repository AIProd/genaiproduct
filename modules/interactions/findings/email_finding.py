from typing import List, Optional

import pandas as pd
from langchain.schema import HumanMessage

from modules.global_utils import LLM
from modules.interactions import constants
from modules.interactions.findings.finding import Finding
from modules.interactions.utils import FindingResult


class EmailFinding(Finding):

    def generate(self, data: pd.DataFrame) -> Optional[List[FindingResult]]:

        data = data[data['indicator'] == 'email']
        data['read_status'] = data.apply(self._determine_read_status, axis=1)

        hcp_groups = data.groupby('hcp_uuid')

        findings = []
        for _, group in hcp_groups:
            account_uuid = data['account_uuid'].iloc[0]
            hcp_uuid = data['hcp_uuid'].iloc[0]
            employee_uuid = data['employee_uuid'].iloc[0]
            product_name = data['product_name'].iloc[0]

            for read_status in ['Read', 'Not Read']:
                relevant_emails = group[group['read_status'] == read_status]
                if not relevant_emails.empty:
                    subjects = ";".join(relevant_emails['subject'].tolist())
                    summary = self._generate_gpt_summary(subjects)

                    latest_email = relevant_emails.sort_values(by='timestamp').iloc[-1]
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
        response = LLM(
            [
                HumanMessage(
                    content=prompt
                ),

            ])

        summary = response.content
        return summary.strip()

    def _determine_read_status(self, row):
        if row['acceptation'] != 0 or row['reaction'] != 0 or row['total_opens'] != 0 or row['total_actions'] != 0:
            return 'Read'
        return 'Not Read'
