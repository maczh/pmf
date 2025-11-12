from typing import Optional, Iterable, Union, Dict, Any, List
import io
import os
import oss2

"""
File: d:/Projects/python/pmgin/storage/alioss.py

阿里云 OSS 管理类封装（基于 oss2）
需要 pip install oss2
"""



class OSSManager:
    """
    简单的阿里云 OSS 管理类封装。
    用法示例：
        mgr = OSSManager(access_key_id, access_key_secret, endpoint)
        mgr.connect(bucket_name)  # 可选地立即连接到某个 bucket
    """

    def __init__(
        self,
        access_key_id: str,
        access_key_secret: str,
        endpoint: str,
        bucket_name: Optional[str] = None,
        sts_token: Optional[str] = None,
    ):
        """
        初始化管理器（仅创建 auth），不自动创建 bucket 实例，除非传入 bucket_name 并调用 connect。
        endpoint 示例: "oss-cn-hangzhou.aliyuncs.com"
        如果使用 OSS 的内网或自定义域名，请填入相应的 endpoint。
        """
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.endpoint = endpoint
        self.sts_token = sts_token
        self.auth = oss2.StsAuth(access_key_id, access_key_secret, sts_token) if sts_token else oss2.Auth(access_key_id, access_key_secret)
        self.bucket: Optional[oss2.Bucket] = None
        if bucket_name:
            self.connect(bucket_name)

    def connect(self, bucket_name: str) -> oss2.Bucket:
        """
        连接到指定 bucket 并返回 Bucket 对象（并保存为 self.bucket）。
        """
        self.bucket = oss2.Bucket(self.auth, self.endpoint, bucket_name)
        return self.bucket

    def create_bucket(self, bucket_name: str, acl: str = oss2.BUCKET_ACL_PRIVATE) -> Dict[str, Any]:
        """
        创建 bucket。acl 可选: oss2.BUCKET_ACL_PRIVATE / PUBLIC_READ / PUBLIC_READ_WRITE
        返回服务器响应的 headers/info。
        """
        service = oss2.Service(self.auth, self.endpoint)
        # oss2 没有直接的 create_bucket 在 service 上，使用 Bucket 的 create_bucket
        bucket = oss2.Bucket(self.auth, self.endpoint, bucket_name)
        result = bucket.create_bucket(acl)
        return {"status": result.status, "headers": result.headers}

    def list_buckets(self) -> List[Dict[str, Any]]:
        """
        列出当前账号下的 bucket（仅返回简单信息列表）。
        """
        service = oss2.Service(self.auth, self.endpoint)
        result = service.list_buckets()
        return [{"name": b.name, "location": b.location, "creation_date": b.creation_date} for b in result.iterator]

    def delete_bucket(self, bucket_name: str) -> Dict[str, Any]:
        """
        删除 bucket（注意 bucket 必须为空）。
        """
        bucket = oss2.Bucket(self.auth, self.endpoint, bucket_name)
        result = bucket.delete_bucket()
        return {"status": result.status, "headers": result.headers}

    def upload_object(
        self,
        object_name: str,
        data: Union[str, bytes, io.BytesIO, io.BufferedReader],
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
        use_multipart_threshold: int = 5 * 1024 * 1024,
    ) -> Dict[str, Any]:
        """
        上传对象。data 可为本地文件路径（str），bytes，或者类文件对象。
        根据大小自动选择 put_object 或 multipart 上传（基于 threshold）。
        返回响应信息。
        """
        if not self.bucket:
            raise RuntimeError("Bucket not connected. Call connect(bucket_name) first.")

        options = {}
        if content_type:
            options['content_type'] = content_type
        if metadata:
            options['headers'] = {**(headers or {}), **{f'x-oss-meta-{k}': v for k, v in metadata.items()}}
        elif headers:
            options['headers'] = headers

        # 本地文件路径
        if isinstance(data, str) and os.path.isfile(data):
            size = os.path.getsize(data)
            if size >= use_multipart_threshold:
                # 分片上传
                result = oss2.resumable_upload(self.bucket, object_name, data, headers=options.get('headers'), multipart_threshold=use_multipart_threshold)
                return {"status": 200, "result": result}
            else:
                result = self.bucket.put_object_from_file(object_name, data, headers=options.get('headers'))
                return {"status": result.status, "headers": result.headers}
        # bytes
        if isinstance(data, (bytes, bytearray)):
            result = self.bucket.put_object(object_name, data, headers=options.get('headers'))
            return {"status": result.status, "headers": result.headers}
        # file-like
        if hasattr(data, "read"):
            result = self.bucket.put_object(object_name, data, headers=options.get('headers'))
            return {"status": result.status, "headers": result.headers}

        raise TypeError("data must be file path, bytes, or file-like object")

    def get_object(self, object_name: str, dest_path: Optional[str] = None) -> Union[bytes, Dict[str, Any]]:
        """
        获取对象内容。若提供 dest_path 则保存到本地并返回保存信息，否则返回 bytes。
        """
        if not self.bucket:
            raise RuntimeError("Bucket not connected. Call connect(bucket_name) first.")

        if dest_path:
            result = self.bucket.get_object_to_file(object_name, dest_path)
            return {"status": result.status, "headers": result.headers, "path": dest_path}
        else:
            obj = self.bucket.get_object(object_name)
            data = obj.read()
            obj.close()
            return data

    def list_objects(self, prefix: Optional[str] = None, delimiter: Optional[str] = None, max_keys: Optional[int] = None) -> Iterable[Dict[str, Any]]:
        """
        列举对象（生成器）。每一项包含 key, size, etag, last_modified 等。
        """
        if not self.bucket:
            raise RuntimeError("Bucket not connected. Call connect(bucket_name) first.")
        for obj in oss2.ObjectIterator(self.bucket, prefix=prefix, delimiter=delimiter, max_keys=max_keys):
            yield {
                "key": obj.key,
                "size": obj.size,
                "etag": obj.etag,
                "last_modified": obj.last_modified,
                "storage_class": obj.storage_class,
            }

    def delete_object(self, object_name: str) -> Dict[str, Any]:
        """
        删除单个对象。
        """
        if not self.bucket:
            raise RuntimeError("Bucket not connected. Call connect(bucket_name) first.")
        result = self.bucket.delete_object(object_name)
        return {"status": result.status, "headers": result.headers}

    def rename_object(self, src_object_name: str, dest_object_name: str, src_bucket_name: Optional[str] = None, dest_bucket_name: Optional[str] = None) -> Dict[str, Any]:
        """
        重命名对象（实际为拷贝后删除原对象）。
        支持跨 bucket（若提供 src_bucket_name/dest_bucket_name）。
        返回拷贝和删除的结果简要信息。
        """
        if not self.bucket and (not src_bucket_name or not dest_bucket_name):
            raise RuntimeError("Bucket not connected. Connect to a bucket or provide src_bucket_name and dest_bucket_name.")

        src_bucket_name = src_bucket_name or self.bucket.bucket_name  # type: ignore
        dest_bucket_name = dest_bucket_name or self.bucket.bucket_name  # type: ignore

        src_bucket = oss2.Bucket(self.auth, self.endpoint, src_bucket_name)
        dest_bucket = oss2.Bucket(self.auth, self.endpoint, dest_bucket_name)

        # copy
        copy_source = oss2.ObjectInfo(src_bucket_name, src_object_name) if hasattr(oss2, 'ObjectInfo') else f"/{src_bucket_name}/{src_object_name}"
        # 使用 copy_object API：目标 bucket 的 copy_object 接受源 (bucket, key) 形式
        result_copy = dest_bucket.copy_object(src_bucket_name, src_object_name, dest_object_name)
        # 删除原对象
        result_delete = src_bucket.delete_object(src_object_name)
        return {
            "copy_status": result_copy.status,
            "copy_headers": result_copy.headers,
            "delete_status": result_delete.status,
            "delete_headers": result_delete.headers,
        }

    def generate_object_url(self, object_name: str, expires: int = 3600, is_private: bool = True, method: str = "GET") -> str:
        """
        生成对象访问 URL。
        - 如果 is_private 为 True，会生成签名 URL（expires 秒后过期）。
        - 否则返回公开访问的 URL（使用 Bucket.object_url）。
        method 可选 "GET"/"PUT" 等（签名时用）。
        """
        if not self.bucket:
            raise RuntimeError("Bucket not connected. Call connect(bucket_name) first.")
        if is_private:
            return self.bucket.sign_url(method, object_name, expires)
        else:
            return self.bucket.object_url(object_name)

    def object_exists(self, object_name: str) -> bool:
        """
        判断对象是否存在。
        """
        if not self.bucket:
            raise RuntimeError("Bucket not connected. Call connect(bucket_name) first.")
        return self.bucket.object_exists(object_name)