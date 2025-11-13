"""
AI 提示词模板管理 API
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from loguru import logger
from datetime import datetime

from app.database import get_db
from app.models import AIPrompt, AdminUser, PromptScenario
from app.schemas import (
    AIPromptCreate,
    AIPromptUpdate,
    AIPromptResponse,
    AIPromptListResponse,
    ResponseModel
)
from app.dependencies import get_current_admin

router = APIRouter(prefix="/api/admin/ai-prompts", tags=["AI提示词管理"])


@router.get("", response_model=ResponseModel)
async def list_ai_prompts(
    skip: int = 0,
    limit: int = 100,
    scenario: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """
    获取 AI 提示词列表
    
    - **skip**: 跳过数量
    - **limit**: 限制数量
    - **scenario**: 过滤使用场景
    - **is_active**: 过滤启用状态
    """
    try:
        query = db.query(AIPrompt)
        
        # 过滤条件
        if scenario:
            query = query.filter(AIPrompt.scenario == scenario)
        if is_active is not None:
            query = query.filter(AIPrompt.is_active == is_active)
        
        # 总数
        total = query.count()
        
        # 查询列表
        prompts = query.order_by(
            AIPrompt.scenario,
            AIPrompt.is_default.desc(),
            AIPrompt.created_at.desc()
        ).offset(skip).limit(limit).all()
        
        return ResponseModel(
            code=200,
            message="success",
            data=AIPromptListResponse(
                total=total,
                items=[AIPromptResponse.from_orm(prompt) for prompt in prompts]
            )
        )
        
    except Exception as e:
        logger.error(f"获取提示词列表失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取列表失败"
        )


@router.post("", response_model=ResponseModel)
async def create_ai_prompt(
    request: AIPromptCreate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """
    创建提示词模板
    """
    try:
        # 验证场景
        try:
            scenario_enum = PromptScenario(request.scenario)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的场景: {request.scenario}"
            )
        
        # 如果设置为默认模板，取消同场景下其他模板的默认状态
        if request.is_default:
            db.query(AIPrompt).filter(
                AIPrompt.scenario == scenario_enum
            ).update({"is_default": False})
        
        # 创建提示词
        prompt = AIPrompt(
            name=request.name,
            scenario=scenario_enum,
            prompt_template=request.prompt_template,
            variables=request.variables,
            is_active=request.is_active,
            is_default=request.is_default
        )
        
        db.add(prompt)
        db.commit()
        db.refresh(prompt)
        
        logger.info(f"创建提示词模板: {prompt.name} (ID: {prompt.id}), 操作人: {admin.username}")
        
        return ResponseModel(
            code=200,
            message="创建成功",
            data=AIPromptResponse.from_orm(prompt)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"创建提示词模板失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建失败"
        )


@router.get("/{prompt_id}", response_model=ResponseModel)
async def get_ai_prompt(
    prompt_id: str,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """
    获取提示词模板详情
    """
    prompt = db.query(AIPrompt).filter(AIPrompt.id == prompt_id).first()
    
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="提示词模板不存在"
        )
    
    return ResponseModel(
        code=200,
        message="success",
        data=AIPromptResponse.from_orm(prompt)
    )


@router.put("/{prompt_id}", response_model=ResponseModel)
async def update_ai_prompt(
    prompt_id: str,
    request: AIPromptUpdate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """
    更新提示词模板
    """
    try:
        prompt = db.query(AIPrompt).filter(AIPrompt.id == prompt_id).first()
        
        if not prompt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="提示词模板不存在"
            )
        
        # 如果设置为默认模板，取消同场景下其他模板的默认状态
        if request.is_default:
            db.query(AIPrompt).filter(
                AIPrompt.scenario == prompt.scenario,
                AIPrompt.id != prompt_id
            ).update({"is_default": False})
        
        # 更新字段
        update_data = request.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(prompt, key, value)
        
        prompt.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(prompt)
        
        logger.info(f"更新提示词模板: {prompt.name} (ID: {prompt_id}), 操作人: {admin.username}")
        
        return ResponseModel(
            code=200,
            message="更新成功",
            data=AIPromptResponse.from_orm(prompt)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"更新提示词模板失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新失败"
        )


@router.delete("/{prompt_id}", response_model=ResponseModel)
async def delete_ai_prompt(
    prompt_id: str,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """
    删除提示词模板
    """
    try:
        prompt = db.query(AIPrompt).filter(AIPrompt.id == prompt_id).first()
        
        if not prompt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="提示词模板不存在"
            )
        
        # 如果是默认模板，不允许删除
        if prompt.is_default:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能删除默认模板，请先设置其他模板为默认"
            )
        
        prompt_name = prompt.name
        db.delete(prompt)
        db.commit()
        
        logger.info(f"删除提示词模板: {prompt_name} (ID: {prompt_id}), 操作人: {admin.username}")
        
        return ResponseModel(
            code=200,
            message="删除成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"删除提示词模板失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除失败"
        )


@router.get("/scenarios/list", response_model=ResponseModel)
async def list_scenarios(
    admin: AdminUser = Depends(get_current_admin)
):
    """
    获取所有支持的场景列表
    """
    scenarios = [
        {"value": scenario.value, "label": scenario.value}
        for scenario in PromptScenario
    ]
    
    return ResponseModel(
        code=200,
        message="success",
        data=scenarios
    )

