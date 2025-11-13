"""
数据库迁移脚本：添加 AI 模型管理系统表 (SQLite 版本)
- ai_models: AI模型配置表
- ai_prompts: 提示词模板表
- admin_users: 管理员用户表
- 为 meetings 和 flashes 表添加 ai_model_id 字段

运行方式：
    python backend/migrations/add_ai_models_and_prompts_sqlite.py
"""

import os
import sys
from pathlib import Path
import sqlite3
import uuid
import bcrypt

# 添加项目根目录到 Python 路径
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from loguru import logger
from config import settings


def hash_password(password: str) -> str:
    """使用 bcrypt 加密密码"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def run_migration():
    """执行数据库迁移"""
    conn = None
    cursor = None
    
    try:
        # 连接SQLite数据库
        db_path = settings.DATABASE_URL.replace('sqlite:///', '')
        logger.info(f"连接数据库: {db_path}")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        logger.info("开始执行数据库迁移...")
        
        # 1. 创建 ai_models 表
        logger.info("创建 ai_models 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_models (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                provider TEXT NOT NULL,
                model_id TEXT NOT NULL,
                api_key TEXT NOT NULL,
                api_base_url TEXT,
                max_tokens INTEGER DEFAULT 4096 NOT NULL,
                temperature INTEGER DEFAULT 70 NOT NULL,
                is_active INTEGER DEFAULT 1 NOT NULL,
                is_default INTEGER DEFAULT 0 NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 2. 创建 ai_prompts 表
        logger.info("创建 ai_prompts 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_prompts (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                scenario TEXT NOT NULL,
                prompt_template TEXT NOT NULL,
                variables TEXT,
                is_active INTEGER DEFAULT 1 NOT NULL,
                is_default INTEGER DEFAULT 0 NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 3. 创建 admin_users 表
        logger.info("创建 admin_users 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                is_active INTEGER DEFAULT 1 NOT NULL,
                is_superuser INTEGER DEFAULT 0 NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                last_login TIMESTAMP
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_admin_users_username ON admin_users(username)")
        
        # 4. 为 flashes 表添加 ai_model_id 字段
        logger.info("为 flashes 表添加 ai_model_id 字段...")
        try:
            cursor.execute("ALTER TABLE flashes ADD COLUMN ai_model_id TEXT")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                logger.info("ai_model_id 字段已存在，跳过")
            else:
                raise
        
        # 5. 为 meetings 表添加 ai_model_id 字段
        logger.info("为 meetings 表添加 ai_model_id 字段...")
        try:
            cursor.execute("ALTER TABLE meetings ADD COLUMN ai_model_id TEXT")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                logger.info("ai_model_id 字段已存在，跳过")
            else:
                raise
        
        # 6. 插入默认管理员账号（如果不存在）
        logger.info("创建默认管理员账号...")
        default_password = os.getenv("ADMIN_DEFAULT_PASSWORD", "admin123456")
        password_hash = hash_password(default_password)
        
        admin_id = str(uuid.uuid4())
        try:
            cursor.execute("""
                INSERT INTO admin_users (id, username, password_hash, is_active, is_superuser, created_at)
                VALUES (?, 'admin', ?, 1, 1, CURRENT_TIMESTAMP)
            """, (admin_id, password_hash))
        except sqlite3.IntegrityError:
            logger.info("管理员账号已存在，跳过")
        
        # 7. 插入默认 AI 模型（通义千问，使用环境变量中的配置）
        if settings.QWEN_API_KEY:
            logger.info("插入默认 AI 模型（通义千问）...")
            model_id = str(uuid.uuid4())
            try:
                cursor.execute("""
                    INSERT INTO ai_models (id, name, provider, model_id, api_key, api_base_url, max_tokens, temperature, is_active, is_default, description, created_at)
                    VALUES (?, '通义千问', 'qwen', ?, ?, 'https://dashscope.aliyuncs.com/compatible-mode/v1', 4096, 70, 1, 1, '阿里云通义千问大模型，适合中文场景', CURRENT_TIMESTAMP)
                """, (model_id, settings.QWEN_MODEL, settings.QWEN_API_KEY))
            except sqlite3.IntegrityError:
                logger.info("默认AI模型已存在，跳过")
        
        # 8. 插入默认提示词模板
        logger.info("插入默认提示词模板...")
        
        prompts = [
            {
                "id": str(uuid.uuid4()),
                "name": "会议摘要生成",
                "scenario": "meeting_summary",
                "prompt_template": """请根据以下会议转录内容，生成一份简洁的会议摘要。

会议转录：
{{transcript}}

要求：
1. 提取会议的主要议题和讨论要点
2. 总结达成的决议和结论
3. 突出重要的数据和事实
4. 使用简洁的语言，字数控制在200-300字

请直接输出摘要内容，不要添加额外的标题或说明。"""
            },
            {
                "id": str(uuid.uuid4()),
                "name": "闪记智能分类",
                "scenario": "flash_classify",
                "prompt_template": """请对以下文本进行分类，从以下类别中选择最合适的一个：工作、生活、学习、灵感、其他

文本内容：
{{content}}

请直接返回类别名称，不要添加任何解释。"""
            },
            {
                "id": str(uuid.uuid4()),
                "name": "行动项识别",
                "scenario": "action_extract",
                "prompt_template": """请从以下会议内容中提取所有的行动项（待办事项）。

会议内容：
{{content}}

要求：
1. 识别所有需要执行的任务
2. 提取责任人（如果有）
3. 提取截止日期（如果有）
4. 按照以下JSON格式输出：
[
  {
    "action": "任务描述",
    "assignee": "责任人",
    "deadline": "截止日期"
  }
]

如果没有找到行动项，返回空数组 []"""
            },
            {
                "id": str(uuid.uuid4()),
                "name": "关键要点提取",
                "scenario": "key_points",
                "prompt_template": """请从以下内容中提取3-5个关键要点。

内容：
{{content}}

要求：
1. 提取最重要的信息点
2. 每个要点用一句话概括
3. 按重要性排序
4. 使用简洁明了的语言

请以JSON数组格式输出：
["要点1", "要点2", "要点3"]"""
            }
        ]
        
        for prompt in prompts:
            try:
                cursor.execute("""
                    INSERT INTO ai_prompts (id, name, scenario, prompt_template, is_active, is_default, created_at)
                    VALUES (?, ?, ?, ?, 1, 1, CURRENT_TIMESTAMP)
                """, (prompt["id"], prompt["name"], prompt["scenario"], prompt["prompt_template"]))
            except sqlite3.IntegrityError:
                logger.info(f"提示词模板 '{prompt['name']}' 已存在，跳过")
        
        # 提交事务
        conn.commit()
        
        logger.success("✅ 数据库迁移完成！")
        logger.info(f"默认管理员账号: admin")
        logger.info(f"默认管理员密码: {default_password}")
        logger.warning("⚠️ 请尽快登录管理后台修改默认密码！")
        
        return True
        
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"❌ 数据库迁移失败: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("AI 模型管理系统 - 数据库迁移 (SQLite)")
    logger.info("=" * 60)
    
    success = run_migration()
    
    if success:
        logger.success("\n🎉 迁移成功！现在可以启动应用并访问管理后台了。")
        sys.exit(0)
    else:
        logger.error("\n❌ 迁移失败，请检查错误信息。")
        sys.exit(1)


if __name__ == "__main__":
    main()

