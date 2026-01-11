import os
import boto3
from botocore.exceptions import ClientError

TABLE_NAME = os.getenv("SALES_TABLE_NAME")
REGION = os.getenv("AWS_REGION")

dynamodb = boto3.resource("dynamodb", region_name=REGION)
table = dynamodb.Table(TABLE_NAME)


class SalesData:
    @staticmethod
    def get_sales(sku: str) -> dict:
        try:
            response = table.get_item(Key={"sku": sku})
            return response.get("Item", {})
        except ClientError as e:
            print(f"Error reading sales data: {e}")
            return {}
    @staticmethod
    def get_all_skus() -> list:
        try:
            response = table.scan(ProjectionExpression="sku")
            return [item["sku"] for item in response.get("Items", [])]
        except ClientError as e:
            print(f"Error scanning sales table: {e}")
            return []

