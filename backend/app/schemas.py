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
    ai_model_id: Optional[str] = Field(None, description="使用的AI模型ID（可选，不传则使用默认模型）")


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
    folder_id: Optional[int] = None  # 知识库ID


class MeetingUpdate(BaseModel):
    """更新会议纪要请求"""
    title: Optional[str] = None
    participants: Optional[List[str]] = None
    meeting_date: Optional[datetime] = None
    summary: Optional[str] = None
    folder_id: Optional[int] = None  # 知识库ID


class MeetingResponse(BaseModel):
    """会议纪要响应"""
    id: str
    title: str
    participants: Optional[List[str]]
    meeting_date: Optional[datetime]
    audio_url: str
    audio_duration: Optional[int]
    transcript: Optional[str]  # 通义听悟转录文本
    transcript_paragraphs: Optional[List[dict]] = None  # 段落级转录（含说话人）
    summary: Optional[str]  # LLM生成的会议摘要
    mind_map: Optional[str] = None  # LLM生成的思维导图（Markdown）
    key_points: Optional[List[dict]]  # LLM提取的关键要点
    action_items: Optional[List[dict]]  # LLM提取的行动项
    is_favorite: Optional[bool] = False  # 收藏状态
    is_viewed: Optional[bool] = False  # 已查看状态 (v0.9.10新增)
    tags: Optional[List[str]] = None  # LLM生成的标签
    folder_id: Optional[int] = None  # 知识库ID
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
            "transcript_paragraphs": json.loads(obj.transcript_paragraphs) if (hasattr(obj, 'transcript_paragraphs') and obj.transcript_paragraphs) else None,
            "summary": obj.summary,
            "mind_map": obj.mind_map if hasattr(obj, 'mind_map') else None,
            "key_points": json.loads(obj.key_points) if obj.key_points else None,
            "action_items": json.loads(obj.action_items) if obj.action_items else None,
            "is_favorite": obj.is_favorite if hasattr(obj, 'is_favorite') else False,
            "is_viewed": obj.is_viewed if hasattr(obj, 'is_viewed') else False,
            "tags": json.loads(obj.tags) if (hasattr(obj, 'tags') and obj.tags) else None,
            "folder_id": obj.folder_id if hasattr(obj, 'folder_id') else None,
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


class GenerateSummaryRequest(BaseModel):
    """生成会议总结请求"""
    ai_model_id: str = Field(..., description="使用的AI模型ID")


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


# ============ 知识库（文件夹）相关 ✨新增 ============

class FolderCreate(BaseModel):
    """创建知识库请求"""
    name: str = Field(..., min_length=1, max_length=50, description="知识库名称")


class FolderUpdate(BaseModel):
    """更新知识库请求"""
    name: str = Field(..., min_length=1, max_length=50, description="知识库名称")


class FolderResponse(BaseModel):
    """知识库响应"""
    id: int
    name: str
    count: int = 0  # 该知识库中的会议数量
    created_at: datetime
    
    class Config:
        from_attributes = True


class FolderListResponse(BaseModel):
    """知识库列表响应"""
    items: List[FolderResponse]


# ============ 联系人相关 ✨新增 ============

class ContactCreate(BaseModel):
    """创建联系人请求"""
    name: str = Field(..., min_length=1, max_length=50, description="联系人姓名")
    position: Optional[str] = Field(None, max_length=50, description="职位")
    phone: Optional[str] = Field(None, max_length=20, description="电话")
    email: Optional[str] = Field(None, max_length=100, description="邮箱")
    avatar: Optional[str] = Field(None, max_length=255, description="头像URL")


class ContactUpdate(BaseModel):
    """更新联系人请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="联系人姓名")
    position: Optional[str] = Field(None, max_length=50, description="职位")
    phone: Optional[str] = Field(None, max_length=20, description="电话")
    email: Optional[str] = Field(None, max_length=100, description="邮箱")
    avatar: Optional[str] = Field(None, max_length=255, description="头像URL")


class ContactResponse(BaseModel):
    """联系人响应"""
    id: int
    name: str
    position: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    avatar: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ContactListResponse(BaseModel):
    """联系人列表响应"""
    total: int
    items: List[ContactResponse]


# ============ 说话人映射相关 ✨新增 ============

class SpeakerMapRequest(BaseModel):
    """说话人映射请求"""
    speaker_id: str = Field(..., description="说话人ID（如：说话人1）")
    contact_id: Optional[int] = Field(None, description="关联的联系人ID")
    custom_name: Optional[str] = Field(None, max_length=50, description="自定义名称")


class SpeakerResponse(BaseModel):
    """说话人响应"""
    speaker_id: str
    display_name: str  # 显示名称（联系人名称或自定义名称）
    contact_id: Optional[int]
    contact: Optional[ContactResponse]  # 关联的联系人信息
    
    class Config:
        from_attributes = True


class SpeakerListResponse(BaseModel):
    """说话人列表响应"""
    items: List[SpeakerResponse]


# ============ 管理员相关 ✨新增 ============

class AdminLoginRequest(BaseModel):
    """管理员登录请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, description="密码")


class AdminLoginResponse(BaseModel):
    """管理员登录响应"""
    token: str
    admin_id: str
    username: str
    is_superuser: bool


class AdminUserResponse(BaseModel):
    """管理员用户响应"""
    id: str
    username: str
    email: Optional[str]
    is_active: bool
    is_superuser: bool
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True


# ============ AI 模型相关 ✨新增 ============

class AIModelCreate(BaseModel):
    """创建 AI 模型请求"""
    name: str = Field(..., min_length=1, max_length=100, description="模型名称")
    provider: str = Field(..., description="提供商：openai/anthropic/doubao/qwen")
    model_id: str = Field(..., min_length=1, max_length=100, description="模型ID")
    api_key: str = Field(..., description="API密钥")
    api_base_url: Optional[str] = Field(None, max_length=255, description="API基础URL")
    max_tokens: int = Field(4096, ge=1, le=128000, description="最大token数")
    temperature: int = Field(70, ge=0, le=100, description="温度参数(0-100)")
    is_active: bool = Field(True, description="是否启用")
    is_default: bool = Field(False, description="是否为默认模型")
    description: Optional[str] = Field(None, description="模型描述")


class AIModelUpdate(BaseModel):
    """更新 AI 模型请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    model_id: Optional[str] = Field(None, min_length=1, max_length=100)
    api_key: Optional[str] = None
    api_base_url: Optional[str] = Field(None, max_length=255)
    max_tokens: Optional[int] = Field(None, ge=1, le=128000)
    temperature: Optional[int] = Field(None, ge=0, le=100)
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None
    description: Optional[str] = None


class AIModelResponse(BaseModel):
    """AI 模型响应"""
    id: str
    name: str
    provider: str
    model_id: str
    api_base_url: Optional[str]
    max_tokens: int
    temperature: int
    is_active: bool
    is_default: bool
    description: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class AIModelListResponse(BaseModel):
    """AI 模型列表响应"""
    total: int
    items: List[AIModelResponse]


class AIModelTestRequest(BaseModel):
    """测试 AI 模型连接请求"""
    model_id: Optional[str] = Field(None, description="模型ID，如果不传则测试指定配置")
    provider: Optional[str] = None
    api_key: Optional[str] = None
    api_base_url: Optional[str] = None


# ============ AI 提示词相关 ✨新增 ============

class AIPromptCreate(BaseModel):
    """创建提示词模板请求"""
    name: str = Field(..., min_length=1, max_length=100, description="模板名称")
    scenario: str = Field(..., description="使用场景")
    prompt_template: str = Field(..., min_length=1, description="提示词模板")
    variables: Optional[str] = Field(None, description="变量说明（JSON格式）")
    is_active: bool = Field(True, description="是否启用")
    is_default: bool = Field(False, description="是否为默认模板")


class AIPromptUpdate(BaseModel):
    """更新提示词模板请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    prompt_template: Optional[str] = Field(None, min_length=1)
    variables: Optional[str] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None


class AIPromptResponse(BaseModel):
    """提示词模板响应"""
    id: str
    name: str
    scenario: str
    prompt_template: str
    variables: Optional[str]
    is_active: bool
    is_default: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class AIPromptListResponse(BaseModel):
    """提示词模板列表响应"""
    total: int
    items: List[AIPromptResponse]


# ============ AI 聊天相关 ✨新增 ============

class AIChatRequest(BaseModel):
    """AI 对话请求"""
    message: str = Field(..., min_length=1, description="用户消息")
    model_id: Optional[str] = Field(None, description="使用的模型ID，不传则使用默认模型")
    system_prompt: Optional[str] = Field(None, description="系统提示词")
    temperature: Optional[int] = Field(None, ge=0, le=100, description="温度参数(0-100)")
    max_tokens: Optional[int] = Field(None, ge=1, description="最大token数")


class AIChatResponse(BaseModel):
    """AI 对话响应"""
    message: str
    model: str
    usage: Optional[dict] = None


