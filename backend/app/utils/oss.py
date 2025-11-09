"""
阿里云 OSS 存储工具
用于上传、删除音频文件
"""

import os
import uuid
import oss2
import json
import base64
import hmac
import hashlib
from datetime import datetime, timedelta
from loguru import logger
from config import settings


# 初始化 OSS 客户端（使用已有的阿里云凭证）
def get_oss_bucket():
    """获取 OSS Bucket 实例"""
    # 使用已配置的阿里云 AccessKey（与通义听悟共用）
    auth = oss2.Auth(
        settings.ALIBABA_CLOUD_ACCESS_KEY_ID,
        settings.ALIBABA_CLOUD_ACCESS_KEY_SECRET
    )
    
    bucket = oss2.Bucket(
        auth,
        settings.OSS_ENDPOINT,
        settings.OSS_BUCKET_NAME
    )
    
    return bucket


def upload_audio_to_oss(local_file_path: str, user_id: str, file_extension: str = ".wav") -> str:
    """
    上传音频文件到 OSS
    
    Args:
        local_file_path: 本地文件路径
        user_id: 用户ID（用于组织文件目录）
        file_extension: 文件扩展名
        
    Returns:
        公开访问的 OSS URL
        
    Raises:
        Exception: 上传失败时抛出异常
    """
    try:
        bucket = get_oss_bucket()
        
        # 1. 生成唯一文件名（按用户ID组织目录）
        unique_id = str(uuid.uuid4())
        object_name = f"audio/{user_id}/{unique_id}{file_extension}"
        
        # 2. 上传到 OSS
        logger.info(f"开始上传文件到 OSS: {object_name}")
        result = bucket.put_object_from_file(object_name, local_file_path)
        
        # 3. 检查上传结果
        if result.status == 200:
            oss_url = f"{settings.oss_base_url}/{object_name}"
            logger.success(f"✅ 文件上传成功: {oss_url}")
            return oss_url
        else:
            raise Exception(f"OSS 上传失败，状态码: {result.status}")
            
    except Exception as e:
        logger.error(f"❌ OSS 上传失败: {e}")
        raise


def delete_audio_from_oss(oss_url: str) -> bool:
    """
    从 OSS 删除音频文件
    
    Args:
        oss_url: OSS 文件 URL
        
    Returns:
        是否删除成功
    """
    try:
        bucket = get_oss_bucket()
        
        # 1. 从 URL 提取 object_name
        object_name = oss_url.replace(f"{settings.oss_base_url}/", "")
        
        # 2. 删除文件
        logger.info(f"删除 OSS 文件: {object_name}")
        bucket.delete_object(object_name)
        
        logger.success(f"✅ 文件删除成功: {object_name}")
        return True
    except Exception as e:
        logger.error(f"❌ OSS 删除失败: {e}")
        return False


def check_oss_connection() -> bool:
    """
    检查 OSS 连接是否正常
    
    Returns:
        是否连接成功
    """
    try:
        # 检查配置是否完整
        if not settings.ALIBABA_CLOUD_ACCESS_KEY_ID or not settings.ALIBABA_CLOUD_ACCESS_KEY_SECRET:
            logger.warning("⚠️  阿里云 AccessKey 未配置")
            return False
            
        if not settings.OSS_BUCKET_NAME or not settings.OSS_ENDPOINT:
            logger.warning("⚠️  OSS Bucket 或 Endpoint 未配置")
            return False
        
        bucket = get_oss_bucket()
        
        # 列举 Bucket 中的文件（最多 1 个，仅用于测试连接）
        result = bucket.list_objects(max_keys=1)
        
        logger.success(f"✅ OSS 连接成功: {settings.OSS_BUCKET_NAME}")
        return True
    except Exception as e:
        logger.error(f"❌ OSS 连接失败: {e}")
        return False


def get_signed_url(oss_url: str, expires: int = 3600) -> str:
    """
    生成签名 URL（适用于私有 Bucket）
    
    Args:
        oss_url: OSS 文件 URL
        expires: 过期时间（秒），默认 1 小时
        
    Returns:
        签名后的 URL
    """
    try:
        bucket = get_oss_bucket()
        
        # 从 URL 提取 object_name
        object_name = oss_url.replace(f"{settings.oss_base_url}/", "")
        
        # 生成签名 URL
        signed_url = bucket.sign_url('GET', object_name, expires)
        
        return signed_url
    except Exception as e:
        logger.error(f"❌ 生成签名 URL 失败: {e}")
        return oss_url  # 降级：返回原始 URL


def generate_oss_upload_signature(user_id: str, expires_in: int = 3600) -> dict:
    """
    生成 OSS 上传签名（用于前端直传）
    
    Args:
        user_id: 用户ID
        expires_in: 签名有效期（秒），默认 1 小时
        
    Returns:
        包含签名信息的字典
    """
    try:
        # 1. 生成文件路径
        unique_id = str(uuid.uuid4())
        object_key = f"audio/{user_id}/{unique_id}.m4a"
        
        # 2. 生成过期时间
        expire_time = datetime.utcnow() + timedelta(seconds=expires_in)
        expire_timestamp = int(expire_time.timestamp())
        
        # 3. 构建 Policy
        policy_dict = {
            "expiration": expire_time.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "conditions": [
                ["content-length-range", 0, 500 * 1024 * 1024],  # 最大 500MB
                ["starts-with", "$key", f"audio/{user_id}/"]
            ]
        }
        
        # 4. Base64 编码 Policy
        policy_str = json.dumps(policy_dict)
        policy_base64 = base64.b64encode(policy_str.encode('utf-8')).decode('utf-8')
        
        # 5. 生成签名
        signature = base64.b64encode(
            hmac.new(
                settings.ALIBABA_CLOUD_ACCESS_KEY_SECRET.encode('utf-8'),
                policy_base64.encode('utf-8'),
                hashlib.sha1
            ).digest()
        ).decode('utf-8')
        
        # 6. 构建返回数据
        return {
            "accessid": settings.ALIBABA_CLOUD_ACCESS_KEY_ID,
            "host": f"https://{settings.OSS_BUCKET_NAME}.{settings.OSS_ENDPOINT}",
            "policy": policy_base64,
            "signature": signature,
            "expire": expire_timestamp,
            "key": object_key,
            "success_action_status": "200"
        }
        
    except Exception as e:
        logger.error(f"❌ 生成 OSS 签名失败: {e}")
        raise


