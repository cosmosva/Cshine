"""
Anthropic Claude LLM 适配器
支持 Claude 系列模型
"""

from typing import List, Optional
import httpx
from loguru import logger

from .base import BaseLLM, LLMMessage, LLMResponse


class AnthropicLLM(BaseLLM):
    """Anthropic Claude LLM 实现"""
    
    def __init__(
        self,
        model_id: str = "claude-3-sonnet-20240229",
        api_key: str = "",
        api_base_url: str = "https://api.anthropic.com",
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
        self.api_version = kwargs.get("api_version", "2023-06-01")
    
    async def complete(
        self,
        messages: List[LLMMessage],
        **kwargs
    ) -> LLMResponse:
        """
        调用 Anthropic Messages API
        
        参考文档: https://docs.anthropic.com/claude/reference/messages_post
        """
        try:
            # 提取 system 消息
            system_message = None
            user_messages = []
            
            for msg in messages:
                if msg.role == "system":
                    system_message = msg.content
                else:
                    user_messages.append({"role": msg.role, "content": msg.content})
            
            # 构建请求参数
            params = {
                "model": self.model_id,
                "messages": user_messages,
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "temperature": kwargs.get("temperature", self.temperature),
            }
            
            if system_message:
                params["system"] = system_message
            
            # 添加其他可选参数
            if "top_p" in kwargs:
                params["top_p"] = kwargs["top_p"]
            if "top_k" in kwargs:
                params["top_k"] = kwargs["top_k"]
            
            # 发送请求
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.api_base_url}/v1/messages",
                    headers={
                        "x-api-key": self.api_key,
                        "anthropic-version": self.api_version,
                        "Content-Type": "application/json"
                    },
                    json=params
                )
                response.raise_for_status()
                data = response.json()
            
            # 解析响应
            content_blocks = data.get("content", [])
            content = ""
            for block in content_blocks:
                if block["type"] == "text":
                    content += block["text"]
            
            usage = data.get("usage", {})
            
            return LLMResponse(
                content=content,
                model=data["model"],
                usage={
                    "prompt_tokens": usage.get("input_tokens", 0),
                    "completion_tokens": usage.get("output_tokens", 0),
                    "total_tokens": usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
                },
                finish_reason=data.get("stop_reason")
            )
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Anthropic API 请求失败: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Anthropic API 错误: {e.response.text}")
        except Exception as e:
            logger.error(f"Anthropic LLM 调用失败: {e}")
            raise
    
    async def test_connection(self) -> bool:
        """测试 Anthropic API 连接"""
        try:
            test_messages = [
                LLMMessage(role="user", content="Hello")
            ]
            
            await self.complete(test_messages, max_tokens=10)
            return True
            
        except Exception as e:
            logger.error(f"Anthropic 连接测试失败: {e}")
            return False

