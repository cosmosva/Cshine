"""
闪记相关 API
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from loguru import logger
import json

from app.database import get_db
from app.models import User, Flash
from app.dependencies import get_current_user
from app.schemas import (
    FlashCreate,
    FlashUpdate,
    FlashResponse,
    FlashListResponse,
    ResponseModel
)
from app.services.ai_processor import process_flash_ai_async, check_flash_ai_status

router = APIRouter()


@router.post("/create", response_model=ResponseModel)
async def create_flash(
    flash_data: FlashCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建闪记
    
    接收转写后的文字内容和相关元数据，创建闪记记录
    """
    try:
        # 创建闪记对象
        flash = Flash(
            user_id=current_user.id,
            title=flash_data.title or flash_data.content[:50],  # 默认使用前50字作为标题
            content=flash_data.content,
            summary=flash_data.summary,
            keywords=json.dumps(flash_data.keywords, ensure_ascii=False) if flash_data.keywords else None,
            category=flash_data.category,
            audio_url=flash_data.audio_url,
            audio_duration=flash_data.audio_duration,
            ai_model_id=flash_data.ai_model_id  # ✨新增：记录使用的AI模型
        )
        
        db.add(flash)
        db.commit()
        db.refresh(flash)
        
        logger.info(f"Flash created: {flash.id} by user {current_user.id}")
        
        # 如果有音频URL，触发 AI 处理
        if flash.audio_url:
            try:
                # 后台异步处理（传递 AI 模型 ID）
                process_flash_ai_async(flash.id, flash.audio_url, ai_model_id=flash_data.ai_model_id)
                logger.info(f"AI 处理已启动: flash_id={flash.id}, model_id={flash_data.ai_model_id}")
            except Exception as e:
                logger.error(f"启动 AI 处理失败: {e}")
                # 不影响创建流程，继续返回
        
        return ResponseModel(
            code=200,
            message="创建成功",
            data=FlashResponse.from_orm(flash)
        )
    
    except Exception as e:
        db.rollback()
        logger.error(f"Create flash error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list", response_model=ResponseModel)
async def get_flash_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    category: Optional[str] = Query(None, description="分类筛选"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    is_favorite: Optional[bool] = Query(None, description="仅收藏"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取闪记列表
    
    支持分页、分类筛选、关键词搜索、收藏筛选
    """
    try:
        # 构建查询
        query = db.query(Flash).filter(Flash.user_id == current_user.id)
        
        # 分类筛选
        if category:
            query = query.filter(Flash.category == category)
        
        # 收藏筛选
        if is_favorite is not None:
            query = query.filter(Flash.is_favorite == is_favorite)
        
        # 关键词搜索（简单实现，搜索标题和内容）
        if keyword:
            query = query.filter(
                (Flash.title.contains(keyword)) |
                (Flash.content.contains(keyword))
            )
        
        # 总数
        total = query.count()
        
        # 分页
        flashes = query.order_by(desc(Flash.created_at))\
            .offset((page - 1) * page_size)\
            .limit(page_size)\
            .all()
        
        return ResponseModel(
            code=200,
            message="success",
            data=FlashListResponse(
                total=total,
                page=page,
                page_size=page_size,
                items=[FlashResponse.from_orm(f) for f in flashes]
            )
        )
    
    except Exception as e:
        logger.error(f"Get flash list error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{flash_id}", response_model=ResponseModel)
async def get_flash_detail(
    flash_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取闪记详情
    """
    flash = db.query(Flash).filter(
        Flash.id == flash_id,
        Flash.user_id == current_user.id
    ).first()
    
    if not flash:
        raise HTTPException(status_code=404, detail="闪记不存在")
    
    return ResponseModel(
        code=200,
        message="success",
        data=FlashResponse.from_orm(flash)
    )


@router.put("/{flash_id}", response_model=ResponseModel)
async def update_flash(
    flash_id: str,
    flash_data: FlashUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新闪记
    """
    flash = db.query(Flash).filter(
        Flash.id == flash_id,
        Flash.user_id == current_user.id
    ).first()
    
    if not flash:
        raise HTTPException(status_code=404, detail="闪记不存在")
    
    try:
        # 更新字段
        update_data = flash_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            # keywords 需要转换为 JSON 字符串
            if field == 'keywords' and value is not None:
                value = json.dumps(value, ensure_ascii=False)
            setattr(flash, field, value)
        
        db.commit()
        db.refresh(flash)
        
        logger.info(f"Flash updated: {flash_id}")
        
        return ResponseModel(
            code=200,
            message="更新成功",
            data=FlashResponse.from_orm(flash)
        )
    
    except Exception as e:
        db.rollback()
        logger.error(f"Update flash error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{flash_id}", response_model=ResponseModel)
async def delete_flash(
    flash_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除闪记
    """
    flash = db.query(Flash).filter(
        Flash.id == flash_id,
        Flash.user_id == current_user.id
    ).first()
    
    if not flash:
        raise HTTPException(status_code=404, detail="闪记不存在")
    
    try:
        db.delete(flash)
        db.commit()
        
        logger.info(f"Flash deleted: {flash_id}")
        
        return ResponseModel(
            code=200,
            message="删除成功",
            data={"id": flash_id}
        )
    
    except Exception as e:
        db.rollback()
        logger.error(f"Delete flash error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{flash_id}/favorite", response_model=ResponseModel)
async def toggle_favorite(
    flash_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    切换收藏状态
    """
    flash = db.query(Flash).filter(
        Flash.id == flash_id,
        Flash.user_id == current_user.id
    ).first()
    
    if not flash:
        raise HTTPException(status_code=404, detail="闪记不存在")
    
    try:
        flash.is_favorite = not flash.is_favorite
        db.commit()
        db.refresh(flash)
        
        return ResponseModel(
            code=200,
            message="收藏状态已更新",
            data={"is_favorite": flash.is_favorite}
        )
    
    except Exception as e:
        db.rollback()
        logger.error(f"Toggle favorite error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{flash_id}/ai-status", response_model=ResponseModel)
async def get_flash_ai_status(
    flash_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    查询闪记的 AI 处理状态
    
    用于轮询查询 AI 转写和分析的进度
    """
    # 验证权限
    flash = db.query(Flash).filter(
        Flash.id == flash_id,
        Flash.user_id == current_user.id
    ).first()
    
    if not flash:
        raise HTTPException(status_code=404, detail="闪记不存在")
    
    try:
        status_info = check_flash_ai_status(flash_id)
        
        return ResponseModel(
            code=200,
            message="success",
            data=status_info
        )
    
    except Exception as e:
        logger.error(f"Get AI status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

