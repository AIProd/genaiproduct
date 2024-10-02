import pandas as pd
from langchain_openai import AzureChatOpenAI
from modules.global_utils import get_llm
from langchain.schema import HumanMessage
from generation.prompts import hcp_insight_prompt
from modules.global_utils import get_llm

class GPTInsightsGenerator:
    def __init__(self):
        self.llm = get_llm()

    def generate_prompt(self, row):
        prompt = hcp_insight_prompt.format(
            hcp_name=row['hcp_name'],
            account_name=row['account_name'],
            employee_name="Me",
            finding=row['finding']
        )
        return prompt

    def get_insight(self, prompt):
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content

    def generate_insights_for_findings(self, findings_df):
        if findings_df.empty:
            return ["Insights not available"]
        row = findings_df.iloc[0]
        prompt = self.generate_prompt(row)
        insight = self.get_insight(prompt)

        return [insight.replace("Insight:","").strip()]