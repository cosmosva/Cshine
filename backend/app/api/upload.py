"""
文件上传 API
"""

import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from loguru import logger

from app.models import User
from app.dependencies import get_current_user
from app.schemas import UploadResponse, ResponseModel
from app.utils.oss import upload_audio_to_oss, generate_oss_upload_signature
from config import settings

router = APIRouter()


def save_upload_file(upload_file: UploadFile, user_id: str) -> tuple:
    """
    保存上传的文件
    
    Args:
        upload_file: 上传的文件
        user_id: 用户ID
        
    Returns:
        (file_path, file_size) 文件路径和大小
    """
    # 创建上传目录
    upload_dir = os.path.join(settings.UPLOAD_DIR, user_id)
    os.makedirs(upload_dir, exist_ok=True)
    
    # 生成唯一文件名
    file_ext = os.path.splitext(upload_file.filename)[1]
    file_name = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(upload_dir, file_name)
    
    # 保存文件
    file_size = 0
    with open(file_path, "wb") as f:
        content = upload_file.file.read()
        file_size = len(content)
        f.write(content)
    
    return file_path, file_size


@router.post("/audio", response_model=ResponseModel)
async def upload_audio(
    file: UploadFile = File(..., description="音频文件"),
    current_user: User = Depends(get_current_user)
):
    """
    上传音频文件到阿里云 OSS
    
    支持的格式：mp3, m4a, wav, amr
    最大文件大小：500MB
    """
    temp_file_path = None
    
    try:
        # 1. 验证文件类型
        allowed_extensions = ['.mp3', '.m4a', '.wav', '.amr']
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件格式，仅支持: {', '.join(allowed_extensions)}"
            )
        
        # 2. 读取文件内容到内存
        content = await file.read()
        file_size = len(content)
        
        # 3. 验证文件大小
        if file_size > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"文件过大，最大支持 {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB"
            )
        
        # 4. 保存到临时文件
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        temp_filename = f"{uuid.uuid4()}{file_ext}"
        temp_file_path = os.path.join(settings.UPLOAD_DIR, temp_filename)
        
        with open(temp_file_path, "wb") as f:
            f.write(content)
        
        logger.info(f"临时文件已保存: {temp_file_path} ({file_size} bytes)")
        
        # 5. 上传到 OSS
        try:
            oss_url = upload_audio_to_oss(temp_file_path, current_user.id, file_ext)
            logger.info(f"用户 {current_user.id} 上传音频到 OSS: {oss_url}")
        except Exception as e:
            logger.error(f"OSS 上传失败: {e}")
            raise HTTPException(status_code=500, detail=f"OSS 上传失败: {str(e)}")
        
        return ResponseModel(
            code=200,
            message="上传成功",
            data=UploadResponse(
                file_url=oss_url,  # 返回 OSS 公开访问 URL
                file_size=file_size,
                duration=None,  # TODO: 从音频文件中提取时长
                task_id=None  # 音频上传不触发 AI，由创建闪记时触发
            )
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"上传音频失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # 6. 延迟删除临时文件（保留一段时间，避免并发访问问题）
        # 注意：生产环境建议使用定时任务清理临时文件
        pass  # 暂时不删除，让系统或定时任务处理


@router.post("/audio-and-meeting", response_model=ResponseModel)
async def upload_audio_and_create_meeting(
    file: UploadFile = File(..., description="音频文件"),
    title: str = None,
    folder_id: int = None,
    current_user: User = Depends(get_current_user)
):
    """
    一次性完成：上传音频 + 创建会议记录
    
    这个接口解决了前端上传过程中页面刷新导致状态丢失的问题
    """
    from app.api.meeting import create_meeting
    from app.schemas import MeetingCreate
    from sqlalchemy.orm import Session
    from app.database import get_db
    
    temp_file_path = None
    
    try:
        # 1. 验证文件类型
        allowed_extensions = ['.mp3', '.m4a', '.wav', '.amr']
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件格式，仅支持: {', '.join(allowed_extensions)}"
            )
        
        # 2. 读取文件内容
        content = await file.read()
        file_size = len(content)
        
        # 3. 验证文件大小
        if file_size > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"文件过大，最大支持 {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB"
            )
        
        # 4. 保存到临时文件
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        temp_filename = f"{uuid.uuid4()}{file_ext}"
        temp_file_path = os.path.join(settings.UPLOAD_DIR, temp_filename)
        
        with open(temp_file_path, "wb") as f:
            f.write(content)
        
        logger.info(f"临时文件已保存: {temp_file_path} ({file_size} bytes)")
        
        # 5. 上传到 OSS
        try:
            oss_url = upload_audio_to_oss(temp_file_path, current_user.id, file_ext)
            logger.info(f"用户 {current_user.id} 上传音频到 OSS: {oss_url}")
        except Exception as e:
            logger.error(f"OSS 上传失败: {e}")
            raise HTTPException(status_code=500, detail=f"OSS 上传失败: {str(e)}")
        
        # 6. 创建会议记录
        from app.database import SessionLocal
        db = SessionLocal()
        try:
            meeting_data = MeetingCreate(
                title=title or file.filename,
                audio_url=oss_url,
                audio_duration=0,  # TODO: 从音频文件提取
                folder_id=folder_id
            )
            
            # 调用创建会议的逻辑
            from app.models import Meeting, MeetingStatus
            from app.services.meeting_processor import process_meeting_ai_async
            
            meeting = Meeting(
                user_id=current_user.id,
                title=meeting_data.title,
                audio_url=meeting_data.audio_url,
                audio_duration=meeting_data.audio_duration,
                folder_id=meeting_data.folder_id,
                status=MeetingStatus.PENDING
            )
            
            db.add(meeting)
            db.commit()
            db.refresh(meeting)
            
            logger.info(f"会议记录已创建: {meeting.id}")
            
            # 触发 AI 处理
            process_meeting_ai_async(meeting.id, meeting.audio_url)
            logger.info(f"会议 AI 处理已启动: meeting_id={meeting.id}")
            
            return ResponseModel(
                code=200,
                message="上传成功，正在处理...",
                data={
                    "meeting_id": meeting.id,
                    "file_url": oss_url,
                    "file_size": file_size
                }
            )
        finally:
            db.close()
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"上传并创建会议失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/oss-signature", response_model=ResponseModel)
async def get_oss_signature(
    current_user: User = Depends(get_current_user)
):
    """
    获取 OSS 上传签名（用于前端直传）
    
    返回阿里云 OSS 的上传签名，前端可以直接使用签名上传文件到 OSS
    """
    try:
        signature_data = generate_oss_upload_signature(current_user.id)
        
        return ResponseModel(
            code=200,
            message="success",
            data=signature_data
        )
    
    except Exception as e:
        logger.error(f"生成 OSS 签名失败: {e}")
        raise HTTPException(status_code=500, detail=f"生成签名失败: {str(e)}")


