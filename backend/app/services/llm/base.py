"""
LLM 基类
定义统一的 LLM 调用接口
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from pydantic import BaseModel


class LLMMessage(BaseModel):
    """LLM 消息格式"""
    role: str  # system / user / assistant
    content: str


class LLMResponse(BaseModel):
    """LLM 响应格式"""
    content: str
    model: str
    usage: Optional[Dict[str, int]] = None  # {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150}
    finish_reason: Optional[str] = None  # stop / length / content_filter


class BaseLLM(ABC):
    """LLM 基类"""
    
    def __init__(
        self,
        model_id: str,
        api_key: str,
        api_base_url: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs
    ):
        """
        初始化 LLM
        
        Args:
            model_id: 模型标识符
            api_key: API 密钥
            api_base_url: API 基础URL（可选）
            max_tokens: 最大token数
            temperature: 温度参数（0-1）
            **kwargs: 其他参数
        """
        self.model_id = model_id
        self.api_key = api_key
        self.api_base_url = api_base_url
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.kwargs = kwargs
    
    @abstractmethod
    async def complete(
        self,
        messages: List[LLMMessage],
        **kwargs
    ) -> LLMResponse:
        """
        执行对话补全
        
        Args:
            messages: 消息列表
            **kwargs: 其他参数（如 temperature, max_tokens 等）
        
        Returns:
            LLMResponse: 响应结果
        """
        pass
    
    async def chat(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        简单的对话接口
        
        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词（可选）
            **kwargs: 其他参数
        
        Returns:
            str: AI 响应内容
        """
        messages = []
        
        if system_prompt:
            messages.append(LLMMessage(role="system", content=system_prompt))
        
        messages.append(LLMMessage(role="user", content=prompt))
        
        response = await self.complete(messages, **kwargs)
        return response.content
    
    def format_messages(self, messages: List[LLMMessage]) -> List[Dict[str, str]]:
        """
        将 LLMMessage 转换为字典格式
        
        Args:
            messages: 消息列表
        
        Returns:
            List[Dict]: 字典格式的消息列表
        """
        return [{"role": msg.role, "content": msg.content} for msg in messages]
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """
        测试 API 连接是否正常
        
        Returns:
            bool: 连接是否成功
        """
        pass

