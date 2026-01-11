from langchain_aws import ChatBedrock
from app.config.settings import settings


def get_llm():
    return ChatBedrock(
        model_id=settings.BEDROCK_MODEL_ID,
        region_name=settings.AWS_REGION,
        temperature=0.2,
        max_tokens=1024,
    )
