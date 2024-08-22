from datetime import datetime, timedelta
from typing import Optional, List

import numpy as np
import pandas as pd

from modules.sales import constants
from modules.sales.findings.finding import Finding
from modules.sales.utils import FindingResult


class CrossSellingFinding(Finding):
    def __init__(self, cross_selling_map: pd.DataFrame, hcps_df: pd.DataFrame, months_threshold: int = 12):
        self.cross_selling_map = cross_selling_map
        self.hcps_df = hcps_df
        self.months_threshold = months_threshold

    def generate(self, data: pd.DataFrame) -> Optional[List[FindingResult]]:
        account_uuid = data['account_uuid'].iloc[0]
        hcp_uuid = data['hcp_uuid'].iloc[0]
        employee_uuid = data['employee_uuid'].iloc[0]

        if not hcp_uuid:
            return None

        account_data = self._preprocess_data(data)
        cutoff_date = datetime.now() - timedelta(days=self.months_threshold * 30)
        account_products = self._get_recent_purchases(account_data)

        merged_df = self._merge_with_hcp_data(account_data)

        merged_df = self._merge_with_cross_selling_map(merged_df)

        current_purchases, opportunities = self._categorize_products(merged_df, account_products, cutoff_date)

        if not current_purchases:
            return None

        current_str = self._format_current_purchases(current_purchases)
        opp_str = self._format_opportunities(opportunities)
        details = f"{current_str}. {opp_str}".strip()

        if not opp_str:
            return None

        return [
            FindingResult(
                account_uuid=account_uuid,
                hcp_uuid=hcp_uuid,
                employee_uuid=employee_uuid,
                product_name=None,
                type=constants.FINDING_TYPE_CROSS_SELLING_OPPORTUNITIES,
                details=details
            )
        ]

    @staticmethod
    def _preprocess_data(account_data: pd.DataFrame) -> pd.DataFrame:
        account_data = account_data.copy()
        account_data['timestamp'] = pd.to_datetime(account_data['timestamp'])
        account_data['product_name'] = account_data['product_name'].replace({np.nan: None})
        return account_data

    @staticmethod
    def _get_recent_purchases(account_data: pd.DataFrame) -> pd.DataFrame:
        return account_data.groupby(['account_uuid', 'hcp_uuid', 'product_name'])['timestamp'].max().unstack(
            level='product_name')

    def _merge_with_cross_selling_map(self, account_data: pd.DataFrame) -> pd.DataFrame:
        return pd.merge(
            account_data[['account_uuid', 'hcp_uuid', 'specialty']].drop_duplicates(),
            self.cross_selling_map,
            on='specialty',
            how='left'
        )

    def _merge_with_hcp_data(self, account_data: pd.DataFrame) -> pd.DataFrame:
        return pd.merge(
            account_data,
            self.hcps_df[['uuid', 'specialty']],
            left_on='hcp_uuid',
            right_on='uuid',
            how='left'
        )

    @staticmethod
    def _categorize_products(group: pd.DataFrame, products: pd.DataFrame, cutoff_date: datetime) -> tuple:
        current_purchases = set()
        opportunities = {}

        for _, row in group.iterrows():
            for product in [row['product_a'], row['product_b']]:
                if pd.notna(product):
                    if product in products.columns:
                        last_sale_date = products[product].iloc[0]
                        if pd.notna(last_sale_date):
                            if last_sale_date >= cutoff_date:
                                current_purchases.add(product)
                            else:
                                months_since_last_sale = (datetime.now() - last_sale_date).days // 30
                                opportunities[product] = f"no sales in {months_since_last_sale} months"
                        else:
                            opportunities[product] = "no sales ever"
                    elif product not in current_purchases:
                        opportunities[product] = "no sales ever"

        for product in current_purchases:
            opportunities.pop(product, None)

        return current_purchases, opportunities

    @staticmethod
    def _format_current_purchases(current_purchases: set) -> str:
        return f"Buying product{'s' if len(current_purchases) > 1 else ''}: {', '.join(current_purchases)}"

    @staticmethod
    def _format_opportunities(opportunities: dict) -> str:
        return f"Cross selling opportunities for: {'; '.join([f'{k} ({v})' for k, v in opportunities.items()])}" if opportunities else ""

