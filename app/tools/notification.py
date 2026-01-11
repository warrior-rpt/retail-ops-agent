
import os
import boto3

TOPIC_ARN = os.getenv("SNS_TOPIC_ARN")
REGION = os.getenv("AWS_REGION")

sns = boto3.client("sns", region_name=REGION)


class Notifier:
    @staticmethod
    def send_email(subject: str, message: str):
        if not TOPIC_ARN:
            print("SNS_TOPIC_ARN not configured")
            return

        sns.publish(
            TopicArn=TOPIC_ARN,
            Subject=subject,
            Message=message
        )

