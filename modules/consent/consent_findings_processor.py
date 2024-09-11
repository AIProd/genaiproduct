from typing import List

import pandas as pd

from modules.consent.findings.finding import Finding
from modules.consent.findings.lack_of_explicit_consent import LackOfExplicitConsentFinding


class ConsentFindingsProcessor:
    def __init__(self, input_data_frame: pd.DataFrame):
        self.input_data_frame = input_data_frame
        self.findings_generators: List[Finding] = [
            LackOfExplicitConsentFinding()
        ]
        self.output_data_frame = pd.DataFrame(columns=['account_uuid',
                                                       'hcp_uuid',
                                                       'employee_uuid',
                                                       'type',
                                                       'details',
                                                       'timestamp',
                                                       ])

    def calculate_findings(self):
        findings = []
        for _, group in self.input_data_frame.groupby(['account_uuid', 'hcp_uuid', 'employee_uuid']):
            for finding_generator in self.findings_generators:
                result = finding_generator.generate(group)
                if result:
                    findings.append(result)

        self.output_data_frame = pd.DataFrame([finding.__dict__ for finding in findings], columns=[
            'account_uuid',
            'hcp_uuid',
            'employee_uuid',
            'type',
            'details',
            'timestamp',
        ])

    def get_processed_data(self) -> pd.DataFrame:
        return self.output_data_frame
