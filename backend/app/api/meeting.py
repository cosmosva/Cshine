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
from app.models import User, Meeting, MeetingStatus, MeetingSpeaker, Contact
from app.dependencies import get_current_user
from app.schemas import (
    MeetingCreate,
    MeetingUpdate,
    MeetingResponse,
    MeetingListResponse,
    MeetingStatusResponse,
    GenerateSummaryRequest,
    SpeakerMapRequest,
    SpeakerResponse,
    SpeakerListResponse,
    ContactResponse,
    ResponseModel
)
from app.services.meeting_processor import (
    process_meeting_transcription_async,
    process_meeting_summary_async,
    check_meeting_ai_status
)

router = APIRouter()


@router.post("/create", response_model=ResponseModel)
async def create_meeting(
    meeting_data: MeetingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建会议纪要（优化版）

    仅上传音频文件，不进行任何 AI 处理
    用户需在详情页点击"立即生成"并选择 AI 模型后，才开始处理
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
            folder_id=meeting_data.folder_id,
            status=MeetingStatus.PENDING  # 初始状态：等待处理
        )

        db.add(meeting)
        db.commit()
        db.refresh(meeting)

        logger.info(f"Meeting created: {meeting.id} by user {current_user.id}")

        return ResponseModel(
            code=200,
            message="会议上传成功",
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
    folder_id: Optional[str] = Query(None, description="知识库ID筛选，传 'uncategorized' 查询未分类"),  # ✨新增
    sort_by: Optional[str] = Query("time", description="排序方式: time/favorite"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取会议纪要列表

    支持分页、状态筛选、收藏筛选、知识库筛选、排序
    folder_id 参数：
    - None: 查询所有会议
    - 'uncategorized': 查询未分类的会议（folder_id 为 NULL）
    - 数字ID: 查询指定知识库的会议
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

        # 知识库筛选 ✨新增
        if folder_id is not None:
            if folder_id == 'uncategorized':
                # 查询未分类的会议
                query = query.filter(Meeting.folder_id == None)
            else:
                # 查询指定知识库的会议
                try:
                    folder_id_int = int(folder_id)
                    query = query.filter(Meeting.folder_id == folder_id_int)
                except ValueError:
                    pass  # 忽略无效的 folder_id
        
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


@router.post("/{meeting_id}/copy", response_model=ResponseModel)
async def copy_meeting(
    meeting_id: str,
    copy_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    复制会议纪要到指定知识库
    
    Args:
        meeting_id: 要复制的会议ID
        copy_data: {"folder_id": int | null}
    """
    # 查找原会议
    original_meeting = db.query(Meeting).filter(
        Meeting.id == meeting_id,
        Meeting.user_id == current_user.id
    ).first()
    
    if not original_meeting:
        raise HTTPException(status_code=404, detail="会议纪要不存在")
    
    try:
        # 创建新的会议副本
        new_meeting = Meeting(
            user_id=current_user.id,
            folder_id=copy_data.get('folder_id'),
            title=f"{original_meeting.title}（副本）",
            participants=original_meeting.participants,
            meeting_date=original_meeting.meeting_date,
            audio_url=original_meeting.audio_url,
            audio_duration=original_meeting.audio_duration,
            transcript=original_meeting.transcript,
            summary=original_meeting.summary,
            conversational_summary=original_meeting.conversational_summary,
            mind_map=original_meeting.mind_map,
            key_points=original_meeting.key_points,
            action_items=original_meeting.action_items,
            tags=original_meeting.tags,
            status=original_meeting.status,
            is_favorite=False  # 副本默认不收藏
        )
        
        db.add(new_meeting)
        db.commit()
        db.refresh(new_meeting)
        
        logger.info(f"Meeting copied: {meeting_id} -> {new_meeting.id}, folder_id={copy_data.get('folder_id')}")
        
        return ResponseModel(
            code=200,
            message="会议已复制",
            data=MeetingResponse.from_orm(new_meeting)
        )
    
    except Exception as e:
        db.rollback()
        logger.error(f"Copy meeting error: {e}")
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


@router.post("/{meeting_id}/speakers/map", response_model=ResponseModel)
async def map_speaker(
    meeting_id: str,
    speaker_data: SpeakerMapRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    标注会议说话人
    
    将"说话人1"、"说话人2"等映射到联系人或自定义名称
    
    Args:
        meeting_id: 会议ID
        speaker_data: {
            "speaker_id": "说话人1",
            "contact_id": 123  # 可选，关联到联系人
            "custom_name": "张三"  # 可选，自定义名称
        }
    """
    # 验证会议权限
    meeting = db.query(Meeting).filter(
        Meeting.id == meeting_id,
        Meeting.user_id == current_user.id
    ).first()
    
    if not meeting:
        raise HTTPException(status_code=404, detail="会议纪要不存在")
    
    # 验证至少提供一种映射方式
    if not speaker_data.contact_id and not speaker_data.custom_name:
        raise HTTPException(status_code=400, detail="请提供联系人ID或自定义名称")
    
    # 如果提供了联系人ID，验证联系人是否存在
    if speaker_data.contact_id:
        contact = db.query(Contact).filter(
            Contact.id == speaker_data.contact_id,
            Contact.user_id == current_user.id
        ).first()
        
        if not contact:
            raise HTTPException(status_code=404, detail="联系人不存在")
    
    try:
        # 查找或创建说话人映射
        speaker_map = db.query(MeetingSpeaker).filter(
            MeetingSpeaker.meeting_id == meeting_id,
            MeetingSpeaker.speaker_id == speaker_data.speaker_id
        ).first()
        
        if speaker_map:
            # 更新已有映射
            speaker_map.contact_id = speaker_data.contact_id
            speaker_map.custom_name = speaker_data.custom_name
        else:
            # 创建新映射
            speaker_map = MeetingSpeaker(
                meeting_id=meeting_id,
                speaker_id=speaker_data.speaker_id,
                contact_id=speaker_data.contact_id,
                custom_name=speaker_data.custom_name
            )
            db.add(speaker_map)
        
        db.commit()
        db.refresh(speaker_map)
        
        # 构建响应
        display_name = speaker_data.custom_name
        contact_info = None
        
        if speaker_data.contact_id:
            contact = db.query(Contact).filter(Contact.id == speaker_data.contact_id).first()
            if contact:
                display_name = contact.name
                contact_info = ContactResponse.from_orm(contact)
        
        logger.info(f"Speaker mapped: meeting={meeting_id}, speaker={speaker_data.speaker_id}, name={display_name}")
        
        return ResponseModel(
            code=200,
            message="标注成功",
            data=SpeakerResponse(
                speaker_id=speaker_data.speaker_id,
                display_name=display_name,
                contact_id=speaker_data.contact_id,
                contact=contact_info
            )
        )
    
    except Exception as e:
        db.rollback()
        logger.error(f"Map speaker error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{meeting_id}/speakers", response_model=ResponseModel)
async def get_meeting_speakers(
    meeting_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取会议的说话人映射关系
    
    返回该会议中所有说话人的标注信息
    """
    # 验证会议权限
    meeting = db.query(Meeting).filter(
        Meeting.id == meeting_id,
        Meeting.user_id == current_user.id
    ).first()
    
    if not meeting:
        raise HTTPException(status_code=404, detail="会议纪要不存在")
    
    try:
        # 查询所有说话人映射
        speaker_maps = db.query(MeetingSpeaker).filter(
            MeetingSpeaker.meeting_id == meeting_id
        ).all()
        
        # 构建响应
        speakers = []
        for speaker_map in speaker_maps:
            display_name = speaker_map.custom_name or speaker_map.speaker_id
            contact_info = None
            
            if speaker_map.contact_id:
                contact = db.query(Contact).filter(Contact.id == speaker_map.contact_id).first()
                if contact:
                    display_name = contact.name
                    contact_info = ContactResponse.from_orm(contact)
            
            speakers.append(SpeakerResponse(
                speaker_id=speaker_map.speaker_id,
                display_name=display_name,
                contact_id=speaker_map.contact_id,
                contact=contact_info
            ))
        
        return ResponseModel(
            code=200,
            message="success",
            data=SpeakerListResponse(items=speakers)
        )
    
    except Exception as e:
        logger.error(f"Get meeting speakers error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{meeting_id}/generate-summary", response_model=ResponseModel)
async def generate_meeting_summary(
    meeting_id: str,
    request_data: GenerateSummaryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    生成会议总结（新版）

    两阶段处理：
    1. 如果会议尚未转录，先调用通义听悟转录（仅转录+说话人）
    2. 使用指定的 AI 模型生成总结（摘要/要点/行动项/思维导图）

    Args:
        meeting_id: 会议ID
        request_data: {"ai_model_id": "xxx"}
    """
    # 验证会议权限
    meeting = db.query(Meeting).filter(
        Meeting.id == meeting_id,
        Meeting.user_id == current_user.id
    ).first()

    if not meeting:
        raise HTTPException(status_code=404, detail="会议纪要不存在")

    if not meeting.audio_url:
        raise HTTPException(status_code=400, detail="该会议没有音频文件")

    try:
        # 检查是否已有转录文本
        if meeting.transcript:
            # 已有转录，直接生成 LLM 总结（第二阶段）
            logger.info(f"会议已有转录，直接生成总结: meeting_id={meeting_id}")

            meeting.status = MeetingStatus.PROCESSING
            db.commit()

            process_meeting_summary_async(meeting.id, request_data.ai_model_id)

            return ResponseModel(
                code=200,
                message="正在生成 AI 总结，请稍候...",
                data={"meeting_id": meeting_id, "status": "processing", "stage": "summarizing"}
            )
        else:
            # 尚未转录，先进行转录（第一阶段）
            logger.info(f"会议尚未转录，启动转录: meeting_id={meeting_id}")

            meeting.status = MeetingStatus.PROCESSING
            meeting.ai_model_id = request_data.ai_model_id  # 保存 AI 模型，转录完成后使用
            db.commit()

            process_meeting_transcription_async(meeting.id, meeting.audio_url)

            return ResponseModel(
                code=200,
                message="正在转录音频，请稍候...",
                data={"meeting_id": meeting_id, "status": "processing", "stage": "transcribing"}
            )

    except Exception as e:
        db.rollback()
        logger.error(f"Generate meeting summary error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# v0.9.9：已移除 /reprocess 接口，统一使用 /generate-summary
# 前端"重新生成"和"立即生成"现在都调用同一个接口
# 后端会智能判断：已有转录则直接生成总结，无转录则先转录再生成



