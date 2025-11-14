"""
LLM 会议总结服务
基于通义听悟的转录文本，使用 LLM 生成结构化的会议总结
"""

from typing import List, Optional, Dict, Any
import json
from loguru import logger
from sqlalchemy.orm import Session

from app.services.llm import get_llm
from app.models import AIPrompt, PromptScenario


class LLMSummaryService:
    """LLM 会议总结服务"""

    @classmethod
    async def generate_full_summary(
        cls,
        transcript: str,
        speakers_info: Optional[List[Dict]] = None,
        model_id: Optional[str] = None,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        基于转录文本生成完整的会议总结

        Args:
            transcript: 通义听悟转录的完整文本
            speakers_info: 说话人信息列表（可选）
            model_id: 使用的 AI 模型 ID（可选，不传则使用默认模型）
            db: 数据库会话（可选）

        Returns:
            包含以下字段的字典:
            - summary: 会议摘要文本
            - key_points: 关键要点列表 [{"title": "...", "content": "..."}]
            - action_items: 行动项列表 [{"task": "...", "assignee": "...", "deadline": "..."}]
            - tags: 标签列表 ["tag1", "tag2", ...]
            - mind_map: 思维导图 Markdown 文本
        """
        logger.info(f"开始生成 LLM 会议总结，转录文本长度: {len(transcript)}")

        result = {
            "summary": "",
            "key_points": [],
            "action_items": [],
            "tags": [],
            "mind_map": ""
        }

        try:
            # 1. 生成会议摘要
            result["summary"] = await cls._generate_summary(
                transcript,
                speakers_info,
                model_id,
                db
            )

            # 2. 提取关键要点
            result["key_points"] = await cls._extract_key_points(
                transcript,
                result["summary"],
                model_id,
                db
            )

            # 3. 提取行动项
            result["action_items"] = await cls._extract_action_items(
                transcript,
                model_id,
                db
            )

            # 4. 生成标签
            result["tags"] = await cls._generate_tags(
                transcript,
                result["summary"],
                result["key_points"],
                model_id,
                db
            )

            # 5. 生成思维导图
            result["mind_map"] = await cls._generate_mind_map(
                result["summary"],
                result["key_points"],
                model_id,
                db
            )

            logger.info(f"LLM 会议总结生成成功")
            return result

        except Exception as e:
            logger.error(f"LLM 会议总结生成失败: {e}", exc_info=True)
            # 返回部分结果，至少保证有基础摘要
            if not result["summary"]:
                result["summary"] = transcript[:300] + "..."
            return result

    @classmethod
    async def _generate_summary(
        cls,
        transcript: str,
        speakers_info: Optional[List[Dict]],
        model_id: Optional[str],
        db: Optional[Session]
    ) -> str:
        """
        生成会议摘要

        Args:
            transcript: 转录文本
            speakers_info: 说话人信息
            model_id: AI 模型 ID
            db: 数据库会话

        Returns:
            摘要文本（200-500字）
        """
        try:
            # 获取提示词模板
            prompt_template = cls._get_prompt_template(
                PromptScenario.meeting_summary,
                db
            )

            # 准备上下文
            context = f"会议转录:\n{transcript[:3000]}"

            # 如果有说话人信息，添加到上下文
            if speakers_info:
                speakers_str = "\n".join([
                    f"- {s.get('name', s.get('speaker_id'))}"
                    for s in speakers_info[:10]  # 最多10个说话人
                ])
                context = f"会议参与者:\n{speakers_str}\n\n{context}"

            # 替换变量
            prompt = prompt_template.replace('{{transcript}}', context)

            # 调用 LLM
            llm = get_llm(model_id=model_id, db=db)
            response = await llm.chat(prompt=prompt)

            summary = response.strip()
            logger.info(f"会议摘要生成成功，长度: {len(summary)}")
            return summary

        except Exception as e:
            logger.error(f"会议摘要生成失败: {e}")
            return transcript[:300] + "..."

    @classmethod
    async def _extract_key_points(
        cls,
        transcript: str,
        summary: str,
        model_id: Optional[str],
        db: Optional[Session]
    ) -> List[Dict[str, str]]:
        """
        提取会议关键要点

        Args:
            transcript: 转录文本
            summary: 会议摘要
            model_id: AI 模型 ID
            db: 数据库会话

        Returns:
            要点列表 [{"title": "要点标题", "content": "要点内容"}]
        """
        try:
            # 获取提示词模板
            prompt_template = cls._get_prompt_template(
                PromptScenario.key_points,
                db
            )

            # 准备内容（优先使用摘要+部分原文）
            content = f"会议摘要:\n{summary}\n\n会议转录（节选）:\n{transcript[:2000]}"

            # 替换变量
            prompt = prompt_template.replace('{{content}}', content)
            prompt += "\n\n请返回 JSON 数组格式: [{\"title\": \"要点标题\", \"content\": \"要点详细内容\"}]"

            # 调用 LLM
            llm = get_llm(model_id=model_id, db=db)
            response = await llm.chat(prompt=prompt)

            # 解析 JSON
            try:
                # 尝试提取 JSON 部分（处理可能的 markdown 代码块）
                response_text = response.strip()
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0]
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0]

                key_points = json.loads(response_text.strip())

                if isinstance(key_points, list) and len(key_points) > 0:
                    # 验证格式
                    valid_points = []
                    for point in key_points[:10]:  # 最多10个要点
                        if isinstance(point, dict) and "title" in point:
                            valid_points.append({
                                "title": point.get("title", ""),
                                "content": point.get("content", "")
                            })

                    logger.info(f"关键要点提取成功: {len(valid_points)} 个")
                    return valid_points

            except json.JSONDecodeError as e:
                logger.warning(f"关键要点 JSON 解析失败: {e}, response: {response[:200]}")

            # 降级方案：返回空列表
            return []

        except Exception as e:
            logger.error(f"关键要点提取失败: {e}")
            return []

    @classmethod
    async def _extract_action_items(
        cls,
        transcript: str,
        model_id: Optional[str],
        db: Optional[Session]
    ) -> List[Dict[str, str]]:
        """
        提取行动项

        Args:
            transcript: 转录文本
            model_id: AI 模型 ID
            db: 数据库会话

        Returns:
            行动项列表 [{"task": "任务", "assignee": "负责人", "deadline": "截止日期"}]
        """
        try:
            # 获取提示词模板
            prompt_template = cls._get_prompt_template(
                PromptScenario.action_extract,
                db
            )

            # 替换变量
            prompt = prompt_template.replace('{{content}}', transcript[:2000])
            prompt += "\n\n请返回 JSON 数组格式: [{\"task\": \"任务描述\", \"assignee\": \"负责人（如有）\", \"deadline\": \"截止日期（如有）\"}]"

            # 调用 LLM
            llm = get_llm(model_id=model_id, db=db)
            response = await llm.chat(prompt=prompt)

            # 解析 JSON
            try:
                # 提取 JSON 部分
                response_text = response.strip()
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0]
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0]

                action_items = json.loads(response_text.strip())

                if isinstance(action_items, list):
                    # 验证格式
                    valid_items = []
                    for item in action_items[:15]:  # 最多15个行动项
                        if isinstance(item, dict) and "task" in item:
                            valid_items.append({
                                "task": item.get("task", ""),
                                "assignee": item.get("assignee", ""),
                                "deadline": item.get("deadline", "")
                            })

                    logger.info(f"行动项提取成功: {len(valid_items)} 个")
                    return valid_items

            except json.JSONDecodeError as e:
                logger.warning(f"行动项 JSON 解析失败: {e}, response: {response[:200]}")

            return []

        except Exception as e:
            logger.error(f"行动项提取失败: {e}")
            return []

    @classmethod
    async def _generate_tags(
        cls,
        transcript: str,
        summary: str,
        key_points: List[Dict],
        model_id: Optional[str],
        db: Optional[Session]
    ) -> List[str]:
        """
        生成会议标签

        Args:
            transcript: 转录文本
            summary: 会议摘要
            key_points: 关键要点
            model_id: AI 模型 ID
            db: 数据库会话

        Returns:
            标签列表（3-5个）
        """
        try:
            # 构建简化的内容
            content_summary = f"会议摘要: {summary[:500]}\n\n"
            if key_points:
                points_text = "\n".join([
                    f"- {p.get('title', '')}"
                    for p in key_points[:5]
                ])
                content_summary += f"关键要点:\n{points_text}"

            # 简单的提示词
            prompt = f"""请为以下会议内容生成3-5个简洁的标签词，用于分类和检索。

{content_summary}

请返回 JSON 数组格式: ["标签1", "标签2", "标签3"]"""

            # 调用 LLM
            llm = get_llm(model_id=model_id, db=db)
            response = await llm.chat(prompt=prompt)

            # 解析 JSON
            try:
                response_text = response.strip()
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0]
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0]

                tags = json.loads(response_text.strip())

                if isinstance(tags, list) and len(tags) > 0:
                    # 清理和验证标签
                    valid_tags = [
                        str(tag).strip()
                        for tag in tags[:5]  # 最多5个
                        if tag and len(str(tag).strip()) > 0
                    ]
                    logger.info(f"标签生成成功: {valid_tags}")
                    return valid_tags

            except json.JSONDecodeError as e:
                logger.warning(f"标签 JSON 解析失败: {e}, response: {response[:200]}")

            return []

        except Exception as e:
            logger.error(f"标签生成失败: {e}")
            return []

    @classmethod
    async def _generate_mind_map(
        cls,
        summary: str,
        key_points: List[Dict],
        model_id: Optional[str],
        db: Optional[Session]
    ) -> str:
        """
        生成思维导图（Markdown 格式）

        Args:
            summary: 会议摘要
            key_points: 关键要点
            model_id: AI 模型 ID
            db: 数据库会话

        Returns:
            Markdown 格式的思维导图文本
        """
        try:
            # 准备内容
            content = f"会议摘要:\n{summary}\n\n"
            if key_points:
                points_text = "\n".join([
                    f"{i+1}. {p.get('title', '')}: {p.get('content', '')[:100]}"
                    for i, p in enumerate(key_points[:8])
                ])
                content += f"关键要点:\n{points_text}"

            # 提示词
            prompt = f"""请基于以下会议内容生成一个结构化的思维导图（Markdown 格式）。

{content}

要求：
1. 使用 Markdown 列表格式（- 或 1. 2. 3.）
2. 最多3层结构
3. 主题分支不超过5个
4. 每个分支下的子项不超过3个

示例格式：
# 会议主题

## 核心议题
- 议题1
  - 要点1-1
  - 要点1-2
- 议题2
  - 要点2-1

## 决策事项
- 决策1
- 决策2

## 后续行动
- 行动1
- 行动2
"""

            # 调用 LLM
            llm = get_llm(model_id=model_id, db=db)
            response = await llm.chat(prompt=prompt)

            mind_map = response.strip()
            logger.info(f"思维导图生成成功，长度: {len(mind_map)}")
            return mind_map

        except Exception as e:
            logger.error(f"思维导图生成失败: {e}")
            # 降级方案：基于要点生成简单的 Markdown
            if key_points:
                fallback_map = "# 会议要点\n\n"
                for i, point in enumerate(key_points[:5]):
                    fallback_map += f"## {point.get('title', f'要点{i+1}')}\n\n"
                    if point.get('content'):
                        fallback_map += f"{point['content']}\n\n"
                return fallback_map
            return "# 会议内容\n\n暂无思维导图"

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
            PromptScenario.meeting_summary: """请总结以下会议内容，要求：
1. 简洁明了，200-500字
2. 包含会议主要议题
3. 突出关键决策和结论

{{transcript}}""",

            PromptScenario.key_points: """请从以下内容中提取5-10个关键要点：

{{content}}

要求：
1. 每个要点包含标题和详细内容
2. 按重要性排序
3. 内容具体、可操作""",

            PromptScenario.action_extract: """请从以下会议内容中提取所有行动项：

{{content}}

要求：
1. 识别明确的待办事项
2. 提取负责人（如有）
3. 提取截止日期（如有）
4. 任务描述清晰明确""",
        }
        return templates.get(scenario, "{{content}}")


# 创建全局实例
llm_summary_service = LLMSummaryService()
