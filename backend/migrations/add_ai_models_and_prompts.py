"""
数据库迁移脚本：添加 AI 模型管理系统表
- ai_models: AI模型配置表
- ai_prompts: 提示词模板表
- admin_users: 管理员用户表
- 为 meetings 和 flashes 表添加 ai_model_id 字段

运行方式：
    python backend/migrations/add_ai_models_and_prompts.py
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import psycopg2
from urllib.parse import urlparse
from loguru import logger
import bcrypt

# 导入配置
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
        # 解析数据库URL
        db_url = urlparse(settings.DATABASE_URL)
        
        logger.info(f"连接数据库: {db_url.hostname}:{db_url.port or 5432}")
        
        # 连接数据库
        conn = psycopg2.connect(
            host=db_url.hostname,
            port=db_url.port or 5432,
            database=db_url.path.lstrip('/'),
            user=db_url.username,
            password=db_url.password
        )
        cursor = conn.cursor()
        
        logger.info("开始执行数据库迁移...")
        
        # 1. 创建 ai_models 表
        logger.info("创建 ai_models 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_models (
                id VARCHAR(36) PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                provider VARCHAR(20) NOT NULL,
                model_id VARCHAR(100) NOT NULL,
                api_key TEXT NOT NULL,
                api_base_url VARCHAR(255),
                max_tokens INTEGER DEFAULT 4096 NOT NULL,
                temperature INTEGER DEFAULT 70 NOT NULL,
                is_active BOOLEAN DEFAULT TRUE NOT NULL,
                is_default BOOLEAN DEFAULT FALSE NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # 2. 创建 ai_prompts 表
        logger.info("创建 ai_prompts 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_prompts (
                id VARCHAR(36) PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                scenario VARCHAR(50) NOT NULL,
                prompt_template TEXT NOT NULL,
                variables TEXT,
                is_active BOOLEAN DEFAULT TRUE NOT NULL,
                is_default BOOLEAN DEFAULT FALSE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # 3. 创建 admin_users 表
        logger.info("创建 admin_users 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_users (
                id VARCHAR(36) PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                email VARCHAR(100),
                is_active BOOLEAN DEFAULT TRUE NOT NULL,
                is_superuser BOOLEAN DEFAULT FALSE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                last_login TIMESTAMP
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_admin_users_username ON admin_users(username);")
        
        # 4. 为 flashes 表添加 ai_model_id 字段
        logger.info("为 flashes 表添加 ai_model_id 字段...")
        cursor.execute("""
            DO $$ 
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'flashes' AND column_name = 'ai_model_id'
                ) THEN
                    ALTER TABLE flashes ADD COLUMN ai_model_id VARCHAR(36);
                    ALTER TABLE flashes ADD CONSTRAINT fk_flashes_ai_model 
                        FOREIGN KEY (ai_model_id) REFERENCES ai_models(id) ON DELETE SET NULL;
                END IF;
            END $$;
        """)
        
        # 5. 为 meetings 表添加 ai_model_id 字段
        logger.info("为 meetings 表添加 ai_model_id 字段...")
        cursor.execute("""
            DO $$ 
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'meetings' AND column_name = 'ai_model_id'
                ) THEN
                    ALTER TABLE meetings ADD COLUMN ai_model_id VARCHAR(36);
                    ALTER TABLE meetings ADD CONSTRAINT fk_meetings_ai_model 
                        FOREIGN KEY (ai_model_id) REFERENCES ai_models(id) ON DELETE SET NULL;
                END IF;
            END $$;
        """)
        
        # 6. 插入默认管理员账号（如果不存在）
        logger.info("创建默认管理员账号...")
        default_password = os.getenv("ADMIN_DEFAULT_PASSWORD", "admin123456")
        password_hash = hash_password(default_password)
        
        cursor.execute("""
            INSERT INTO admin_users (id, username, password_hash, is_active, is_superuser, created_at)
            VALUES (gen_random_uuid()::text, 'admin', %s, TRUE, TRUE, CURRENT_TIMESTAMP)
            ON CONFLICT (username) DO NOTHING;
        """, (password_hash,))
        
        # 7. 插入默认 AI 模型（通义千问，使用环境变量中的配置）
        if settings.QWEN_API_KEY:
            logger.info("插入默认 AI 模型（通义千问）...")
            cursor.execute("""
                INSERT INTO ai_models (id, name, provider, model_id, api_key, api_base_url, max_tokens, temperature, is_active, is_default, description, created_at)
                VALUES (
                    gen_random_uuid()::text,
                    '通义千问',
                    'qwen',
                    %s,
                    %s,
                    'https://dashscope.aliyuncs.com/compatible-mode/v1',
                    4096,
                    70,
                    TRUE,
                    TRUE,
                    '阿里云通义千问大模型，适合中文场景',
                    CURRENT_TIMESTAMP
                )
                ON CONFLICT DO NOTHING;
            """, (settings.QWEN_MODEL, settings.QWEN_API_KEY))
        
        # 8. 插入默认提示词模板
        logger.info("插入默认提示词模板...")
        
        # 会议摘要提示词
        cursor.execute("""
            INSERT INTO ai_prompts (id, name, scenario, prompt_template, is_active, is_default, created_at)
            VALUES (
                gen_random_uuid()::text,
                '会议摘要生成',
                'meeting_summary',
                '请根据以下会议转录内容，生成一份简洁的会议摘要。

会议转录：
{{transcript}}

要求：
1. 提取会议的主要议题和讨论要点
2. 总结达成的决议和结论
3. 突出重要的数据和事实
4. 使用简洁的语言，字数控制在200-300字

请直接输出摘要内容，不要添加额外的标题或说明。',
                TRUE,
                TRUE,
                CURRENT_TIMESTAMP
            )
            ON CONFLICT DO NOTHING;
        """)
        
        # 闪记分类提示词
        cursor.execute("""
            INSERT INTO ai_prompts (id, name, scenario, prompt_template, is_active, is_default, created_at)
            VALUES (
                gen_random_uuid()::text,
                '闪记智能分类',
                'flash_classify',
                '请对以下文本进行分类，从以下类别中选择最合适的一个：工作、生活、学习、灵感、其他

文本内容：
{{content}}

请直接返回类别名称，不要添加任何解释。',
                TRUE,
                TRUE,
                CURRENT_TIMESTAMP
            )
            ON CONFLICT DO NOTHING;
        """)
        
        # 行动项提取提示词
        cursor.execute("""
            INSERT INTO ai_prompts (id, name, scenario, prompt_template, is_active, is_default, created_at)
            VALUES (
                gen_random_uuid()::text,
                '行动项识别',
                'action_extract',
                '请从以下会议内容中提取所有的行动项（待办事项）。

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

如果没有找到行动项，返回空数组 []',
                TRUE,
                TRUE,
                CURRENT_TIMESTAMP
            )
            ON CONFLICT DO NOTHING;
        """)
        
        # 关键要点提取提示词
        cursor.execute("""
            INSERT INTO ai_prompts (id, name, scenario, prompt_template, is_active, is_default, created_at)
            VALUES (
                gen_random_uuid()::text,
                '关键要点提取',
                'key_points',
                '请从以下内容中提取3-5个关键要点。

内容：
{{content}}

要求：
1. 提取最重要的信息点
2. 每个要点用一句话概括
3. 按重要性排序
4. 使用简洁明了的语言

请以JSON数组格式输出：
["要点1", "要点2", "要点3"]',
                TRUE,
                TRUE,
                CURRENT_TIMESTAMP
            )
            ON CONFLICT DO NOTHING;
        """)
        
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
    logger.info("AI 模型管理系统 - 数据库迁移")
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

