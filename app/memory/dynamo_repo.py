import os
import boto3
from botocore.exceptions import ClientError

TABLE_NAME = os.getenv("DYNAMO_TABLE_NAME")
REGION = os.getenv("AWS_REGION")

dynamodb = boto3.resource("dynamodb", region_name=REGION)
table = dynamodb.Table(TABLE_NAME)


class AgentMemory:
    @staticmethod
    def get_memory(sku: str) -> dict:
        try:
            response = table.get_item(Key={"sku": sku})
            return response.get("Item", {})
        except ClientError as e:
            print(f"Error reading memory: {e}")
            return {}

    @staticmethod
    def update_memory(sku: str, last_action: str, last_decision: str):
        try:
            table.put_item(
                Item={
                    "sku": sku,
                    "last_action": last_action,
                    "last_decision": last_decision,
                }
            )
        except ClientError as e:
            print(f"Error writing memory: {e}")
