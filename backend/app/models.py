"""
数据库模型定义
基于 PRD 第6章数据模型设计
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base
import enum


def generate_uuid():
    """生成 UUID"""
    return str(uuid.uuid4())


class SubscriptionTier(str, enum.Enum):
    """订阅等级"""
    FREE = "free"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class MeetingStatus(str, enum.Enum):
    """会议处理状态"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AIProvider(str, enum.Enum):
    """AI 模型提供商"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    DOUBAO = "doubao"
    QWEN = "qwen"


class PromptScenario(str, enum.Enum):
    """提示词使用场景"""
    meeting_summary = "meeting_summary"
    flash_classify = "flash_classify"
    action_extract = "action_extract"
    key_points = "key_points"
    general_chat = "general_chat"


class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    openid = Column(String(100), unique=True, nullable=False, index=True)
    unionid = Column(String(100), unique=True, nullable=True)
    nickname = Column(String(50), nullable=True)
    avatar = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    subscription_tier = Column(SQLEnum(SubscriptionTier), default=SubscriptionTier.FREE)
    
    # 关系
    flashes = relationship("Flash", back_populates="user", cascade="all, delete-orphan")
    meetings = relationship("Meeting", back_populates="user", cascade="all, delete-orphan")
    tags = relationship("Tag", back_populates="user", cascade="all, delete-orphan")
    folders = relationship("Folder", back_populates="user", cascade="all, delete-orphan")
    contacts = relationship("Contact", back_populates="user", cascade="all, delete-orphan")


class Flash(Base):
    """闪记记录表"""
    __tablename__ = "flashes"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(100), nullable=True)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    keywords = Column(Text, nullable=True)  # 存储为 JSON 字符串
    category = Column(String(20), nullable=True)
    audio_url = Column(Text, nullable=True)
    audio_duration = Column(Integer, nullable=True)  # 秒
    is_favorite = Column(Boolean, default=False, nullable=False)
    
    # AI 处理状态
    ai_status = Column(String(20), default='pending', nullable=False)  # pending/processing/completed/failed
    ai_task_id = Column(String(100), nullable=True)  # 通义听悟任务ID
    ai_error = Column(Text, nullable=True)  # 错误信息
    ai_model_id = Column(String(36), ForeignKey("ai_models.id", ondelete="SET NULL"), nullable=True)  # 使用的AI模型 ✨新增
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 用于语义搜索的向量字段（V2.0）
    # embedding = Column(Vector(1536), nullable=True)
    
    # 关系
    user = relationship("User", back_populates="flashes")
    flash_tags = relationship("FlashTag", back_populates="flash", cascade="all, delete-orphan")
    ai_model = relationship("AIModel", foreign_keys=[ai_model_id])


class Meeting(Base):
    """会议纪要表"""
    __tablename__ = "meetings"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    folder_id = Column(Integer, ForeignKey("folders.id", ondelete="SET NULL"), nullable=True)  # 知识库ID ✨新增
    title = Column(String(200), nullable=False)
    participants = Column(Text, nullable=True)  # 存储为 JSON 字符串
    meeting_date = Column(DateTime, nullable=True)
    audio_url = Column(Text, nullable=True)
    audio_duration = Column(Integer, nullable=True)  # 秒
    transcript = Column(Text, nullable=True)  # 通义听悟转录文本
    transcript_paragraphs = Column(Text, nullable=True)  # 段落级转录数据（JSON格式，含说话人）
    summary = Column(Text, nullable=True)  # LLM生成的会议摘要
    mind_map = Column(Text, nullable=True)  # LLM生成的思维导图（Markdown格式）
    key_points = Column(Text, nullable=True)  # LLM提取的关键要点（JSON格式）
    action_items = Column(Text, nullable=True)  # LLM提取的行动项（JSON格式）
    is_favorite = Column(Boolean, default=False, nullable=False)  # 收藏状态 ✨新增
    tags = Column(Text, nullable=True)  # AI生成的标签，存储为JSON字符串 ✨新增
    ai_model_id = Column(String(36), ForeignKey("ai_models.id", ondelete="SET NULL"), nullable=True)  # 使用的AI模型 ✨新增
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(SQLEnum(MeetingStatus), default=MeetingStatus.PENDING, nullable=False)
    
    # 关系
    user = relationship("User", back_populates="meetings")
    folder = relationship("Folder", back_populates="meetings")
    speakers = relationship("MeetingSpeaker", back_populates="meeting", cascade="all, delete-orphan")
    ai_model = relationship("AIModel", foreign_keys=[ai_model_id])


class Tag(Base):
    """标签表"""
    __tablename__ = "tags"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(20), nullable=False)
    color = Column(String(7), nullable=True)  # HEX 颜色
    usage_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="tags")
    flash_tags = relationship("FlashTag", back_populates="tag", cascade="all, delete-orphan")


class FlashTag(Base):
    """闪记-标签关联表"""
    __tablename__ = "flash_tags"
    
    flash_id = Column(String(36), ForeignKey("flashes.id", ondelete="CASCADE"), primary_key=True)
    tag_id = Column(String(36), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    flash = relationship("Flash", back_populates="flash_tags")
    tag = relationship("Tag", back_populates="flash_tags")


class Folder(Base):
    """知识库（文件夹）表 ✨新增"""
    __tablename__ = "folders"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="folders")
    meetings = relationship("Meeting", back_populates="folder", cascade="all, delete-orphan")


class Contact(Base):
    """常用联系人表 ✨新增"""
    __tablename__ = "contacts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(50), nullable=False)
    position = Column(String(50), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    avatar = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 关系
    user = relationship("User", back_populates="contacts")
    meeting_speakers = relationship("MeetingSpeaker", back_populates="contact")


class MeetingSpeaker(Base):
    """会议说话人映射表 ✨新增"""
    __tablename__ = "meeting_speakers"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    meeting_id = Column(String(36), ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False, index=True)
    speaker_id = Column(String(20), nullable=False)  # "说话人1", "说话人2" 等
    contact_id = Column(Integer, ForeignKey("contacts.id", ondelete="SET NULL"), nullable=True, index=True)
    custom_name = Column(String(50), nullable=True)  # 自定义名称（不关联联系人时使用）
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 关系
    meeting = relationship("Meeting", back_populates="speakers")
    contact = relationship("Contact", back_populates="meeting_speakers")


class AIModel(Base):
    """AI模型配置表 ✨新增"""
    __tablename__ = "ai_models"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)  # 模型显示名称，如 "GPT-4"、"豆包-32K"
    provider = Column(SQLEnum(AIProvider), nullable=False)  # 提供商
    model_id = Column(String(100), nullable=False)  # API调用的模型标识符
    api_key = Column(Text, nullable=False)  # API密钥（需加密存储）
    api_base_url = Column(String(255), nullable=True)  # API基础URL
    max_tokens = Column(Integer, default=4096, nullable=False)  # 最大token数
    temperature = Column(Integer, default=70, nullable=False)  # 温度参数 * 100（0-100，实际使用时/100）
    is_active = Column(Boolean, default=True, nullable=False)  # 是否启用
    is_default = Column(Boolean, default=False, nullable=False)  # 是否为默认模型
    description = Column(Text, nullable=True)  # 模型描述
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AIPrompt(Base):
    """AI提示词模板表 ✨新增"""
    __tablename__ = "ai_prompts"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)  # 模板名称
    scenario = Column(SQLEnum(PromptScenario), nullable=False)  # 使用场景
    prompt_template = Column(Text, nullable=False)  # 提示词模板（支持变量占位符）
    variables = Column(Text, nullable=True)  # 变量说明（JSON格式）
    is_active = Column(Boolean, default=True, nullable=False)  # 是否启用
    is_default = Column(Boolean, default=False, nullable=False)  # 是否为默认模板
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AdminUser(Base):
    """管理员用户表 ✨新增"""
    __tablename__ = "admin_users"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)  # bcrypt加密
    email = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)  # 超级管理员
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)


