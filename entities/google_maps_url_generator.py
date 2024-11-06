from urllib.parse import quote_plus


class GoogleMapsURLGenerator:
    BASE_URL = "https://www.google.com/maps/search/"
    QUERY_PARAM = "api=1&query="

    @classmethod
    def generate_url(cls, account_name=None, street=None, city=None, zip_code=None):
        query_parts = list(filter(None, (account_name, street, city, zip_code)))
        if not query_parts:
            raise ValueError(
                "At least one piece of information (account_name, street, city, or zip_code) must be provided."
            )
        query = ", ".join(query_parts)
        encoded_query = quote_plus(query)
        return f"{cls.BASE_URL}?{cls.QUERY_PARAM}{encoded_query}"
