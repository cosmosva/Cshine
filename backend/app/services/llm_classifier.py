"""
基于 LLM 的智能分类器
使用可配置的 AI 模型进行内容分类和关键词提取
"""

from typing import List, Optional
import json
from loguru import logger
from sqlalchemy.orm import Session

from app.services.llm import get_llm, LLMMessage
from app.models import AIPrompt, PromptScenario
from app.services.classifier import classifier as rule_classifier


class LLMClassifier:
    """基于 LLM 的分类器"""
    
    @classmethod
    async def classify(
        cls,
        text: str,
        model_id: Optional[str] = None,
        db: Optional[Session] = None
    ) -> str:
        """
        使用 LLM 对文本进行分类
        
        Args:
            text: 要分类的文本
            model_id: 使用的 AI 模型 ID（可选，不传则使用默认模型）
            db: 数据库会话（可选）
        
        Returns:
            分类标签：工作/生活/学习/灵感/其他
        """
        try:
            # 获取提示词模板
            prompt_template = cls._get_prompt_template(
                PromptScenario.flash_classify,
                db
            )
            
            # 替换变量
            prompt = prompt_template.replace('{{content}}', text[:1000])  # 限制长度
            
            # 获取 LLM 并调用
            llm = get_llm(model_id=model_id, db=db)
            response = await llm.chat(prompt=prompt)
            
            # 解析响应
            category = response.strip()
            
            # 验证分类是否有效
            valid_categories = ['工作', '生活', '学习', '灵感', '其他']
            if category in valid_categories:
                logger.info(f"LLM 分类成功: {category}")
                return category
            else:
                logger.warning(f"LLM 返回了无效的分类: {category}，使用规则分类")
                return rule_classifier.classify(text)
                
        except Exception as e:
            logger.error(f"LLM 分类失败: {e}，降级到规则分类")
            # 降级到规则分类器
            return rule_classifier.classify(text)
    
    @classmethod
    async def extract_keywords(
        cls,
        text: str,
        summary: Optional[str] = None,
        key_sentences: Optional[List[str]] = None,
        model_id: Optional[str] = None,
        db: Optional[Session] = None
    ) -> List[str]:
        """
        使用 LLM 提取关键词
        
        Args:
            text: 转写文本
            summary: 摘要（可选）
            key_sentences: 关键句列表（可选）
            model_id: 使用的 AI 模型 ID（可选）
            db: 数据库会话（可选）
        
        Returns:
            关键词列表（3-5个）
        """
        try:
            # 获取提示词模板
            prompt_template = cls._get_prompt_template(
                PromptScenario.key_points,
                db
            )
            
            # 准备内容（优先使用摘要，否则使用原文）
            content = summary if summary else text[:500]
            
            # 替换变量
            prompt = prompt_template.replace('{{content}}', content)
            
            # 获取 LLM 并调用
            llm = get_llm(model_id=model_id, db=db)
            response = await llm.chat(prompt=prompt)
            
            # 解析 JSON 响应
            try:
                keywords = json.loads(response.strip())
                if isinstance(keywords, list) and len(keywords) > 0:
                    logger.info(f"LLM 提取关键词成功: {keywords}")
                    return keywords[:5]  # 最多5个
            except json.JSONDecodeError:
                logger.warning(f"LLM 返回的不是有效的 JSON: {response}")
            
            # 如果解析失败，降级到规则提取
            return rule_classifier.extract_keywords(text, summary, key_sentences)
            
        except Exception as e:
            logger.error(f"LLM 关键词提取失败: {e}，降级到规则提取")
            # 降级到规则提取器
            return rule_classifier.extract_keywords(text, summary, key_sentences)
    
    @classmethod
    async def extract_action_items(
        cls,
        content: str,
        model_id: Optional[str] = None,
        db: Optional[Session] = None
    ) -> List[dict]:
        """
        使用 LLM 提取行动项
        
        Args:
            content: 会议内容
            model_id: 使用的 AI 模型 ID（可选）
            db: 数据库会话（可选）
        
        Returns:
            行动项列表
        """
        try:
            # 获取提示词模板
            prompt_template = cls._get_prompt_template(
                PromptScenario.action_extract,
                db
            )
            
            # 替换变量
            prompt = prompt_template.replace('{{content}}', content[:2000])
            
            # 获取 LLM 并调用
            llm = get_llm(model_id=model_id, db=db)
            response = await llm.chat(prompt=prompt)
            
            # 解析 JSON 响应
            try:
                action_items = json.loads(response.strip())
                if isinstance(action_items, list):
                    logger.info(f"LLM 提取行动项成功: {len(action_items)} 项")
                    return action_items
            except json.JSONDecodeError:
                logger.warning(f"LLM 返回的不是有效的 JSON: {response}")
            
            return []
            
        except Exception as e:
            logger.error(f"LLM 行动项提取失败: {e}")
            return []
    
    @classmethod
    async def generate_summary(
        cls,
        transcript: str,
        model_id: Optional[str] = None,
        db: Optional[Session] = None
    ) -> str:
        """
        使用 LLM 生成会议摘要
        
        Args:
            transcript: 会议转录文本
            model_id: 使用的 AI 模型 ID（可选）
            db: 数据库会话（可选）
        
        Returns:
            会议摘要
        """
        try:
            # 获取提示词模板
            prompt_template = cls._get_prompt_template(
                PromptScenario.meeting_summary,
                db
            )
            
            # 替换变量
            prompt = prompt_template.replace('{{transcript}}', transcript[:3000])
            
            # 获取 LLM 并调用
            llm = get_llm(model_id=model_id, db=db)
            response = await llm.chat(prompt=prompt)
            
            logger.info(f"LLM 生成摘要成功，长度: {len(response)}")
            return response.strip()
            
        except Exception as e:
            logger.error(f"LLM 摘要生成失败: {e}")
            # 返回截断的原文作为降级方案
            return transcript[:300] + "..."
    
    @classmethod
    def _get_prompt_template(
        cls,
        scenario: PromptScenario,
        db: Optional[Session] = None
    ) -> str:
        """
        获取指定场景的提示词模板
        
        Args:
            scenario: 使用场景
            db: 数据库会话（可选）
        
        Returns:
            提示词模板文本
        """
        should_close_db = False
        
        try:
            if db is None:
                from app.database import SessionLocal
                db = SessionLocal()
                should_close_db = True
            
            # 查询默认的提示词模板
            prompt = db.query(AIPrompt).filter(
                AIPrompt.scenario == scenario,
                AIPrompt.is_active == True,
                AIPrompt.is_default == True
            ).first()
            
            if prompt:
                return prompt.prompt_template
            
            # 如果没有找到，返回默认模板
            return cls._get_fallback_template(scenario)
            
        finally:
            if should_close_db and db:
                db.close()
    
    @classmethod
    def _get_fallback_template(cls, scenario: PromptScenario) -> str:
        """获取降级的默认模板"""
        templates = {
            PromptScenario.flash_classify: "请对以下文本进行分类，从以下类别中选择：工作、生活、学习、灵感、其他\n\n{{content}}\n\n只返回类别名称。",
            PromptScenario.key_points: "请从以下内容中提取3-5个关键词，以JSON数组格式返回：\n\n{{content}}",
            PromptScenario.action_extract: "请从以下内容中提取行动项，以JSON数组格式返回：\n\n{{content}}",
            PromptScenario.meeting_summary: "请总结以下会议内容：\n\n{{transcript}}",
        }
        return templates.get(scenario, "{{content}}")


# 创建全局实例
llm_classifier = LLMClassifier()

