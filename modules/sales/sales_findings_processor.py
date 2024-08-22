import pandas as pd

from modules.sales.findings.crosselling_oportunities import CrossSellingFinding
from modules.sales.findings.mat_trends import MATTrends
from modules.sales.findings.msd_orders import MSDFinding
from modules.sales.findings.cantonal_findings import CantonalFinding
from modules.sales.findings.underperforming_accounts import UnderperformingAccounts
from modules.sales.findings.highperforming_account import HighperformingAccounts


class SalesFindingsProcessor:
    def __init__(
            self,
            input_data_frame: pd.DataFrame,
            cross_selling_map: pd.DataFrame,
            hcps_df: pd.DataFrame
    ):
        self.finding_groups = [
            {
                'columns': ['account_uuid', 'hcp_uuid', 'employee_uuid'],
                'generators': [
                    CrossSellingFinding(cross_selling_map, hcps_df),
                    MSDFinding(),
                    MATTrends(),
                    CantonalFinding(hcps_df),
                    UnderperformingAccounts(),
                    HighperformingAccounts()
                ],
            },
        ]

        self.input_data_frame = input_data_frame
        self.output_data_frame = pd.DataFrame()

    def calculate_findings(self):
        findings = []
        for group_config in self.finding_groups:
            for _, group in self.input_data_frame.groupby(group_config['columns']):
                for finding_generator in group_config['generators']:
                    result = finding_generator.generate(group)
                    if result:
                        findings.extend(result)

        self.output_data_frame = pd.DataFrame([finding.__dict__ for finding in findings])

    def get_processed_data(self):
        return self.output_data_frame
