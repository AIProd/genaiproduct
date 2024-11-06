from langchain_core.prompts import PromptTemplate

hcp_insight_prompt = PromptTemplate(
    input_variables=["hcp_name", "account_name", "employee_name", "finding"],
    template="""
         Role:
        You are a data analyst tasked with deriving actionable insights based on findings related to various healthcare professionals (HCPs). Your goal is to analyze the findings and provide strategic recommendations for the sales team.

        ---

         Audience:
        The insights are for the sales team members who are responsible for managing relationships with healthcare professionals. Insights should be practical, clear, and directly address business opportunities, risks, and follow-up actions.

        ---

         Format:
        For each healthcare professional, generate a concise insight (80-120 words) based on the provided findings. The insight should include:

        1. Business Opportunities: Identify any areas for potential growth or sales opportunities.
        2. Potential Risks: Highlight any risks or concerns that may require attention.
        3. Follow-up Strategy: Recommend next steps for me, including addressing any concerns or barriers.
        4. Cross-Selling or Product Uptake: If relevant, suggest cross-selling opportunities or observe any product trends or gaps.
        5. Additional Investigations: Mention any areas that may need further inquiry or clarification.

        Use the following template for generating insights:

        ---

         Template for Input:

         HCP Name: Name of HCP
         Account: Account under which HCP lies
         Employee: Me
         Finding: Combined findings


         Template for Output:
        Insight: Concise and actionable insight with Focus on business opportunities, risks, follow-up actions, and cross-selling, as applicable

        ---

         Example Insight:

        Insight: Markus Nadig is currently not purchasing VAXNUEVANCE, although interest in Gardasil9 has been noted. You should explore if there are any concerns regarding VAXNUEVANCE uptake. You may also want to inform him about recent reimbursement options for Gardasil9 in his canton. Additionally, consider addressing potential knowledge gaps on the benefits of VAXNUEVANCE could support cross-selling efforts.

        ---

         Input for Analysis:

         HCP Name: {hcp_name}
         Account: {account_name}
         Employee: {employee_name}
         Finding: {finding}

        ---

         Final Instructions:
        Generate insights for each HCP listed to be read by me, using the format and example above. The output should focus solely on the insights and follow the length guidelines of 80-120 words.
        """
)



email_findings_summary_prompt = PromptTemplate(
    input_variables=["subjects"],
    template="""
        Please review the following email subject lines from the past some months 
        and generate a one-line summary that captures the main themes and key actions 
        discussed in these emails. 
        The summary should be concise, professional, and appropriate for a business report:

        {subjects}

        Return only a single sentence as the summary.
    """
)