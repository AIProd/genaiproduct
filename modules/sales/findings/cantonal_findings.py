from typing import Optional, List
import pandas as pd

from modules.sales import constants
from modules.sales.findings.finding import Finding
from modules.sales.utils import FindingResult
from typing import Optional, List

import pandas as pd

from modules.sales import constants
from modules.sales.findings.finding import Finding
from modules.sales.utils import FindingResult


class CantonalFinding(Finding):
    def __init__(self, hcps_df: pd.DataFrame):
        self.hcps_df = hcps_df

    def generate(self, data: pd.DataFrame) -> Optional[List[FindingResult]]:
        findings = []
        account_uuid = data['account_uuid'].iloc[0]
        hcp_uuid = data['hcp_uuid'].iloc[0]
        employee_uuid = data['employee_uuid'].iloc[0]

        if not hcp_uuid:
            return None

        pediatric_data = data.merge(self.hcps_df, left_on='hcp_uuid', right_on='uuid', how='inner')
        gardasil_data = pediatric_data[pediatric_data['product_name'] == 'GARDASIL9']

        if pediatric_data.empty:
            return None

        if gardasil_data.empty:
            findings.append(
                FindingResult(
                    account_uuid=account_uuid,
                    hcp_uuid=hcp_uuid,
                    employee_uuid=employee_uuid,
                    type=constants.FINDING_TYPE_CANTONAL_PROGRAM,
                    details="HCP in account not buying GARDASIL9",
                    product_name=None
                )
            )

        if not gardasil_data.empty:
            latest_gardasil_record = gardasil_data.sort_values(by='timestamp').iloc[-1]
            order_category = latest_gardasil_record['category']

            if order_category != 'Cantonal':
                findings.append(
                    FindingResult(
                        account_uuid=account_uuid,
                        hcp_uuid=hcp_uuid,
                        employee_uuid=employee_uuid,
                        type=constants.FINDING_TYPE_CANTONAL_PROGRAM,
                        details="Buying GARDASIL9 but not via Cantonal category",
                        product_name="GARDASIL9"
                    )
                )

        return findings if findings else None