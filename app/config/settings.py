from pydantic import BaseModel
from dotenv import load_dotenv
import os
from app.utils.aws_params import get_ssm_parameter

load_dotenv()


class Settings(BaseModel):
    AWS_REGION: str
    BEDROCK_MODEL_ID: str
    LOG_LEVEL: str = "INFO"


# Fetch from environment first, then fallback to SSM
aws_region = os.getenv("AWS_REGION", "ca-central-1")
bedrock_model_id = os.getenv("BEDROCK_MODEL_ID")

if not bedrock_model_id:
    # Try fetching from Parameter Store
    bedrock_model_id = get_ssm_parameter("/retail-ops/bedrock-model-id", region=aws_region)

# Fallback for local development if both fail
if not bedrock_model_id:
    bedrock_model_id = "anthropic.claude-3-haiku-20240307-v1:0"

settings = Settings(
    AWS_REGION=aws_region,
    BEDROCK_MODEL_ID=bedrock_model_id,
    LOG_LEVEL=os.getenv("LOG_LEVEL", "INFO"),
)

