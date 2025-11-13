"""
字节豆包 LLM 适配器
支持字节跳动豆包大模型
"""

from typing import List, Optional
import httpx
from loguru import logger

from .base import BaseLLM, LLMMessage, LLMResponse


class DoubaoLLM(BaseLLM):
    """字节豆包 LLM 实现"""
    
    def __init__(
        self,
        model_id: str = "doubao-pro-32k",
        api_key: str = "",
        api_base_url: str = "https://ark.cn-beijing.volces.com/api/v3",
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs
    ):
        super().__init__(
            model_id=model_id,
            api_key=api_key,
            api_base_url=api_base_url,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )
    
    async def complete(
        self,
        messages: List[LLMMessage],
        **kwargs
    ) -> LLMResponse:
        """
        调用字节豆包 Chat API
        
        参考文档: https://www.volcengine.com/docs/82379/1099475
        豆包兼容 OpenAI 格式
        """
        try:
            # 合并参数
            params = {
                "model": self.model_id,
                "messages": self.format_messages(messages),
                "temperature": kwargs.get("temperature", self.temperature),
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            }
            
            # 添加其他可选参数
            if "top_p" in kwargs:
                params["top_p"] = kwargs["top_p"]
            if "frequency_penalty" in kwargs:
                params["frequency_penalty"] = kwargs["frequency_penalty"]
            if "presence_penalty" in kwargs:
                params["presence_penalty"] = kwargs["presence_penalty"]
            
            # 发送请求
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.api_base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=params
                )
                response.raise_for_status()
                data = response.json()
            
            # 解析响应
            choice = data["choices"][0]
            usage = data.get("usage", {})
            
            return LLMResponse(
                content=choice["message"]["content"],
                model=data.get("model", self.model_id),
                usage={
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0)
                },
                finish_reason=choice.get("finish_reason")
            )
            
        except httpx.HTTPStatusError as e:
            logger.error(f"豆包 API 请求失败: {e.response.status_code} - {e.response.text}")
            raise Exception(f"豆包 API 错误: {e.response.text}")
        except Exception as e:
            logger.error(f"豆包 LLM 调用失败: {e}")
            raise
    
    async def test_connection(self) -> bool:
        """测试豆包 API 连接"""
        try:
            test_messages = [
                LLMMessage(role="user", content="你好")
            ]
            
            await self.complete(test_messages, max_tokens=10)
            return True
            
        except Exception as e:
            logger.error(f"豆包连接测试失败: {e}")
            return False

