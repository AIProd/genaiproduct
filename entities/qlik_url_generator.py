from urllib.parse import urlencode
from datetime import datetime


class QlikSenseURLGenerator:
    BASE_QLIK_URL = "https://ghh.qlikeurss.merck.com/sense/app/9183f2cc-33c6-4b01-85da-aea707c65733"

    @staticmethod
    def generate_hcp_page_url(hcp_id: str) -> str:
        hcp_id = hcp_id.replace("CH-", "", 1)
        hcp_param = hcp_id.replace(' ', '')
        url = f"{QlikSenseURLGenerator.BASE_QLIK_URL}/sheet/72512643-9503-4b68-b202-796417d1c5b2/analysis/options/clearselections/select/hcp_id/{hcp_param}/select/HCP%20Territory%20Business%20Unit/"
        return url

    @staticmethod
    def generate_account_page_url(acc_id: str) -> str:
        account_param = str(acc_id).replace(' ', '')

        url = f"{QlikSenseURLGenerator.BASE_QLIK_URL}/sheet/79c854ca-ab30-4c33-bc2d-4e2f8fed9486/analysis/options/clearselections/select/acc_id/{account_param}/select/HCP%20Territory%20Business%20Unit/"
        return url

    @staticmethod
    def generate_customer_360_insights_url() -> str:
        url = f"{QlikSenseURLGenerator.BASE_QLIK_URL}/sheet/5a6304b8-d637-4e40-bc26-7a5eba10012c/state/analysis"

        return url
