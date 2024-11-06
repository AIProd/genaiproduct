from langchain.schema import HumanMessage

from generation.prompts import hcp_insight_prompt
from generation.utils import get_llm


class GPTInsightsGenerator:
    @staticmethod
    def generate_prompt(row):
        prompt = hcp_insight_prompt.format(
            hcp_name=row['hcp_name'],
            account_name=row['account_name'],
            employee_name="Me",
            finding=row['finding']
        )
        return prompt

    @staticmethod
    def get_insight(prompt):
        response = get_llm().invoke([HumanMessage(content=prompt)])
        return response.content

    @staticmethod
    def generate_insights_for_findings(findings_df):
        if findings_df.empty:
            return ["Insights not available"]
        row = findings_df.iloc[0]
        prompt = GPTInsightsGenerator.generate_prompt(row)
        insight = GPTInsightsGenerator.get_insight(prompt)

        return [insight.replace("Insight:", "").strip()]
