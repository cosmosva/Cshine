"""
会议纪要 AI 处理器
处理会议音频的转写、说话人识别、要点提取、行动项识别
"""

import json
import threading
import re
from typing import Optional, List, Dict
from loguru import logger
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Meeting, MeetingStatus
from app.services.tingwu_service import tingwu_service


def process_meeting_ai_async(meeting_id: str, audio_url: str, ai_model_id: str = None):
    """
    后台异步处理会议纪要的 AI 分析
    
    Args:
        meeting_id: 会议ID
        audio_url: 音频文件URL（需要公网可访问）
        ai_model_id: 使用的AI模型ID（可选）
    """
    # 在新线程中执行
    thread = threading.Thread(
        target=_process_meeting_ai,
        args=(meeting_id, audio_url, ai_model_id),
        daemon=True
    )
    thread.start()
    logger.info(f"启动会议 AI 处理线程: meeting_id={meeting_id}, model_id={ai_model_id}")


def _process_meeting_ai(meeting_id: str, audio_url: str, ai_model_id: str = None):
    """
    执行会议 AI 处理（在后台线程中）
    
    流程：
    1. 提交通义听悟任务（开启说话人分离、章节分段等）
    2. 轮询等待完成
    3. 解析转写文本
    4. 提取会议要点（使用LLM或通义听悟）
    5. 识别行动项（使用LLM或通义听悟）
    6. 生成结构化纪要（使用LLM或通义听悟）
    7. 更新数据库
    
    Args:
        meeting_id: 会议ID
        audio_url: 音频URL
        ai_model_id: AI模型ID（可选）
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
        
        # 2. 提交通义听悟任务
        logger.info(f"提交会议转写任务: meeting_id={meeting_id}, audio_url={audio_url}")
        
        # 会议纪要配置：开启完整的会议功能
        task_result = tingwu_service.create_task(
            file_url=audio_url,
            source_language="cn",
            enable_summarization=True,  # 开启智能摘要
            summarization_types=['Paragraph', 'Conversational', 'MindMap'],  # 明确指定三种摘要类型
            enable_chapters=True,  # 开启章节划分（自动识别议题）
            enable_meeting_assistance=True,  # 开启会议助手（行动项识别）
            enable_speaker_diarization=True,  # 开启说话人分离
            speaker_count=0  # 0表示不定人数，自动识别
        )
        
        task_id = task_result['task_id']
        logger.info(f"会议转写任务已提交: task_id={task_id}")
        
        # 3. 等待任务完成（会议音频可能较长，最多等待60分钟）
        result = tingwu_service.wait_for_completion(
            task_id=task_id,
            max_wait_seconds=3600,  # 60分钟
            poll_interval=10  # 每10秒查询一次
        )
        
        # 4. 解析结果
        parsed_result = result.get('result', {})
        transcription = parsed_result.get('transcription', '')
        summary = parsed_result.get('summary', '')
        chapters = parsed_result.get('chapters', [])  # 章节信息
        paragraphs = parsed_result.get('paragraphs', [])  # 段落信息（包含说话人）
        
        logger.info(f"会议转写完成: meeting_id={meeting_id}, 文本长度={len(transcription)}, 段落数={len(paragraphs)}")
        
        # 5. 提取会议要点（优先使用章节信息）
        key_points = _extract_key_points_with_chapters(chapters, paragraphs, transcription, summary)
        
        # 6. 识别行动项（优先使用通义听悟的行动项识别结果）
        tingwu_actions = parsed_result.get('actions', [])
        if tingwu_actions:
            logger.info(f"使用通义听悟识别的行动项: {len(tingwu_actions)}个")
            action_items = _format_tingwu_actions(tingwu_actions)
        else:
            logger.info("通义听悟未返回行动项，使用规则识别")
            action_items = _extract_action_items(transcription, paragraphs)
        
        # 7. 生成会议摘要（如果通义听悟没有返回，则生成简单摘要）
        if not summary:
            summary = _generate_simple_summary(transcription, key_points)
        
        # 8. 获取其他类型的摘要
        conversational_summary = parsed_result.get('conversational_summary', '')
        mind_map = parsed_result.get('mind_map', '')
        
        # 9. 生成AI标签（从关键词和要点中提取）
        tags = _generate_tags(parsed_result.get('keywords', []), key_points, transcription)
        logger.info(f"为会议生成标签: {tags}")
        
        # 10. 更新数据库
        meeting.transcript = transcription
        meeting.transcript_paragraphs = json.dumps(paragraphs, ensure_ascii=False) if paragraphs else None  # ✨新增：保存段落数据
        meeting.summary = summary
        meeting.conversational_summary = conversational_summary  # ✨新增
        meeting.mind_map = mind_map  # ✨新增
        meeting.key_points = json.dumps(key_points, ensure_ascii=False)
        meeting.action_items = json.dumps(action_items, ensure_ascii=False)
        meeting.tags = json.dumps(tags, ensure_ascii=False) if tags else None  # ✨新增
        meeting.status = MeetingStatus.COMPLETED
        
        db.commit()
        
        logger.info(f"会议 AI 处理完成: meeting_id={meeting_id}, 要点数={len(key_points)}, 行动项数={len(action_items)}")
        
    except Exception as e:
        logger.error(f"会议 AI 处理失败: meeting_id={meeting_id}, error={e}", exc_info=True)
        
        # 更新错误状态
        try:
            meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
            if meeting:
                meeting.status = MeetingStatus.FAILED
                # 可以选择记录错误信息（如果模型有error字段）
                db.commit()
                logger.info(f"已将会议 {meeting_id} 状态更新为 FAILED")
        except Exception as update_error:
            logger.error(f"更新会议失败状态时出错: {update_error}")
            
    finally:
        db.close()


def _extract_key_points_with_chapters(
    chapters: List[Dict],
    paragraphs: List[Dict],
    transcription: str,
    summary: str
) -> List[Dict]:
    """
    提取会议要点（优先使用章节信息）
    
    Args:
        chapters: 通义听悟返回的章节信息
        paragraphs: 通义听悟返回的段落信息（包含说话人）
        transcription: 完整转写文本
        summary: 摘要
    
    Returns:
        要点列表
    """
    key_points = []
    
    # 策略1：如果有章节信息（推荐）
    if chapters:
        logger.info(f"使用章节信息提取要点: {len(chapters)}个章节")
        for chapter in chapters:
            # 章节可能包含以下字段（根据通义听悟返回格式）
            # StartTime, EndTime, Title, Summary, Text 等
            start_time = chapter.get('StartTime', chapter.get('start_time', 0))
            title = chapter.get('Title', chapter.get('title', '讨论要点'))
            chapter_summary = chapter.get('Summary', chapter.get('summary', ''))
            text = chapter.get('Text', chapter.get('text', ''))
            
            point = {
                "timestamp": _format_timestamp(start_time // 1000),  # 毫秒转秒
                "speaker": "多人",  # 章节通常包含多个发言人
                "topic": title,
                "content": chapter_summary if chapter_summary else (text[:200] if text else "")
            }
            key_points.append(point)
        
        logger.info(f"从{len(chapters)}个章节中提取了{len(key_points)}个要点")
        return key_points
    
    # 策略2：使用段落信息（说话人分离）
    if paragraphs:
        return _extract_key_points_from_paragraphs(paragraphs, transcription, summary)
    
    # 策略3：兜底方案
    return _extract_key_points_fallback(transcription, summary)


def _extract_key_points_from_paragraphs(
    paragraphs: List[Dict],
    transcription: str,
    summary: str
) -> List[Dict]:
    """
    从段落信息中提取会议要点（使用说话人分离结果）
    
    Args:
        paragraphs: 通义听悟返回的段落信息（包含说话人）
        transcription: 完整转写文本
        summary: 摘要
    
    Returns:
        要点列表
    """
    key_points = []
    
    # 如果有段落信息（说话人分离成功）
    if paragraphs:
        for para in paragraphs[:20]:  # 最多20个段落
            # 提取段落文本
            words = para.get('Words', [])
            if not words:
                continue
            
            # 拼接段落文本
            para_text = ''.join([w.get('Text', '') for w in words])
            if not para_text.strip():
                continue
            
            # 获取时间戳（使用第一个词的开始时间）
            start_time = words[0].get('Start', 0) if words else 0
            
            point = {
                "timestamp": _format_timestamp(start_time // 1000),  # 毫秒转秒
                "speaker": f"发言人{para.get('SpeakerId', '未知')}",
                "topic": para_text[:30] + "...",  # 用前30字作为主题
                "content": para_text[:200]  # 限制长度
            }
            key_points.append(point)
        
        logger.info(f"从{len(paragraphs)}个段落中提取了{len(key_points)}个要点")
        return key_points
    
    # 兜底：使用旧的逻辑
    return _extract_key_points_fallback(transcription, summary)


def _extract_key_points_fallback(
    transcription: str,
    summary: str
) -> List[Dict]:
    """
    兜底方案：从转写文本和摘要中提取要点
    """
    key_points = []
    
    # 如果有摘要，尝试从摘要中提取
    if summary:
        # 简单实现：将摘要分段
        paragraphs = summary.split('\n')
        for i, para in enumerate(paragraphs):
            if para.strip():
                point = {
                    "timestamp": f"{i:02d}:00:00",
                    "speaker": "会议内容",
                    "topic": f"要点 {i+1}",
                    "content": para.strip()
                }
                key_points.append(point)
    
    # 兜底：如果都没有，从转写文本中提取
    else:
        # 将文本分段（每500字一段）
        segments = [transcription[i:i+500] for i in range(0, len(transcription), 500)]
        for i, segment in enumerate(segments[:10]):  # 最多10个要点
            if segment.strip():
                point = {
                    "timestamp": f"{i:02d}:00:00",
                    "speaker": "会议内容",
                    "topic": f"讨论要点 {i+1}",
                    "content": segment.strip()[:200]
                }
                key_points.append(point)
    
    return key_points[:20]  # 最多返回20个要点


def _format_tingwu_actions(tingwu_actions: List[str]) -> List[Dict]:
    """
    格式化通义听悟返回的行动项
    """
    action_items = []
    for action_text in tingwu_actions[:15]:  # 最多15个
        action_item = {
            "content": action_text,
            "assignee": "待分配",
            "deadline": None,
            "priority": "medium",
            "status": "pending"
        }
        action_items.append(action_item)
    
    return action_items


def _extract_action_items(transcription: str, paragraphs: List[Dict]) -> List[Dict]:
    """
    识别行动项（Action Items）
    
    通过关键词和句式识别会议中的待办事项
    
    Returns:
        [
            {
                "content": "完成产品原型设计",
                "assignee": "张三",
                "deadline": "2025-11-15",
                "priority": "high"
            }
        ]
    """
    action_items = []
    
    # 行动项关键词
    action_keywords = [
        '需要', '要', '负责', '完成', '提交', '准备', '安排', 
        '跟进', '处理', '解决', '落实', '推进', '执行',
        '待办', 'TODO', 'Action', '行动项'
    ]
    
    # 人名关键词（简单实现）
    assignee_keywords = ['你', '我', '他', '她', '张', '李', '王', '刘', '陈', '杨', '赵', '黄', '周', '吴', '徐', '孙', '马', '朱', '胡', '郭', '何']
    
    # 时间关键词
    deadline_keywords = ['今天', '明天', '后天', '本周', '下周', '本月', '下月', '号', '日', '截止', '之前', '之内']
    
    # 按句子分割
    sentences = re.split(r'[。！？\n]', transcription)
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        # 检查是否包含行动关键词
        has_action = any(keyword in sentence for keyword in action_keywords)
        
        if has_action and len(sentence) > 10:  # 至少10个字
            # 提取行动项内容
            content = sentence[:100]  # 限制长度
            
            # 尝试识别负责人
            assignee = None
            for name_char in assignee_keywords:
                if name_char in sentence:
                    # 简单提取（实际应该用 NER 命名实体识别）
                    assignee = name_char + '**'  # 占位符
                    break
            
            # 尝试识别截止日期
            deadline = None
            for time_word in deadline_keywords:
                if time_word in sentence:
                    # 简单提取
                    deadline = '待确认'
                    break
            
            # 判断优先级（简单规则）
            priority = 'medium'
            if any(word in sentence for word in ['紧急', '重要', '优先', '尽快']):
                priority = 'high'
            elif any(word in sentence for word in ['可选', '建议', '考虑']):
                priority = 'low'
            
            action_item = {
                "content": content,
                "assignee": assignee or "待分配",
                "deadline": deadline,
                "priority": priority,
                "status": "pending"
            }
            
            action_items.append(action_item)
    
    # 去重并限制数量
    seen = set()
    unique_items = []
    for item in action_items:
        content_key = item['content'][:50]  # 用前50字判重
        if content_key not in seen:
            seen.add(content_key)
            unique_items.append(item)
    
    return unique_items[:15]  # 最多返回15个行动项


def _generate_simple_summary(transcription: str, key_points: List[Dict]) -> str:
    """
    生成简单摘要（当通义听悟没有返回摘要时的兜底方案）
    """
    if not transcription:
        return "会议内容处理中..."
    
    # 取前300字作为摘要
    summary = transcription[:300]
    
    if key_points:
        summary += f"\n\n会议共讨论了 {len(key_points)} 个要点。"
    
    return summary


def _format_timestamp(seconds: int) -> str:
    """
    格式化时间戳
    
    Args:
        seconds: 秒数
    
    Returns:
        "HH:MM:SS" 格式
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


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
            status_info['message'] = '正在转写和分析，请稍候...'
            status_info['progress'] = 50
        elif status_value == MeetingStatus.COMPLETED.value:
            status_info['message'] = '处理完成'
            status_info['progress'] = 100
        elif status_value == MeetingStatus.FAILED.value:
            status_info['message'] = '处理失败'
            status_info['error'] = '音频处理出错，请稍后重试'
        
        return status_info
        
    finally:
        db.close()


def _generate_tags(keywords: List[str], key_points: List[Dict], transcription: str) -> List[str]:
    """
    从关键词和要点中生成标签
    
    优先使用关键词，如果没有则从要点的topic中提取
    """
    tags = []
    
    # 1. 优先使用通义听悟的关键词（取前5个）
    if keywords:
        tags.extend(keywords[:5])
    
    # 2. 如果标签不足3个，从要点的topic补充
    if len(tags) < 3 and key_points:
        for point in key_points:
            topic = point.get('topic', '')
            if topic and topic not in tags:
                # 清理topic（去掉时间戳等）
                cleaned_topic = re.sub(r'\d+[:：]\d+', '', topic).strip()
                if cleaned_topic and len(cleaned_topic) <= 10:  # 只保留短标签
                    tags.append(cleaned_topic)
                    if len(tags) >= 5:
                        break
    
    # 3. 如果还是没有标签，尝试从转写文本中提取常见主题词
    if not tags and transcription:
        # 简单的主题词提取（可以后续优化为更智能的算法）
        common_topics = ['产品', '设计', '技术', '市场', '运营', '财务', '人事', '策略', '方案', '讨论']
        for topic in common_topics:
            if topic in transcription:
                tags.append(topic)
                if len(tags) >= 3:
                    break
    
    return tags[:5]  # 最多返回5个标签

