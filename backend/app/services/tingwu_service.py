"""
阿里云通义听悟服务
音频转写 + AI分析一站式解决方案
"""

import os
import time
from typing import Dict, Optional
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
        enable_chapters: bool = True,
        enable_meeting_assistance: bool = True
    ) -> Dict:
        """
        创建音频转写任务
        
        Args:
            file_url: 音频文件的 HTTP/HTTPS URL（需要公网可访问）
            source_language: 语种（cn=中文, en=英语, yue=粤语）
            enable_summarization: 是否开启智能摘要
            enable_chapters: 是否开启章节划分
            enable_meeting_assistance: 是否开启会议助手
        
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
            
            # 构建参数配置（简化版，只使用基础功能）
            parameters = tingwu_models.CreateTaskRequestParameters(
                # 语音识别
                transcription=tingwu_models.CreateTaskRequestParametersTranscription()
            )
            
            # 创建请求
            request = tingwu_models.CreateTaskRequest(
                app_key=self.app_key,
                type='offline',  # 离线转写任务
                input=input_params,
                parameters=parameters
            )
            
            # 发送请求
            response = self.client.create_task(request)
            
            logger.info(f"通义听悟任务创建成功: {response.body.data.task_id}")
            
            return {
                "task_id": response.body.data.task_id,
                "status": response.body.data.task_status,
                "message": "任务提交成功"
            }
            
        except Exception as e:
            logger.error(f"创建通义听悟任务失败: {e}")
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
                "key_sentences": [...]
            }
        """
        result = {}
        
        try:
            # 1. 获取转写文本（result.transcription 就是URL）
            if hasattr(data, 'result') and hasattr(data.result, 'transcription') and data.result.transcription:
                # 需要下载转写文件
                import requests
                transcription_url = data.result.transcription  # 直接是URL字符串
                logger.info(f"下载转写文件: {transcription_url[:100]}...")
                transcription_data = requests.get(transcription_url).json()
                
                # 提取完整文本（新格式：Transcription.Paragraphs.Words）
                if 'Transcription' in transcription_data:
                    text_parts = []
                    paragraphs = transcription_data['Transcription'].get('Paragraphs', [])
                    for para in paragraphs:
                        for word in para.get('Words', []):
                            if 'Text' in word:
                                text_parts.append(word['Text'])
                    result['transcription'] = ''.join(text_parts)
                    logger.info(f"✅ 转写文本提取成功，长度: {len(result['transcription'])}")
            
            # 2. 获取智能摘要（result.summarization 就是URL）
            if hasattr(data, 'result') and hasattr(data.result, 'summarization') and data.result.summarization:
                import requests
                summary_url = data.result.summarization  # 直接是URL字符串
                logger.info(f"下载摘要文件: {summary_url[:100]}...")
                summary_data = requests.get(summary_url).json()
                
                if 'Summarization' in summary_data:
                    summaries = summary_data['Summarization']
                    if summaries and len(summaries) > 0:
                        result['summary'] = summaries[0].get('Summary', '')
            
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

