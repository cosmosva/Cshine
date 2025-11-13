"""
LLM 工厂
根据配置动态创建 LLM 实例
"""

from typing import Optional
from loguru import logger
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import AIModel, AIProvider
from .base import BaseLLM
from .openai_llm import OpenAILLM
from .anthropic_llm import AnthropicLLM
from .doubao_llm import DoubaoLLM
from .qwen_llm import QwenLLM


# LLM 提供商映射
LLM_PROVIDERS = {
    AIProvider.OPENAI: OpenAILLM,
    AIProvider.ANTHROPIC: AnthropicLLM,
    AIProvider.DOUBAO: DoubaoLLM,
    AIProvider.QWEN: QwenLLM,
}


def get_llm(model_id: Optional[str] = None, db: Optional[Session] = None) -> BaseLLM:
    """
    获取 LLM 实例
    
    Args:
        model_id: AI 模型 ID（数据库中的UUID），如果不传则使用默认模型
        db: 数据库会话（可选，如果不传会创建新会话）
    
    Returns:
        BaseLLM: LLM 实例
    
    Raises:
        ValueError: 模型不存在或未启用
        NotImplementedError: 不支持的提供商
    """
    should_close_db = False
    
    try:
        # 如果没有传入 db，创建新会话
        if db is None:
            db = SessionLocal()
            should_close_db = True
        
        # 查询模型配置
        if model_id:
            model = db.query(AIModel).filter(
                AIModel.id == model_id,
                AIModel.is_active == True
            ).first()
            
            if not model:
                raise ValueError(f"模型不存在或未启用: {model_id}")
        else:
            # 使用默认模型
            model = db.query(AIModel).filter(
                AIModel.is_default == True,
                AIModel.is_active == True
            ).first()
            
            if not model:
                raise ValueError("未配置默认 AI 模型，请在管理后台配置")
        
        # 获取对应的 LLM 类
        llm_class = LLM_PROVIDERS.get(model.provider)
        if not llm_class:
            raise NotImplementedError(f"不支持的提供商: {model.provider}")
        
        # 创建 LLM 实例
        logger.info(f"创建 LLM 实例: {model.name} ({model.provider} - {model.model_id})")
        
        return llm_class(
            model_id=model.model_id,
            api_key=model.api_key,
            api_base_url=model.api_base_url,
            max_tokens=model.max_tokens,
            temperature=model.temperature / 100.0,  # 数据库中存储的是 0-100，使用时转换为 0-1
        )
        
    except Exception as e:
        logger.error(f"创建 LLM 实例失败: {e}")
        raise
        
    finally:
        # 如果是自己创建的会话，需要关闭
        if should_close_db and db:
            db.close()


async def test_llm_connection(model_id: str, db: Optional[Session] = None) -> dict:
    """
    测试 LLM 连接
    
    Args:
        model_id: AI 模型 ID
        db: 数据库会话（可选）
    
    Returns:
        dict: {"success": bool, "message": str, "error": str}
    """
    try:
        llm = get_llm(model_id=model_id, db=db)
        success = await llm.test_connection()
        
        if success:
            return {
                "success": True,
                "message": "连接成功",
                "error": None
            }
        else:
            return {
                "success": False,
                "message": "连接失败",
                "error": "API 返回错误"
            }
            
    except Exception as e:
        return {
            "success": False,
            "message": "连接失败",
            "error": str(e)
        }


def get_available_models(db: Optional[Session] = None) -> list:
    """
    获取所有可用的 AI 模型列表
    
    Args:
        db: 数据库会话（可选）
    
    Returns:
        list: 模型列表
    """
    should_close_db = False
    
    try:
        if db is None:
            db = SessionLocal()
            should_close_db = True
        
        models = db.query(AIModel).filter(
            AIModel.is_active == True
        ).order_by(
            AIModel.is_default.desc(),  # 默认模型排在前面
            AIModel.created_at.desc()
        ).all()
        
        return [
            {
                "id": model.id,
                "name": model.name,
                "provider": model.provider.value,
                "model_id": model.model_id,
                "description": model.description,
                "is_default": model.is_default,
                "max_tokens": model.max_tokens,
                "temperature": model.temperature / 100.0,
            }
            for model in models
        ]
        
    finally:
        if should_close_db and db:
            db.close()

