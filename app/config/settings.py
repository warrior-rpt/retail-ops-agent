from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseModel):
    AWS_REGION: str
    BEDROCK_MODEL_ID: str
    LOG_LEVEL: str = "INFO"


settings = Settings(
    AWS_REGION=os.getenv("AWS_REGION"),
    BEDROCK_MODEL_ID=os.getenv("BEDROCK_MODEL_ID"),
    LOG_LEVEL=os.getenv("LOG_LEVEL", "INFO"),
)

