from typing import List, Optional, Dict
import pandas as pd
from langchain.schema import HumanMessage
from modules.global_utils import get_llm, FindingResult
from modules.interactions import constants
from modules.interactions.findings.finding import Finding
from generation.prompts import email_findings_summary_prompt


class EmailFinding(Finding):

    def generate(self, data: pd.DataFrame) -> Optional[List[FindingResult]]:
        findings = []

        channels = {
            'AE - Veeva': {
                'clicked': constants.FINDING_TYPE_CLICKED_EMAIL_AE,
                'read': constants.FINDING_TYPE_READ_EMAIL_AE,
                'unread': constants.FINDING_TYPE_UNREAD_EMAIL_AE,
                'summary': constants.FINDING_TYPE_EMAIL_FINDINGS_AE,
            },
            'SFMC Marketing Email': {
                'clicked': constants.FINDING_TYPE_CLICKED_EMAIL_ME,
                'read': constants.FINDING_TYPE_READ_EMAIL_ME,
                'unread': constants.FINDING_TYPE_UNREAD_EMAIL_ME,
                'summary': constants.FINDING_TYPE_EMAIL_FINDINGS_ME,
            },
        }

        for channel, types in channels.items():
            channel_data = data[data["channel"] == channel]

            # Marketing Email Summary
            marketing_email_data = channel_data[
                channel_data[constants.COLUMN_INDICATOR] == constants.INDICATOR_MARKETING_EMAIL
                ]
            findings.extend(self._generate_findings_for_group(marketing_email_data, types['summary']))

            # Clicked, Read, and Unread Emails
            email_categories = {
                constants.INDICATOR_CLICKED_EMAIL: types['clicked'],
                constants.INDICATOR_READ_EMAIL: types['read'],
                constants.INDICATOR_UNREAD_EMAIL: types['unread'],
            }
            for indicator, email_type in email_categories.items():
                filtered_data = channel_data[channel_data[constants.COLUMN_INDICATOR] == indicator]
                findings.extend(self._generate_findings_for_group(filtered_data, email_type))

        return findings

    def _generate_findings_for_group(self, data: pd.DataFrame, email_type: str) -> List[FindingResult]:
        """Generate findings for any email group, with the provided email type."""
        findings = []
        hcp_groups = data.groupby([constants.COLUMN_ACCOUNT_UUID, constants.COLUMN_HCP_UUID, constants.COLUMN_EMPLOYEE_UUID])

        for _, group in hcp_groups:
            if not group.empty:

                account_uuid = group[constants.COLUMN_ACCOUNT_UUID].iloc[0]
                hcp_uuid = group[constants.COLUMN_HCP_UUID].iloc[0]
                employee_uuid = group[constants.COLUMN_EMPLOYEE_UUID].iloc[0]
                product_name = group[constants.COLUMN_PRODUCT_NAME].iloc[0]

                subjects = " | ".join(group[constants.COLUMN_SUBJECT].unique())
                summary = self._generate_gpt_summary(subjects)

                latest_date_sent = group[constants.COLUMN_TIMESTAMP].max()

                findings.append(FindingResult(
                    account_uuid=account_uuid,
                    hcp_uuid=hcp_uuid,
                    employee_uuid=employee_uuid,
                    type=email_type,
                    details=summary,
                    product_name=product_name,
                    timestamp=latest_date_sent
                ))

        return findings


    @staticmethod
    def _generate_gpt_summary(subjects: str) -> str:

        if not subjects:
            return constants.NO_EMAILS_MESSAGE

        prompt_content = email_findings_summary_prompt.format(subjects=subjects)
        llm = get_llm()
        response = llm.invoke([HumanMessage(content=prompt_content)])
        return response.content.strip()