"""
Pydantic Schemas
用于请求验证和响应序列化
"""

from typing import List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field


# ============ 通用响应模型 ============

class ResponseModel(BaseModel):
    """统一响应格式"""
    code: int = 200
    message: str = "success"
    data: Optional[Any] = None


# ============ 用户相关 ============

class WeChatLoginRequest(BaseModel):
    """微信登录请求"""
    code: str = Field(..., description="微信登录凭证")
    nickname: Optional[str] = Field(None, description="用户昵称")
    avatar: Optional[str] = Field(None, description="头像URL")


class UserResponse(BaseModel):
    """用户信息响应"""
    id: str
    nickname: Optional[str]
    avatar: Optional[str]
    subscription_tier: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    """登录响应"""
    token: str
    user_id: str
    is_new_user: bool


# ============ 闪记相关 ============

class FlashCreate(BaseModel):
    """创建闪记请求"""
    title: Optional[str] = None
    content: str = Field(..., min_length=1, description="转写文字内容")
    summary: Optional[str] = None
    keywords: Optional[List[str]] = None
    category: Optional[str] = None
    audio_url: Optional[str] = None
    audio_duration: Optional[int] = None


class FlashUpdate(BaseModel):
    """更新闪记请求"""
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    keywords: Optional[List[str]] = None
    category: Optional[str] = None
    is_favorite: Optional[bool] = None


class FlashResponse(BaseModel):
    """闪记响应"""
    id: str
    title: Optional[str]
    content: str
    summary: Optional[str]
    keywords: Optional[List[str]]
    category: Optional[str]
    audio_url: Optional[str]
    audio_duration: Optional[int]
    is_favorite: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm(cls, obj):
        """从 ORM 对象转换，处理 JSON 字段"""
        import json
        data = {
            "id": obj.id,
            "title": obj.title,
            "content": obj.content,
            "summary": obj.summary,
            "keywords": json.loads(obj.keywords) if obj.keywords else None,
            "category": obj.category,
            "audio_url": obj.audio_url,
            "audio_duration": obj.audio_duration,
            "is_favorite": obj.is_favorite,
            "created_at": obj.created_at,
            "updated_at": obj.updated_at
        }
        return cls(**data)


class FlashListResponse(BaseModel):
    """闪记列表响应"""
    total: int
    page: int
    page_size: int
    items: List[FlashResponse]


# ============ 会议纪要相关 ============

class MeetingCreate(BaseModel):
    """创建会议纪要请求"""
    title: str = Field(..., min_length=1, description="会议主题")
    participants: Optional[List[str]] = None
    meeting_date: Optional[datetime] = None
    audio_url: str = Field(..., description="音频文件URL")
    audio_duration: Optional[int] = None


class MeetingUpdate(BaseModel):
    """更新会议纪要请求"""
    title: Optional[str] = None
    participants: Optional[List[str]] = None
    meeting_date: Optional[datetime] = None
    summary: Optional[str] = None


class MeetingResponse(BaseModel):
    """会议纪要响应"""
    id: str
    title: str
    participants: Optional[List[str]]
    meeting_date: Optional[datetime]
    audio_url: str
    audio_duration: Optional[int]
    transcript: Optional[str]
    summary: Optional[str]  # 段落摘要
    conversational_summary: Optional[str] = None  # 发言总结 ✨新增
    mind_map: Optional[str] = None  # 思维导图 ✨新增
    key_points: Optional[List[dict]]
    action_items: Optional[List[dict]]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm(cls, obj):
        """从 ORM 对象转换，处理 JSON 字段"""
        import json
        data = {
            "id": obj.id,
            "title": obj.title,
            "participants": json.loads(obj.participants) if obj.participants else None,
            "meeting_date": obj.meeting_date,
            "audio_url": obj.audio_url,
            "audio_duration": obj.audio_duration,
            "transcript": obj.transcript,
            "summary": obj.summary,
            "conversational_summary": obj.conversational_summary if hasattr(obj, 'conversational_summary') else None,
            "mind_map": obj.mind_map if hasattr(obj, 'mind_map') else None,
            "key_points": json.loads(obj.key_points) if obj.key_points else None,
            "action_items": json.loads(obj.action_items) if obj.action_items else None,
            "status": obj.status.value if hasattr(obj.status, 'value') else obj.status,
            "created_at": obj.created_at
        }
        return cls(**data)


class MeetingListResponse(BaseModel):
    """会议列表响应"""
    total: int
    page: int
    page_size: int
    items: List[MeetingResponse]


class MeetingStatusResponse(BaseModel):
    """会议处理状态响应"""
    meeting_id: str
    status: str
    progress: Optional[int] = None
    message: Optional[str] = None
    error: Optional[str] = None


# ============ 搜索相关 ============

class SearchRequest(BaseModel):
    """搜索请求"""
    q: str = Field(..., min_length=1, description="搜索关键词")
    type: str = Field(default="all", description="搜索类型：flash/meeting/all")
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class SearchResultItem(BaseModel):
    """搜索结果项"""
    id: str
    type: str  # flash / meeting
    title: str
    highlight: str
    score: float
    created_at: datetime


class SearchResponse(BaseModel):
    """搜索响应"""
    results: List[SearchResultItem]
    total: int


# ============ 文件上传相关 ============

class UploadResponse(BaseModel):
    """文件上传响应"""
    file_url: str
    file_size: int
    duration: Optional[int] = None
    task_id: Optional[str] = None


# ============ 统计相关 ============

class StatsResponse(BaseModel):
    """统计数据响应"""
    today: dict
    week: dict
    month: dict
    category_distribution: List[dict]

