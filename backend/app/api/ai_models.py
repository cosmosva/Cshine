"""
AI 模型管理 API
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from loguru import logger
from datetime import datetime

from app.database import get_db
from app.models import AIModel, AdminUser, AIProvider
from app.schemas import (
    AIModelCreate,
    AIModelUpdate,
    AIModelResponse,
    AIModelListResponse,
    AIModelTestRequest,
    AIChatRequest,
    AIChatResponse,
    ResponseModel
)
from app.dependencies import get_current_admin, get_current_user
from app.services.llm import get_llm, test_llm_connection, LLMMessage

# 管理员路由
admin_router = APIRouter(prefix="/api/admin/ai-models", tags=["AI模型管理"])

# 用户路由
user_router = APIRouter(prefix="/api/ai-models", tags=["AI模型"])


# ============ 管理员接口 ============

@admin_router.get("", response_model=ResponseModel)
async def list_ai_models(
    skip: int = 0,
    limit: int = 100,
    provider: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """
    获取 AI 模型列表
    
    - **skip**: 跳过数量
    - **limit**: 限制数量
    - **provider**: 过滤提供商
    - **is_active**: 过滤启用状态
    """
    try:
        query = db.query(AIModel)
        
        # 过滤条件
        if provider:
            query = query.filter(AIModel.provider == provider)
        if is_active is not None:
            query = query.filter(AIModel.is_active == is_active)
        
        # 总数
        total = query.count()
        
        # 查询列表
        models = query.order_by(
            AIModel.is_default.desc(),
            AIModel.created_at.desc()
        ).offset(skip).limit(limit).all()
        
        return ResponseModel(
            code=200,
            message="success",
            data=AIModelListResponse(
                total=total,
                items=[AIModelResponse.from_orm(model) for model in models]
            )
        )
        
    except Exception as e:
        logger.error(f"获取 AI 模型列表失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取列表失败"
        )


@admin_router.post("", response_model=ResponseModel)
async def create_ai_model(
    request: AIModelCreate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """
    创建 AI 模型配置
    """
    try:
        # 验证提供商
        try:
            provider_enum = AIProvider(request.provider)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的提供商: {request.provider}"
            )
        
        # 如果设置为默认模型，取消其他模型的默认状态
        if request.is_default:
            db.query(AIModel).update({"is_default": False})
        
        # 创建模型
        model = AIModel(
            name=request.name,
            provider=provider_enum,
            model_id=request.model_id,
            api_key=request.api_key,  # TODO: 加密存储
            api_base_url=request.api_base_url,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            is_active=request.is_active,
            is_default=request.is_default,
            description=request.description
        )
        
        db.add(model)
        db.commit()
        db.refresh(model)
        
        logger.info(f"创建 AI 模型: {model.name} (ID: {model.id}), 操作人: {admin.username}")
        
        return ResponseModel(
            code=200,
            message="创建成功",
            data=AIModelResponse.from_orm(model)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"创建 AI 模型失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建失败"
        )


@admin_router.get("/{model_id}", response_model=ResponseModel)
async def get_ai_model(
    model_id: str,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """
    获取 AI 模型详情
    """
    model = db.query(AIModel).filter(AIModel.id == model_id).first()
    
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模型不存在"
        )
    
    return ResponseModel(
        code=200,
        message="success",
        data=AIModelResponse.from_orm(model)
    )


@admin_router.put("/{model_id}", response_model=ResponseModel)
async def update_ai_model(
    model_id: str,
    request: AIModelUpdate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """
    更新 AI 模型配置
    """
    try:
        model = db.query(AIModel).filter(AIModel.id == model_id).first()
        
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="模型不存在"
            )
        
        # 如果设置为默认模型，取消其他模型的默认状态
        if request.is_default:
            db.query(AIModel).filter(AIModel.id != model_id).update({"is_default": False})
        
        # 更新字段
        update_data = request.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(model, key, value)
        
        model.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(model)
        
        logger.info(f"更新 AI 模型: {model.name} (ID: {model_id}), 操作人: {admin.username}")
        
        return ResponseModel(
            code=200,
            message="更新成功",
            data=AIModelResponse.from_orm(model)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"更新 AI 模型失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新失败"
        )


@admin_router.delete("/{model_id}", response_model=ResponseModel)
async def delete_ai_model(
    model_id: str,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """
    删除 AI 模型配置
    """
    try:
        model = db.query(AIModel).filter(AIModel.id == model_id).first()
        
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="模型不存在"
            )
        
        # 如果是默认模型，不允许删除
        if model.is_default:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能删除默认模型，请先设置其他模型为默认"
            )
        
        model_name = model.name
        db.delete(model)
        db.commit()
        
        logger.info(f"删除 AI 模型: {model_name} (ID: {model_id}), 操作人: {admin.username}")
        
        return ResponseModel(
            code=200,
            message="删除成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"删除 AI 模型失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除失败"
        )


@admin_router.post("/{model_id}/test", response_model=ResponseModel)
async def test_ai_model(
    model_id: str,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """
    测试 AI 模型连接
    """
    try:
        result = await test_llm_connection(model_id, db)
        
        logger.info(f"测试 AI 模型连接: {model_id}, 结果: {result['success']}, 操作人: {admin.username}")
        
        return ResponseModel(
            code=200 if result["success"] else 400,
            message=result["message"],
            data=result
        )
        
    except Exception as e:
        logger.error(f"测试 AI 模型失败: {e}")
        return ResponseModel(
            code=500,
            message="测试失败",
            data={"success": False, "error": str(e)}
        )


# ============ 用户接口 ============

@user_router.get("", response_model=ResponseModel)
async def get_available_models(
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """
    获取可用的 AI 模型列表（用户端）
    """
    try:
        models = db.query(AIModel).filter(
            AIModel.is_active == True
        ).order_by(
            AIModel.is_default.desc(),
            AIModel.created_at.desc()
        ).all()
        
        # 返回简化的信息（不包含 API Key）
        return ResponseModel(
            code=200,
            message="success",
            data=[
                {
                    "id": model.id,
                    "name": model.name,
                    "provider": model.provider.value,
                    "model_id": model.model_id,
                    "description": model.description,
                    "is_default": model.is_default,
                    "max_tokens": model.max_tokens,
                    "temperature": model.temperature / 100.0,
                }
                for model in models
            ]
        )
        
    except Exception as e:
        logger.error(f"获取可用模型列表失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取列表失败"
        )


@user_router.post("/chat", response_model=ResponseModel)
async def chat_with_ai(
    request: AIChatRequest,
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    """
    与 AI 对话
    
    - **message**: 用户消息
    - **model_id**: 使用的模型ID（可选，不传则使用默认模型）
    - **system_prompt**: 系统提示词（可选）
    - **temperature**: 温度参数（可选）
    - **max_tokens**: 最大token数（可选）
    """
    try:
        # 获取 LLM 实例
        llm = get_llm(model_id=request.model_id, db=db)
        
        # 构建消息
        messages = []
        if request.system_prompt:
            messages.append(LLMMessage(role="system", content=request.system_prompt))
        messages.append(LLMMessage(role="user", content=request.message))
        
        # 调用参数
        kwargs = {}
        if request.temperature is not None:
            kwargs["temperature"] = request.temperature / 100.0
        if request.max_tokens is not None:
            kwargs["max_tokens"] = request.max_tokens
        
        # 调用 LLM
        response = await llm.complete(messages, **kwargs)
        
        logger.info(f"AI 对话成功: user_id={user.id}, model={response.model}, tokens={response.usage}")
        
        return ResponseModel(
            code=200,
            message="success",
            data=AIChatResponse(
                message=response.content,
                model=response.model,
                usage=response.usage
            )
        )
        
    except Exception as e:
        logger.error(f"AI 对话失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"对话失败: {str(e)}"
        )

