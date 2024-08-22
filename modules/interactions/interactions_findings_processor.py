from difflib import SequenceMatcher
from io import StringIO

import pandas as pd
import re


class InteractionsFindingsProcessor:
    def __init__(self, input_data_frame: pd.DataFrame):
        self.input_data_frame = input_data_frame
        self.output_data_frame = pd.DataFrame()

    def calculate_findings(self):
        acc_names = self.input_data_frame['acc_name'].drop_duplicates()
        data = []

        for acc_name in acc_names:
            filtered_df = self.input_data_frame[self.input_data_frame["acc_name"] == acc_name]
            last_row = None
            for index, row in filtered_df.iterrows():
                if last_row is None:
                    last_row = row
                    continue
                finding = self._analyze_metrics(row, last_row)
                finding_calls = self._analyse_finding_interaction_calls(row)
                if finding:
                    data.append(dict(
                        acc_name=acc_name,
                        customer_name=row['customer_name'],
                        cases_date=row['cases_date'],
                        brand_name=row['brand_name'],
                        ter_code=row['ter_code'],
                        ter_emp_name=row['ter_emp_name'],
                        month=row['month'],
                        year=row['year'],
                        finding=finding
                    ))
                if finding_calls:
                    data.append(dict(
                        acc_name=acc_name,
                        customer_name=row['customer_name'],
                        cases_date=row['cases_date'],
                        brand_name=row['brand_name'],
                        ter_code=row['ter_code'],
                        ter_emp_name=row['ter_emp_name'],
                        month=row['month'],
                        year=row['year'],
                        finding=finding_calls
                    ))
                last_row = row

        self.output_data_frame = pd.concat([self.output_data_frame, pd.DataFrame(data)])

    def _analyze_metrics(self, row, last_row):
        delta_rolling_quarter_previous_month = float(last_row['rolling_quarter_change_previous_year'])
        delta_rolling_quarter_change_current_month = float(row['rolling_quarter_change_previous_year'])
        delta_mat_change_previous_month = float(last_row['moving_annual_total_change_previous_year'])
        delta_mat_change_current_month = float(row['moving_annual_total_change_previous_year'])

        conditions = (
            delta_mat_change_previous_month < 0,
            delta_rolling_quarter_previous_month < 0,
            delta_mat_change_current_month < 0,
            delta_rolling_quarter_change_current_month < 0
        )

        status_dict = {
            (True, True, True, True): "Long-term decline persists with no recent improvements.",
            (True, True, True, False): "Long-term decline persists, but recent improvements are noticeable.",
            (True, True, False, False): "Shift from long-term decline to consistent growth.",
            (True, True, False, True): "Despite long-term decline, recent downturns overshadow initial growth.",
            (False, True, True, True): "Recent improvements could not prevent continued long-term decline.",
            (False, True, False, False): "Long-term decline remains but recent improvements persist.",
            (False, True, False, True): "Complete shift from long-term decline to consistent growth.",
            (False, True, True, False): "Recent growth trends decline in spite of long-term growth.",
            (False, False, True, True): "Transition from consistent growth to long-term decline.",
            (False, False, False, True): "Despite recent growth, long-term growth turns into decline.",
            (False, False, False, False): "Consistent growth continues both in the long term and recently.",
            (False, False, False, True): "Long-term growth persists despite recent downturns.",
            (True, False, True, True): "Decline in recent growth trends leads to overall long-term decline.",
            (True, False, False, True): "Long-term growth turns into decline despite recent growth.",
            (False, False, True, False): "Recent downturns are replaced by persistent growth.",
            (False, False, False, True): "Long-term growth continues despite a persistent downturn recently."
        }

        return status_dict.get(conditions, '')

    def _analyse_finding_interaction_calls(self, row):
        last_call = row["previous_call"]
        next_call = row["next_call"]

        if pd.isna(last_call):
            last_call = None

        if pd.isna(next_call):
            next_call = None

        if not last_call and not next_call:
            return "No calls happened nor are scheduled"

        if not last_call and next_call:
            return f"No calls happened but next call is scheduled to {next_call}"

        if last_call and not next_call:
            return f"Last call happened {last_call}. No future calls are scheduled."

        if last_call and next_call:
            return f"Last call happened {last_call} next call is scheduled to {next_call}."

    def get_processed_data(self) -> pd.DataFrame:
        return self.output_data_frame


    @staticmethod
    def is_valid_email(email):
        """Check if the email is in a valid format."""
        if not isinstance(email, str):
            return False
        email_regex = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
        return re.match(email_regex, email) is not None

    @staticmethod
    def semantic_match(name, email_user):
        """Check if the email user part matches the name using a similarity score."""
        name_parts = name.lower().split()
        email_user = email_user.lower()
        for part in name_parts:
            if SequenceMatcher(None, part, email_user).ratio() > 0.7:
                return True
        return False

    def classify_email(self, name, email):
        """Classify the email as invalid, personal, or non-personal."""
        if not self.is_valid_email(email):
            return "invalid"

        email_user, _ = email.split('@')
        if self.semantic_match(name, email_user):
            return "personal"
        else:
            return "non-personal"
