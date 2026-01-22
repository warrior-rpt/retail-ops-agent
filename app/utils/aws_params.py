import boto3
from botocore.exceptions import ClientError
import os

def get_ssm_parameter(name: str, region: str = None) -> str:
    """
    Fetch a parameter from AWS SSM Parameter Store.
    """
    if region is None:
        region = os.getenv("AWS_REGION", "ca-central-1")
        
    ssm = boto3.client("ssm", region_name=region)
    try:
        response = ssm.get_parameter(Name=name, WithDecryption=True)
        return response["Parameter"]["Value"]
    except ClientError as e:
        print(f"Error fetching parameter {name}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error fetching parameter {name}: {e}")
        return None
