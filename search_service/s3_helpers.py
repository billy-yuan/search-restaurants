import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import os

load_dotenv()
s3 = boto3.client('s3')


def load_env_var(env_var_name: str):
    env_var = os.getenv(env_var_name)

    if env_var is None:
        raise ValueError("Env var {} not found".format(env_var_name))
    return env_var


def upload_file_to_s3(file_name: str, bucket: str, s3_object_name=None) -> bool:
    if s3_object_name is None:
        s3_object_name = file_name

    s3_client = boto3.client('s3')
    try:
        s3_client.upload_file(file_name, bucket, s3_object_name)
    except ClientError as e:
        print(e)
        return False
    print("Uploaded {} to {}".format(file_name, s3_object_name))
    return True


def download_file_from_s3(file_name: str, bucket: str, s3_object_name: str):
    """
    Download a file from s3 to disk.

    * `file_name`: path of the download destination on disk
    * `bucket`: S3 bucket name
    * `s3_object_name`: path of the file you want to download on s3
    """
    s3_client = boto3.client('s3')
    try:
        s3_client.download_file(bucket, s3_object_name, file_name)
    except ClientError as e:
        print(e)
        return False
    print("Downloaded {} to {}".format(s3_object_name, file_name))
    return True
