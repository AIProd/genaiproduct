from typing import Optional, List

import pandas as pd

from modules.global_utils import FindingResult
from modules.sales import constants
from modules.sales.findings.finding import Finding


class MSDFinding(Finding):
    def generate(self, data: pd.DataFrame) -> Optional[List[FindingResult]]:
        account_uuid = data['account_uuid'].iloc[0]
        hcp_uuid = data['hcp_uuid'].iloc[0]
        employee_uuid = data['employee_uuid'].iloc[0]

        current_orders = self._get_current_orders(data)
        msd_recommendations = self._get_msd_recommendations(data, list(current_orders.keys()))

        if not msd_recommendations:
            return None

        details = f"MSD orders recommended for: {', '.join(msd_recommendations)}"

        return [
            FindingResult(
                account_uuid=account_uuid,
                hcp_uuid=hcp_uuid,
                employee_uuid=employee_uuid,
                product_name=None,
                type=constants.FINDING_TYPE_MSD_ORDERS_RECOMMENDATIONS,
                details=details
            )
        ]

    @staticmethod
    def _get_current_orders(hcp_data: pd.DataFrame) -> dict:
        return hcp_data.groupby('product_name')['source'].last().to_dict()

    @staticmethod
    def _get_msd_recommendations(hcp_data: pd.DataFrame, relevant_products: List[str]) -> List[str]:
        return [product for product in relevant_products if
                hcp_data[(hcp_data['product_name'] == product) & (hcp_data['source'] == 'MSD')].empty]
