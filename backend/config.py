"""
配置管理
使用 pydantic-settings 管理环境变量
"""

from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用基础配置
    APP_NAME: str = "Cshine API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 数据库配置
    DATABASE_URL: str = Field(
        default="sqlite:///./cshine.db",
        description="数据库连接字符串"
    )
    
    # JWT 配置
    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        description="JWT 密钥"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7天
    
    # 微信小程序配置
    # ⚠️ 必须配置！从微信公众平台获取：https://mp.weixin.qq.com/
    # 开发 → 开发管理 → 开发设置
    WECHAT_APPID: str = Field(
        default="",
        description="微信小程序 AppID（必填）"
    )
    WECHAT_SECRET: str = Field(
        default="",
        description="微信小程序 AppSecret（必填）"
    )
    
    # Redis 配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""
    
    # 文件存储配置
    STORAGE_TYPE: str = "local"  # local / oss
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 500 * 1024 * 1024  # 500MB
    
    # 阿里云 OSS 配置
    OSS_ACCESS_KEY_ID: str = ""
    OSS_ACCESS_KEY_SECRET: str = ""
    OSS_ENDPOINT: str = "oss-cn-guangzhou.aliyuncs.com"  # 华南3（广州）
    OSS_BUCKET_NAME: str = "cshine-audio"
    
    @property
    def oss_base_url(self) -> str:
        """OSS 公开访问基础 URL"""
        if self.OSS_BUCKET_NAME and self.OSS_ENDPOINT:
            return f"https://{self.OSS_BUCKET_NAME}.{self.OSS_ENDPOINT}"
        return ""
    
    # AI 服务配置 - 阿里云通义听悟
    TINGWU_APP_KEY: str = ""  # 通义听悟 AppKey
    ALIBABA_CLOUD_ACCESS_KEY_ID: str = ""  # 阿里云 AccessKey ID
    ALIBABA_CLOUD_ACCESS_KEY_SECRET: str = ""  # 阿里云 AccessKey Secret
    
    # 旧配置（保留备用）
    ASR_PROVIDER: str = "tingwu"  # tingwu / xunfei / tencent / aliyun
    XUNFEI_APP_ID: str = ""
    XUNFEI_API_KEY: str = ""
    XUNFEI_API_SECRET: str = ""
    
    LLM_PROVIDER: str = "qwen"  # openai / qwen
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    
    QWEN_API_KEY: str = ""
    QWEN_MODEL: str = "qwen-turbo"
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/cshine.log"
    
    # CORS 配置
    CORS_ORIGINS: str = "*"  # 允许所有来源（开发环境）
    
    @property
    def cors_origins_list(self) -> List[str]:
        """解析 CORS 域名列表"""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # 忽略额外的环境变量


# 创建全局配置实例
settings = Settings()

