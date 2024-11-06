import pandas as pd

from modules.interactions.findings.email_finding import EmailFinding
from modules.interactions.findings.high_priority_engagement_finding import HighPriorityEngagementFinding


class InteractionsFindingsProcessor:
    def __init__(
            self,
            input_data_frame: pd.DataFrame,
    ):
        self.finding_groups = [
            {
                'columns': ['account_uuid', 'hcp_uuid', 'employee_uuid'],
                'generators': [
                    EmailFinding(),
                    HighPriorityEngagementFinding()
                ],
            },
        ]

        self.input_data_frame = input_data_frame
        self.output_data_frame = pd.DataFrame(columns=['account_uuid',
                                                       'hcp_uuid',
                                                       'employee_uuid',
                                                       'type',
                                                       'details',
                                                       'product_name',
                                                       'timestamp',
                                                       ])

    def calculate_findings(self):
        findings = []
        for group_config in self.finding_groups:
            for _, group in self.input_data_frame.groupby(group_config['columns']):
                for finding_generator in group_config['generators']:
                    result = finding_generator.generate(group)
                    if result:
                        findings.extend(result)

        self.output_data_frame = pd.DataFrame(
            columns=[
                'account_uuid',
                'hcp_uuid',
                'employee_uuid',
                'type',
                'details',
                'product_name',
                'timestamp',
            ],
            data=[finding.__dict__ for finding in findings]
        )

    def get_processed_data(self):
        return self.output_data_frame
