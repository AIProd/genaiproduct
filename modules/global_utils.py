import os

from langchain_openai import AzureChatOpenAI

LLM = AzureChatOpenAI(
    azure_endpoint=os.getenv("GP_TEAL_API"),
    openai_api_version=os.getenv("GP_TEAL_API_VERSION"),
    openai_api_key=os.getenv("GP_TEAL_API_KEY"),
    azure_deployment=os.getenv("GP_TEAL_DEPLOYMENT"),
    max_retries=1,
)
