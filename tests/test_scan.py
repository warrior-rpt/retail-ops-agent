import os
import boto3
from dotenv import load_dotenv

load_dotenv()

# Simulate Lambda environment
os.environ["SALES_TABLE_NAME"] = "RetailSalesData"
os.environ["AWS_REGION"] = "ca-central-1"

from app.memory.sales_data import SalesData

def test_scan():
    print(f"Testing scan on table: {os.getenv('SALES_TABLE_NAME')} in region: {os.getenv('AWS_REGION')}")
    skus = SalesData.get_all_skus()
    print(f"Found SKUs: {skus}")

if __name__ == "__main__":
    test_scan()
