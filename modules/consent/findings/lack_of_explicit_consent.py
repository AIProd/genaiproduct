from typing import Optional

import pandas as pd

from modules.consent.findings.finding import Finding
from modules.global_utils import FindingResult


class LackOfExplicitConsentFinding(Finding):
    def generate(self, data: pd.DataFrame) -> Optional[FindingResult]:
        account_uuid = data['account_uuid'].iloc[0]
        hcp_uuid = data['hcp_uuid'].iloc[0]
        employee_uuid = data['employee_uuid'].iloc[0]

        findings_details = []

        ae_data = data[data['indicator'] == 'cust_ae_consent_flag']
        if not ae_data.empty and ae_data['value'].iloc[0] == 'None':
            findings_details.append("Lack of explicit AE consent")

        me_data = data[data['indicator'] == 'cust_me_consent_flag']
        if not me_data.empty and me_data['value'].iloc[0] == 'None':
            findings_details.append("Lack of explicit ME consent")

        if findings_details:
            details = "; ".join(findings_details)
            return FindingResult(
                account_uuid=account_uuid,
                hcp_uuid=hcp_uuid,
                employee_uuid=employee_uuid,
                type="Consent",
                details=details
            )

        return None
