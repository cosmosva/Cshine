"""
会议纪要 AI 处理器（优化版）
两阶段处理架构：
  阶段1：通义听悟转录（转录文本 + 说话人分离）
  阶段2：LLM 总结（基于转录文本生成摘要/要点/行动项/思维导图）
"""

import json
import threading
from typing import Optional, List, Dict
from loguru import logger
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Meeting, MeetingStatus
from app.services.tingwu_service import tingwu_service
from app.services.llm_summary_service import llm_summary_service


# ===================== 第一阶段：通义听悟转录 =====================


def process_meeting_transcription_async(meeting_id: str, audio_url: str):
    """
    后台异步处理会议音频转录（仅转录 + 说话人分离）

    Args:
        meeting_id: 会议ID
        audio_url: 音频文件URL（需要公网可访问）
    """
    thread = threading.Thread(
        target=_process_meeting_transcription,
        args=(meeting_id, audio_url),
        daemon=True
    )
    thread.start()
    logger.info(f"启动会议转录线程: meeting_id={meeting_id}")


def _process_meeting_transcription(meeting_id: str, audio_url: str):
    """
    执行会议音频转录（在后台线程中）

    流程：
    1. 提交通义听悟任务（仅转录 + 说话人分离）
    2. 轮询等待完成
    3. 解析转录文本和段落数据
    4. 更新数据库（仅转录相关字段）

    Args:
        meeting_id: 会议ID
        audio_url: 音频URL
    """
    db: Session = SessionLocal()

    try:
        # 1. 查询会议记录
        meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if not meeting:
            logger.error(f"会议不存在: {meeting_id}")
            return

        # 更新状态为处理中
        meeting.status = MeetingStatus.PROCESSING
        db.commit()

        # 2. 提交通义听悟任务（简化配置：仅转录 + 说话人）
        logger.info(f"提交会议转录任务: meeting_id={meeting_id}, audio_url={audio_url}")

        task_result = tingwu_service.create_task(
            file_url=audio_url,
            source_language="cn",
            enable_summarization=False,  # 关闭智能摘要（由 LLM 生成）
            enable_chapters=False,  # 关闭章节划分
            enable_meeting_assistance=False,  # 关闭会议助手
            enable_speaker_diarization=True,  # 仅开启说话人分离
            speaker_count=0  # 0表示不定人数，自动识别
        )

        task_id = task_result['task_id']
        logger.info(f"会议转录任务已提交: task_id={task_id}")

        # 3. 等待任务完成（会议音频可能较长，最多等待60分钟）
        result = tingwu_service.wait_for_completion(
            task_id=task_id,
            max_wait_seconds=3600,  # 60分钟
            poll_interval=10  # 每10秒查询一次
        )

        # 4. 解析结果
        parsed_result = result.get('result', {})
        transcription = parsed_result.get('transcription', '')
        paragraphs = parsed_result.get('paragraphs', [])  # 段落信息（包含说话人）

        logger.info(f"会议转录完成: meeting_id={meeting_id}, 文本长度={len(transcription)}, 段落数={len(paragraphs)}")

        # 5. 更新数据库（仅转录相关字段）
        meeting.transcript = transcription
        meeting.transcript_paragraphs = json.dumps(paragraphs, ensure_ascii=False) if paragraphs else None
        meeting.status = MeetingStatus.COMPLETED  # 转录完成，等待用户选择 AI 生成总结
        db.commit()

        logger.info(f"会议转录处理完成: meeting_id={meeting_id}")

    except Exception as e:
        logger.error(f"会议转录处理失败: meeting_id={meeting_id}, error={e}", exc_info=True)

        # 更新错误状态
        try:
            meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
            if meeting:
                meeting.status = MeetingStatus.FAILED
                db.commit()
                logger.info(f"已将会议 {meeting_id} 状态更新为 FAILED")
        except Exception as update_error:
            logger.error(f"更新会议失败状态时出错: {update_error}")

    finally:
        db.close()


# ===================== 第二阶段：LLM 总结 =====================


def process_meeting_summary_async(meeting_id: str, ai_model_id: str):
    """
    后台异步处理会议总结（基于已有的转录文本）

    Args:
        meeting_id: 会议ID
        ai_model_id: 使用的AI模型ID
    """
    thread = threading.Thread(
        target=_process_meeting_summary,
        args=(meeting_id, ai_model_id),
        daemon=True
    )
    thread.start()
    logger.info(f"启动会议总结线程: meeting_id={meeting_id}, model_id={ai_model_id}")


def _process_meeting_summary(meeting_id: str, ai_model_id: str):
    """
    执行会议 LLM 总结（在后台线程中）

    流程：
    1. 查询会议转录文本
    2. 调用 LLM 服务生成摘要/要点/行动项/标签/思维导图
    3. 更新数据库

    Args:
        meeting_id: 会议ID
        ai_model_id: AI模型ID
    """
    db: Session = SessionLocal()

    try:
        # 1. 查询会议记录
        meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if not meeting:
            logger.error(f"会议不存在: {meeting_id}")
            return

        # 检查是否有转录文本
        if not meeting.transcript:
            logger.error(f"会议尚未完成转录: {meeting_id}")
            meeting.status = MeetingStatus.FAILED
            db.commit()
            return

        # 更新状态为处理中
        meeting.status = MeetingStatus.PROCESSING
        meeting.ai_model_id = ai_model_id  # 保存使用的 AI 模型
        db.commit()

        # 2. 解析说话人信息（如果有）
        speakers_info = None
        if meeting.transcript_paragraphs:
            try:
                paragraphs = json.loads(meeting.transcript_paragraphs)
                # 提取唯一说话人列表
                speakers_set = set()
                for para in paragraphs:
                    speaker_id = para.get('SpeakerId')
                    if speaker_id:
                        speakers_set.add(speaker_id)

                speakers_info = [{"speaker_id": s} for s in speakers_set]
            except Exception as e:
                logger.warning(f"解析说话人信息失败: {e}")

        # 3. 调用 LLM 服务生成完整总结
        logger.info(f"开始 LLM 总结: meeting_id={meeting_id}, model_id={ai_model_id}")

        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        summary_result = loop.run_until_complete(
            llm_summary_service.generate_full_summary(
                transcript=meeting.transcript,
                speakers_info=speakers_info,
                model_id=ai_model_id,
                db=db
            )
        )

        loop.close()

        logger.info(f"LLM 总结完成: meeting_id={meeting_id}")

        # 4. 更新数据库
        meeting.summary = summary_result.get('summary', '')
        meeting.key_points = json.dumps(summary_result.get('key_points', []), ensure_ascii=False)
        meeting.action_items = json.dumps(summary_result.get('action_items', []), ensure_ascii=False)
        meeting.tags = json.dumps(summary_result.get('tags', []), ensure_ascii=False) if summary_result.get('tags') else None
        meeting.mind_map = summary_result.get('mind_map', '')
        meeting.status = MeetingStatus.COMPLETED

        db.commit()

        logger.info(f"会议总结处理完成: meeting_id={meeting_id}, 要点数={len(summary_result.get('key_points', []))}, 行动项数={len(summary_result.get('action_items', []))}")

    except Exception as e:
        logger.error(f"会议总结处理失败: meeting_id={meeting_id}, error={e}", exc_info=True)

        # 更新错误状态
        try:
            meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
            if meeting:
                meeting.status = MeetingStatus.FAILED
                db.commit()
                logger.info(f"已将会议 {meeting_id} 状态更新为 FAILED")
        except Exception as update_error:
            logger.error(f"更新会议失败状态时出错: {update_error}")

    finally:
        db.close()


# ===================== 状态查询 =====================


def check_meeting_ai_status(meeting_id: str) -> Dict:
    """
    检查会议纪要的 AI 处理状态

    Args:
        meeting_id: 会议ID

    Returns:
        {
            "meeting_id": "xxx",
            "status": "pending/processing/completed/failed",
            "progress": 0-100,
            "message": "处理信息"
        }
    """
    db: Session = SessionLocal()

    try:
        meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if not meeting:
            return {"status": "not_found"}

        status_value = meeting.status.value if hasattr(meeting.status, 'value') else str(meeting.status)

        status_info = {
            "meeting_id": meeting_id,
            "status": status_value
        }

        # 根据状态提供不同信息
        if status_value == MeetingStatus.PENDING.value:
            status_info['message'] = '等待处理...'
            status_info['progress'] = 0
        elif status_value == MeetingStatus.PROCESSING.value:
            # 判断是转录中还是总结中
            if meeting.transcript:
                status_info['message'] = '正在生成 AI 总结...'
                status_info['progress'] = 70
            else:
                status_info['message'] = '正在转录音频...'
                status_info['progress'] = 30
        elif status_value == MeetingStatus.COMPLETED.value:
            status_info['message'] = '处理完成'
            status_info['progress'] = 100
        elif status_value == MeetingStatus.FAILED.value:
            status_info['message'] = '处理失败'
            status_info['error'] = '音频处理出错，请稍后重试'

        return status_info

    finally:
        db.close()
