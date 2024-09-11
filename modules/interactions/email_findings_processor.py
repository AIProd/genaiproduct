import pandas as pd
from langchain.schema import HumanMessage

from modules.global_utils import LLM


class EmailFindingsProcessor:
    def __init__(self, email_data_frame: pd.DataFrame):
        self.email_data_frame = email_data_frame
        self.output_data_frame = pd.DataFrame()

    def generate_findings(self):

        hcp_groups = self.email_data_frame.groupby('hcp_uuid')

        findings = []

        for hcp_uuid, group in hcp_groups:
            for read_status in ['Read', 'Not Read']:
                relevant_emails = group[group['read_status'] == read_status]
                if not relevant_emails.empty:
                    subjects = ";".join(relevant_emails['subject'].tolist())
                    summary = self._generate_gpt_summary(subjects)

                    latest_email = relevant_emails.sort_values(by='cases_date').iloc[-1]
                    latest_date_sent = latest_email['cases_date']
                    latest_days_passed = latest_email['days_passed']

                    findings.append({
                        'hcp_uuid': hcp_uuid,
                        'subject_summary': summary,
                        'latest_date_sent': latest_date_sent,
                        'latest_days_passed': latest_days_passed,
                        'read_status': read_status,
                        'body_summary': latest_email['body']

                    })

        self.output_data_frame = pd.DataFrame(findings)

    def _generate_gpt_summary(self, subjects: str) -> str:

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
        if row['acceptation'] != 0 or row['reaction'] != 0 or row['total_opens'] != 0 or row[
            'total_actions'] != 0:
            return 'Read'
        return 'Not Read'