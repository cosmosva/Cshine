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
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 用于语义搜索的向量字段（V2.0）
    # embedding = Column(Vector(1536), nullable=True)
    
    # 关系
    user = relationship("User", back_populates="flashes")
    flash_tags = relationship("FlashTag", back_populates="flash", cascade="all, delete-orphan")


class Meeting(Base):
    """会议纪要表"""
    __tablename__ = "meetings"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    participants = Column(Text, nullable=True)  # 存储为 JSON 字符串
    meeting_date = Column(DateTime, nullable=True)
    audio_url = Column(Text, nullable=True)
    audio_duration = Column(Integer, nullable=True)  # 秒
    transcript = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)  # 段落摘要
    conversational_summary = Column(Text, nullable=True)  # 发言总结 ✨新增
    mind_map = Column(Text, nullable=True)  # 思维导图 ✨新增
    key_points = Column(Text, nullable=True)  # 存储为 JSON 字符串
    action_items = Column(Text, nullable=True)  # 存储为 JSON 字符串
    is_favorite = Column(Boolean, default=False, nullable=False)  # 收藏状态 ✨新增
    tags = Column(Text, nullable=True)  # AI生成的标签，存储为JSON字符串 ✨新增
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(SQLEnum(MeetingStatus), default=MeetingStatus.PENDING, nullable=False)
    
    # 关系
    user = relationship("User", back_populates="meetings")


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

