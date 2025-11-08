"""
会议纪要相关 API
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from loguru import logger
import json

from app.database import get_db
from app.models import User, Meeting, MeetingStatus
from app.dependencies import get_current_user
from app.schemas import (
    MeetingCreate,
    MeetingUpdate,
    MeetingResponse,
    MeetingListResponse,
    MeetingStatusResponse,
    ResponseModel
)
from app.services.meeting_processor import process_meeting_ai_async, check_meeting_ai_status

router = APIRouter()


@router.post("/create", response_model=ResponseModel)
async def create_meeting(
    meeting_data: MeetingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建会议纪要
    
    上传会议音频文件，自动生成结构化纪要
    """
    try:
        # 创建会议记录
        meeting = Meeting(
            user_id=current_user.id,
            title=meeting_data.title,
            participants=json.dumps(meeting_data.participants, ensure_ascii=False) if meeting_data.participants else None,
            meeting_date=meeting_data.meeting_date,
            audio_url=meeting_data.audio_url,
            audio_duration=meeting_data.audio_duration,
            status=MeetingStatus.PENDING
        )
        
        db.add(meeting)
        db.commit()
        db.refresh(meeting)
        
        logger.info(f"Meeting created: {meeting.id} by user {current_user.id}")
        
        # 触发 AI 处理
        try:
            process_meeting_ai_async(meeting.id, meeting.audio_url)
            logger.info(f"会议 AI 处理已启动: meeting_id={meeting.id}")
        except Exception as e:
            logger.error(f"启动会议 AI 处理失败: {e}")
            # 不影响创建流程，继续返回
        
        return ResponseModel(
            code=200,
            message="会议创建成功，正在处理中...",
            data=MeetingResponse.from_orm(meeting)
        )
    
    except Exception as e:
        db.rollback()
        logger.error(f"Create meeting error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list", response_model=ResponseModel)
async def get_meeting_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    status: Optional[str] = Query(None, description="状态筛选"),
    is_favorite: Optional[bool] = Query(None, description="收藏筛选"),
    sort_by: Optional[str] = Query("time", description="排序方式: time/favorite"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取会议纪要列表
    
    支持分页、状态筛选、收藏筛选、排序
    """
    try:
        # 构建查询
        query = db.query(Meeting).filter(Meeting.user_id == current_user.id)
        
        # 状态筛选
        if status:
            try:
                status_enum = MeetingStatus(status)
                query = query.filter(Meeting.status == status_enum)
            except ValueError:
                pass  # 忽略无效状态
        
        # 收藏筛选
        if is_favorite is not None:
            query = query.filter(Meeting.is_favorite == is_favorite)
        
        # 总数
        total = query.count()
        
        # 排序
        if sort_by == "favorite":
            # 收藏优先，然后按时间倒序
            query = query.order_by(desc(Meeting.is_favorite), desc(Meeting.created_at))
        else:
            # 默认按时间倒序
            query = query.order_by(desc(Meeting.created_at))
        
        # 分页
        meetings = query.offset((page - 1) * page_size)\
            .limit(page_size)\
            .all()
        
        return ResponseModel(
            code=200,
            message="success",
            data=MeetingListResponse(
                total=total,
                page=page,
                page_size=page_size,
                items=[MeetingResponse.from_orm(m) for m in meetings]
            )
        )
    
    except Exception as e:
        logger.error(f"Get meeting list error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{meeting_id}", response_model=ResponseModel)
async def get_meeting_detail(
    meeting_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取会议纪要详情
    """
    meeting = db.query(Meeting).filter(
        Meeting.id == meeting_id,
        Meeting.user_id == current_user.id
    ).first()
    
    if not meeting:
        raise HTTPException(status_code=404, detail="会议纪要不存在")
    
    return ResponseModel(
        code=200,
        message="success",
        data=MeetingResponse.from_orm(meeting)
    )


@router.put("/{meeting_id}", response_model=ResponseModel)
async def update_meeting(
    meeting_id: str,
    meeting_data: MeetingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新会议纪要
    """
    meeting = db.query(Meeting).filter(
        Meeting.id == meeting_id,
        Meeting.user_id == current_user.id
    ).first()
    
    if not meeting:
        raise HTTPException(status_code=404, detail="会议纪要不存在")
    
    try:
        # 更新字段
        update_data = meeting_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            # participants 需要转换为 JSON 字符串
            if field == 'participants' and value is not None:
                value = json.dumps(value, ensure_ascii=False)
            setattr(meeting, field, value)
        
        db.commit()
        db.refresh(meeting)
        
        logger.info(f"Meeting updated: {meeting_id}")
        
        return ResponseModel(
            code=200,
            message="更新成功",
            data=MeetingResponse.from_orm(meeting)
        )
    
    except Exception as e:
        db.rollback()
        logger.error(f"Update meeting error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{meeting_id}", response_model=ResponseModel)
async def delete_meeting(
    meeting_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除会议纪要
    """
    meeting = db.query(Meeting).filter(
        Meeting.id == meeting_id,
        Meeting.user_id == current_user.id
    ).first()
    
    if not meeting:
        raise HTTPException(status_code=404, detail="会议纪要不存在")
    
    try:
        db.delete(meeting)
        db.commit()
        
        logger.info(f"Meeting deleted: {meeting_id}")
        
        return ResponseModel(
            code=200,
            message="删除成功",
            data={"id": meeting_id}
        )
    
    except Exception as e:
        db.rollback()
        logger.error(f"Delete meeting error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{meeting_id}/favorite", response_model=ResponseModel)
async def toggle_meeting_favorite(
    meeting_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    切换会议收藏状态
    """
    meeting = db.query(Meeting).filter(
        Meeting.id == meeting_id,
        Meeting.user_id == current_user.id
    ).first()
    
    if not meeting:
        raise HTTPException(status_code=404, detail="会议纪要不存在")
    
    try:
        # 切换收藏状态
        meeting.is_favorite = not meeting.is_favorite
        db.commit()
        db.refresh(meeting)
        
        logger.info(f"Meeting favorite toggled: {meeting_id}, is_favorite={meeting.is_favorite}")
        
        return ResponseModel(
            code=200,
            message="收藏状态已更新",
            data=MeetingResponse.from_orm(meeting)
        )
    
    except Exception as e:
        db.rollback()
        logger.error(f"Toggle meeting favorite error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{meeting_id}/status", response_model=ResponseModel)
async def get_meeting_status(
    meeting_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    查询会议纪要的 AI 处理状态
    
    用于轮询查询处理进度
    """
    # 验证权限
    meeting = db.query(Meeting).filter(
        Meeting.id == meeting_id,
        Meeting.user_id == current_user.id
    ).first()
    
    if not meeting:
        raise HTTPException(status_code=404, detail="会议纪要不存在")
    
    try:
        status_info = check_meeting_ai_status(meeting_id)
        
        return ResponseModel(
            code=200,
            message="success",
            data=status_info
        )
    
    except Exception as e:
        logger.error(f"Get meeting status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

