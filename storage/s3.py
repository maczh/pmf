import boto3
from botocore.exceptions import ClientError
from typing import List, Optional
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)
class S3Manager:
    def __init__(self, access_key: str, secret_key: str, endpoint_url: str = None, region_name: str = 'us-east-1', bucket: str = 'default'):
        """初始化S3连接"""
        self.client = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            endpoint_url=endpoint_url,
            region_name=region_name
        )
        self.endpoint_url = endpoint_url
        self.region_name = region_name
        self.bucket = bucket

    def create_bucket(self, bucket_name: str) -> bool:
        """创建bucket"""
        try:
            self.client.create_bucket(Bucket=bucket_name)
            return True
        except ClientError as e:
            print(f"Error creating bucket: {e}")
            return False

    def list_buckets(self) -> List[str]:
        """获取bucket列表"""
        try:
            response = self.client.list_buckets()
            return [bucket['Name'] for bucket in response['Buckets']]
        except ClientError as e:
            print(f"Error listing buckets: {e}")
            return []

    def delete_bucket(self, bucket_name: str) -> bool:
        """删除bucket"""
        try:
            self.client.delete_bucket(Bucket=bucket_name)
            return True
        except ClientError as e:
            print(f"Error deleting bucket: {e}")
            return False

    def upload_object(self, object_key: str, file_path: str, bucket_name: str = None) -> bool:
        """上传对象"""
        try:
            if not bucket_name:
                bucket_name = self.bucket
            self.client.upload_file(file_path, bucket_name, object_key)
            return True
        except ClientError as e:
            print(f"Error uploading object: {e}")
            return False

    def get_object(self, object_key: str, file_path: str, bucket_name: str = None) -> bool:
        """获取对象"""
        try:
            if not bucket_name:
                bucket_name = self.bucket
            self.client.download_file(bucket_name, object_key, file_path)
            return True
        except ClientError as e:
            print(f"Error downloading object: {e}")
            return False

    def list_objects(self, prefix: str = '', bucket_name: str = None) -> List[str]:
        """获取对象列表"""
        try:
            if not bucket_name:
                bucket_name = self.bucket
            response = self.client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
            logger.debug(f"Objects in bucket {bucket_name}: {response}")
            return response.get('Contents', [])
        except ClientError as e:
            print(f"Error listing objects: {e}")
            return []

    def delete_object(self, object_key: str, bucket_name: str = None) -> bool:
        """删除对象"""
        try:
            if not bucket_name:
                bucket_name = self.bucket
            self.client.delete_object(Bucket=bucket_name, Key=object_key)
            return True
        except ClientError as e:
            print(f"Error deleting object: {e}")
            return False

    def rename_object(self, old_key: str, new_key: str, bucket_name: str = None) -> bool:
        """对象改名"""
        try:
            if not bucket_name:
                bucket_name = self.bucket
            self.client.copy_object(
                CopySource={'Bucket': bucket_name, 'Key': old_key},
                Bucket=bucket_name,
                Key=new_key
            )
            self.client.delete_object(Bucket=bucket_name, Key=old_key)
            return True
        except ClientError as e:
            print(f"Error renaming object: {e}")
            return False

    def get_object_url(self, object_key: str, expires_in: int = 3600, bucket_name: str = None) -> Optional[str]:
        """生成对象HTTP URL链接"""
        try:
            if not bucket_name:
                bucket_name = self.bucket
            url = self.client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket_name, 'Key': object_key},
                ExpiresIn=expires_in
            )
            return url
        except ClientError as e:
            print(f"Error generating URL: {e}")
            return None