"""
AI 异步处理器
处理音频转写和智能分析
"""

import json
import threading
from typing import Optional
from loguru import logger
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Flash
from app.services.tingwu_service import tingwu_service
from app.services.classifier import classifier


def process_flash_ai_async(flash_id: str, audio_url: str):
    """
    后台异步处理闪记的 AI 分析
    
    Args:
        flash_id: 闪记ID
        audio_url: 音频文件URL（需要公网可访问）
    """
    # 在新线程中执行
    thread = threading.Thread(
        target=_process_flash_ai,
        args=(flash_id, audio_url),
        daemon=True
    )
    thread.start()
    logger.info(f"启动 AI 处理线程: flash_id={flash_id}")


def _process_flash_ai(flash_id: str, audio_url: str):
    """
    执行 AI 处理（在后台线程中）
    
    流程：
    1. 提交通义听悟任务
    2. 轮询等待完成
    3. 解析结果
    4. 智能分类
    5. 更新数据库
    """
    db: Session = SessionLocal()
    
    try:
        # 1. 查询闪记记录
        flash = db.query(Flash).filter(Flash.id == flash_id).first()
        if not flash:
            logger.error(f"闪记不存在: {flash_id}")
            return
        
        # 2. 提交通义听悟任务
        logger.info(f"提交通义听悟任务: flash_id={flash_id}, audio_url={audio_url}")
        
        task_result = tingwu_service.create_task(
            file_url=audio_url,
            source_language="cn",  # 中文
            enable_summarization=True,
            enable_chapters=False,  # 短音频不需要章节
            enable_meeting_assistance=True  # 开启会议助手获取关键句
        )
        
        task_id = task_result['task_id']
        
        # 更新状态为处理中
        flash.ai_status = 'processing'
        flash.ai_task_id = task_id
        db.commit()
        
        logger.info(f"通义听悟任务已提交: task_id={task_id}")
        
        # 3. 等待任务完成（轮询，最多等待30分钟）
        result = tingwu_service.wait_for_completion(
            task_id=task_id,
            max_wait_seconds=1800,  # 30分钟
            poll_interval=5  # 每5秒查询一次
        )
        
        # 4. 解析结果
        parsed_result = result.get('result', {})
        transcription = parsed_result.get('transcription', '')
        summary = parsed_result.get('summary', '')
        key_sentences = parsed_result.get('key_sentences', [])
        
        logger.info(f"转写完成: flash_id={flash_id}, 文本长度={len(transcription)}")
        
        # 5. 智能分类
        category = classifier.classify(transcription)
        
        # 6. 提取关键词
        keywords = classifier.extract_keywords(
            text=transcription,
            summary=summary,
            key_sentences=key_sentences
        )
        
        # 7. 生成标题（摘要的前20字或转写文本的前20字）
        title = summary[:20] if summary else transcription[:20]
        if not title:
            title = "语音记录"
        
        # 8. 更新数据库
        flash.content = transcription or '语音转写中...'
        flash.title = title
        flash.summary = summary
        flash.keywords = json.dumps(keywords, ensure_ascii=False)
        flash.category = category
        flash.ai_status = 'completed'
        flash.ai_error = None
        
        db.commit()
        
        logger.info(f"AI 处理完成: flash_id={flash_id}, category={category}, keywords={keywords}")
        
    except Exception as e:
        logger.error(f"AI 处理失败: flash_id={flash_id}, error={e}")
        
        # 更新错误状态
        try:
            flash = db.query(Flash).filter(Flash.id == flash_id).first()
            if flash:
                flash.ai_status = 'failed'
                flash.ai_error = str(e)
                db.commit()
        except:
            pass
            
    finally:
        db.close()


def check_flash_ai_status(flash_id: str) -> dict:
    """
    检查闪记的 AI 处理状态
    
    Args:
        flash_id: 闪记ID
    
    Returns:
        {
            "status": "pending/processing/completed/failed",
            "progress": 0-100,
            "error": "错误信息"
        }
    """
    db: Session = SessionLocal()
    
    try:
        flash = db.query(Flash).filter(Flash.id == flash_id).first()
        if not flash:
            return {"status": "not_found"}
        
        status_info = {
            "status": flash.ai_status,
            "flash_id": flash_id
        }
        
        # 如果正在处理中，查询通义听悟任务进度
        if flash.ai_status == 'processing' and flash.ai_task_id:
            try:
                task_status = tingwu_service.get_task_status(flash.ai_task_id)
                if task_status['status'] == 'SUCCEEDED':
                    # 任务已完成但数据库还没更新，触发更新
                    status_info['status'] = 'processing'
                    status_info['message'] = '正在更新结果...'
                elif task_status['status'] == 'FAILED':
                    flash.ai_status = 'failed'
                    flash.ai_error = task_status.get('error_message', '任务失败')
                    db.commit()
                    status_info['status'] = 'failed'
                    status_info['error'] = flash.ai_error
            except Exception as e:
                logger.error(f"查询任务状态失败: {e}")
        
        # 如果失败，返回错误信息
        if flash.ai_status == 'failed':
            status_info['error'] = flash.ai_error or '未知错误'
        
        return status_info
        
    finally:
        db.close()

