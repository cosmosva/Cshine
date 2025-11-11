"""
阿里云通义听悟服务
音频转写 + AI分析一站式解决方案
"""

import os
import time
from typing import Dict, List, Optional
from loguru import logger
from alibabacloud_tingwu20230930 import models as tingwu_models
from alibabacloud_tingwu20230930.client import Client as TingwuClient
from alibabacloud_tea_openapi import models as open_api_models
from config import settings


class TingwuService:
    """通义听悟服务"""
    
    def __init__(self):
        """初始化客户端"""
        self.app_key = settings.TINGWU_APP_KEY
        self.client = self._create_client()
        
    def _create_client(self) -> TingwuClient:
        """创建通义听悟客户端"""
        config = open_api_models.Config(
            access_key_id=settings.ALIBABA_CLOUD_ACCESS_KEY_ID,
            access_key_secret=settings.ALIBABA_CLOUD_ACCESS_KEY_SECRET,
        )
        # 设置服务地址
        config.endpoint = 'tingwu.cn-beijing.aliyuncs.com'
        return TingwuClient(config)
    
    def create_task(
        self, 
        file_url: str,
        source_language: str = "cn",
        enable_summarization: bool = True,
        summarization_types: List[str] = None,  # 新增：摘要类型
        enable_chapters: bool = False,
        enable_meeting_assistance: bool = True,
        enable_speaker_diarization: bool = False,
        speaker_count: int = 0
    ) -> Dict:
        """
        创建音频转写任务
        
        Args:
            file_url: 音频文件的 HTTP/HTTPS URL（需要公网可访问）
            source_language: 语种（cn=中文, en=英语, yue=粤语）
            enable_summarization: 是否开启智能摘要
            summarization_types: 摘要类型列表，可选：
                - 'Paragraph': 段落摘要
                - 'Conversational': 发言总结
                - 'MindMap': 思维导图
                - 'QuestionsAnswering': 问答总结
                默认 ['Paragraph', 'Conversational', 'MindMap']
            enable_chapters: 是否开启章节划分
            enable_meeting_assistance: 是否开启会议助手
            enable_speaker_diarization: 是否开启说话人分离
            speaker_count: 说话人数量（0=不定人数，2=2人，默认0）
        
        Returns:
            {
                "task_id": "任务ID",
                "status": "SUBMITTED"
            }
        """
        try:
            # 构建输入参数
            input_params = tingwu_models.CreateTaskRequestInput(
                file_url=file_url,
                source_language=source_language,
                format='text'
            )
            
            # 构建转写参数（包含说话人分离）
            transcription_params = tingwu_models.CreateTaskRequestParametersTranscription()
            
            # 如果开启说话人分离
            if enable_speaker_diarization:
                transcription_params.diarization_enabled = True
                # 创建说话人分离配置
                diarization = tingwu_models.CreateTaskRequestParametersTranscriptionDiarization()
                diarization.speaker_count = speaker_count
                transcription_params.diarization = diarization
                logger.info(f"已开启说话人分离: speaker_count={speaker_count}")
            
            # 构建参数配置
            parameters = tingwu_models.CreateTaskRequestParameters(
                transcription=transcription_params
            )
            
            # 如果开启智能摘要
            if enable_summarization:
                # 默认开启所有摘要类型
                if summarization_types is None:
                    summarization_types = ['Paragraph', 'Conversational', 'MindMap']
                
                summarization = tingwu_models.CreateTaskRequestParametersSummarization()
                summarization.types = summarization_types
                parameters.summarization = summarization
                logger.info(f"已开启智能摘要: {', '.join(summarization_types)}")
            
            # 如果开启会议助手
            if enable_meeting_assistance:
                meeting_assistance = tingwu_models.CreateTaskRequestParametersMeetingAssistance()
                meeting_assistance.types = ['Actions']  # 行动项识别
                parameters.meeting_assistance = meeting_assistance
                logger.info("已开启会议助手")
            
            # 如果开启章节划分
            if enable_chapters:
                auto_chapters = tingwu_models.CreateTaskRequestParametersAutoChapters()
                parameters.auto_chapters = auto_chapters
                logger.info("已开启章节划分")
            
            # 创建请求
            request = tingwu_models.CreateTaskRequest(
                app_key=self.app_key,
                type='offline',  # 离线转写任务
                input=input_params,
                parameters=parameters
            )
            
            # 打印请求参数（调试用）
            logger.info(f"📤 发送给通义听悟的参数:")
            logger.info(f"  - 转写: diarization_enabled={getattr(parameters.transcription, 'diarization_enabled', False)}")
            logger.info(f"  - 摘要: {getattr(parameters, 'summarization', None)}")
            logger.info(f"  - 会议助手: {getattr(parameters, 'meeting_assistance', None)}")
            logger.info(f"  - 章节: {getattr(parameters, 'auto_chapters', None)}")
            
            # 发送请求
            response = self.client.create_task(request)
            
            logger.info(f"通义听悟任务创建成功: {response.body.data.task_id}")
            
            return {
                "task_id": response.body.data.task_id,
                "status": response.body.data.task_status,
                "message": "任务提交成功"
            }
            
        except Exception as e:
            logger.error(f"创建通义听悟任务失败: {e}", exc_info=True)
            raise Exception(f"创建转写任务失败: {str(e)}")
    
    def get_task_status(self, task_id: str) -> Dict:
        """
        查询任务状态和结果
        
        Args:
            task_id: 任务ID
        
        Returns:
            {
                "status": "SUBMITTED/RUNNING/COMPLETED/FAILED",
                "progress": 0-100,
                "result": {...}  # 完成后的结果
            }
        """
        try:
            response = self.client.get_task_info(task_id)
            
            data = response.body.data
            status = data.task_status
            
            result = {
                "task_id": task_id,
                "status": status,
            }
            
            # 如果任务完成，解析结果（通义听悟返回 SUCCEEDED 或 COMPLETED）
            if status in ["SUCCEEDED", "COMPLETED"]:
                logger.info(f"任务 {task_id} 已完成，开始解析结果")
                result["result"] = self._parse_result(data)
            elif status == "FAILED":
                result["error_message"] = data.error_message if hasattr(data, 'error_message') else "任务失败"
            
            return result
            
        except Exception as e:
            logger.error(f"查询任务状态失败: {e}")
            raise Exception(f"查询任务失败: {str(e)}")
    
    def _parse_result(self, data) -> Dict:
        """
        解析转写结果
        
        Returns:
            {
                "transcription": "转写的完整文本",
                "summary": "智能摘要",
                "keywords": ["关键词1", "关键词2"],
                "chapters": [...],
                "paragraphs": [...],  # 段落信息（包含说话人）
                "key_sentences": [...]
            }
        """
        result = {}
        
        try:
            # 1. 获取转写文本和段落信息（result.transcription 就是URL）
            if hasattr(data, 'result') and hasattr(data.result, 'transcription') and data.result.transcription:
                # 需要下载转写文件
                import requests
                transcription_url = data.result.transcription  # 直接是URL字符串
                logger.info(f"下载转写文件: {transcription_url[:100]}...")
                transcription_data = requests.get(transcription_url).json()
                
                # 提取完整文本和段落信息（新格式：Transcription.Paragraphs.Words）
                if 'Transcription' in transcription_data:
                    text_parts = []
                    paragraphs = transcription_data['Transcription'].get('Paragraphs', [])
                    
                    # 保存段落信息（包含说话人）
                    result['paragraphs'] = paragraphs
                    
                    # 拼接完整文本
                    for para in paragraphs:
                        for word in para.get('Words', []):
                            if 'Text' in word:
                                text_parts.append(word['Text'])
                    result['transcription'] = ''.join(text_parts)
                    logger.info(f"✅ 转写文本提取成功，长度: {len(result['transcription'])}, 段落数: {len(paragraphs)}")
            
            # 2. 获取智能摘要（result.summarization 就是URL）
            logger.info(f"🔍 检查摘要字段: hasattr(data, 'result')={hasattr(data, 'result')}")
            if hasattr(data, 'result'):
                # 打印所有非空字段
                result_fields = {}
                for field in ['transcription', 'summarization', 'meeting_assistance', 'auto_chapters', 
                             'translation', 'ppt_extraction', 'text_polish', 'custom_prompt']:
                    value = getattr(data.result, field, None)
                    if value is not None:
                        result_fields[field] = str(value)[:100] if isinstance(value, str) else value
                logger.info(f"🔍 data.result 中非空的字段: {result_fields}")
                logger.info(f"🔍 summarization 值: {data.result.summarization}")
            
            if hasattr(data, 'result') and hasattr(data.result, 'summarization') and data.result.summarization:
                import requests
                summary_url = data.result.summarization  # 直接是URL字符串
                logger.info(f"下载摘要文件: {summary_url[:100]}...")
                summary_data = requests.get(summary_url).json()
                
                if 'Summarization' in summary_data:
                    summaries = summary_data['Summarization']
                    logger.info(f"📋 通义听悟返回的摘要类型: {[s.get('Type') for s in summaries]}")
                    
                    # 解析不同类型的摘要
                    for summary_item in summaries:
                        summary_type = summary_item.get('Type', '')
                        summary_content = summary_item.get('Summary', '')
                        
                        if summary_type == 'Paragraph':
                            # 段落摘要（默认摘要）
                            result['summary'] = summary_content
                            logger.info(f"✅ 已获取段落摘要，长度: {len(summary_content)}")
                        
                        elif summary_type == 'Conversational':
                            # 发言总结
                            result['conversational_summary'] = summary_content
                            logger.info(f"✅ 已获取发言总结，长度: {len(summary_content)}")
                        
                        elif summary_type == 'MindMap':
                            # 思维导图
                            result['mind_map'] = summary_content
                            logger.info(f"✅ 已获取思维导图，长度: {len(summary_content)}")
                        
                        elif summary_type == 'QuestionsAnswering':
                            # 问答总结
                            result['qa_summary'] = summary_content
                            logger.info(f"✅ 已获取问答总结，长度: {len(summary_content)}")
                    
                    logger.info(f"✅ 摘要解析完成，类型数: {len(summaries)}")
                else:
                    logger.warning("⚠️ 摘要数据中没有 Summarization 字段")
            
            # 3. 获取会议助手结果（关键句、行动项）
            if hasattr(data, 'result') and hasattr(data.result, 'meeting_assistance') and data.result.meeting_assistance:
                import requests
                meeting_url = data.result.meeting_assistance  # 直接是URL字符串
                meeting_data = requests.get(meeting_url).json()
                
                # 提取关键句作为关键词
                if 'KeySentences' in meeting_data:
                    result['key_sentences'] = [
                        item['Text'] for item in meeting_data['KeySentences'][:5]
                    ]
                
                # 提取行动项
                if 'Actions' in meeting_data:
                    result['actions'] = [
                        item['ActionItem'] for item in meeting_data['Actions'][:5]
                    ]
            
            # 4. 获取章节信息
            if hasattr(data, 'result') and hasattr(data.result, 'auto_chapters') and data.result.auto_chapters:
                import requests
                chapters_url = data.result.auto_chapters  # 直接是URL字符串
                chapters_data = requests.get(chapters_url).json()
                
                if 'AutoChapters' in chapters_data:
                    result['chapters'] = chapters_data['AutoChapters']
            
            logger.info(f"解析结果成功: 转写文本长度={len(result.get('transcription', ''))}")
            
        except Exception as e:
            logger.error(f"解析结果失败: {e}")
            # 即使解析失败也返回部分结果
        
        return result
    
    def wait_for_completion(
        self, 
        task_id: str, 
        max_wait_seconds: int = 3600,
        poll_interval: int = 5
    ) -> Dict:
        """
        等待任务完成（轮询）
        
        Args:
            task_id: 任务ID
            max_wait_seconds: 最大等待时间（秒）
            poll_interval: 轮询间隔（秒）
        
        Returns:
            任务结果
        """
        start_time = time.time()
        
        while True:
            # 检查超时
            if time.time() - start_time > max_wait_seconds:
                raise TimeoutError(f"任务超时: {task_id}")
            
            # 查询状态
            status_info = self.get_task_status(task_id)
            status = status_info['status']
            
            # 通义听悟返回 COMPLETED 或 SUCCEEDED
            if status in ["SUCCEEDED", "COMPLETED"]:
                logger.info(f"任务完成: {task_id}")
                return status_info
            elif status == "FAILED":
                error_msg = status_info.get('error_message', '未知错误')
                raise Exception(f"任务失败: {error_msg}")
            
            # 等待后继续轮询
            logger.info(f"任务处理中... status={status}")
            time.sleep(poll_interval)


# 创建全局实例
tingwu_service = TingwuService()

