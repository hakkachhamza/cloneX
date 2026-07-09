import os
import shutil
from pathlib import Path
from typing import BinaryIO

import boto3
from botocore.exceptions import ClientError

from app.config import get_settings

settings = get_settings()


class StorageService:
    def __init__(self):
        self.storage_type = settings.storage_type
        self.local_path = Path(settings.storage_local_path)
        self.local_path.mkdir(parents=True, exist_ok=True)

        if self.storage_type == "s3":
            self.s3 = boto3.client(
                "s3",
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
                region_name=settings.aws_region,
                endpoint_url=settings.s3_endpoint_url,
            )
            self.bucket = settings.s3_bucket_name

    def get_base_path(self, project_id: str) -> Path:
        return self.local_path / project_id

    def write_text(self, project_id: str, relative_path: str, content: str) -> None:
        if self.storage_type == "local":
            path = self.get_base_path(project_id) / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        else:
            self.s3.put_object(Bucket=self.bucket, Key=f"{project_id}/{relative_path}", Body=content.encode("utf-8"))

    def write_bytes(self, project_id: str, relative_path: str, data: bytes) -> None:
        if self.storage_type == "local":
            path = self.get_base_path(project_id) / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        else:
            self.s3.put_object(Bucket=self.bucket, Key=f"{project_id}/{relative_path}", Body=data)

    def read_text(self, project_id: str, relative_path: str) -> str:
        if self.storage_type == "local":
            path = self.get_base_path(project_id) / relative_path
            return path.read_text(encoding="utf-8")
        else:
            response = self.s3.get_object(Bucket=self.bucket, Key=f"{project_id}/{relative_path}")
            return response["Body"].read().decode("utf-8")

    def exists(self, project_id: str, relative_path: str) -> bool:
        if self.storage_type == "local":
            return (self.get_base_path(project_id) / relative_path).exists()
        else:
            try:
                self.s3.head_object(Bucket=self.bucket, Key=f"{project_id}/{relative_path}")
                return True
            except ClientError:
                return False

    def delete_project(self, project_id: str) -> None:
        if self.storage_type == "local":
            path = self.get_base_path(project_id)
            if path.exists():
                shutil.rmtree(path)
        else:
            paginator = self.s3.get_paginator("list_objects_v2")
            pages = paginator.paginate(Bucket=self.bucket, Prefix=f"{project_id}/")
            keys = [{"Key": obj["Key"]} for page in pages for obj in page.get("Contents", [])]
            if keys:
                self.s3.delete_objects(Bucket=self.bucket, Delete={"Objects": keys})
