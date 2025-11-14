"""
数据库迁移脚本：移除 meetings 表的 conversational_summary 字段

版本: v0.9.5
日期: 2025-01-14
原因: AI 调度逻辑优化，通义听悟不再生成发言总结，统一由 LLM 生成
"""

import os
import sys
import urllib.parse
from loguru import logger

# SQLite 和 PostgreSQL 都需要支持
def run_migration():
    """
    执行数据库迁移

    支持 SQLite 和 PostgreSQL
    根据 DATABASE_URL 环境变量自动判断
    """
    database_url = os.getenv('DATABASE_URL')

    if not database_url:
        # 开发环境：使用 SQLite
        logger.info("未找到 DATABASE_URL，使用 SQLite 开发数据库")
        run_sqlite_migration()
    else:
        # 生产环境：解析 DATABASE_URL
        parsed = urllib.parse.urlparse(database_url)

        if parsed.scheme in ['postgres', 'postgresql']:
            logger.info("检测到 PostgreSQL 数据库")
            run_postgresql_migration(parsed)
        elif parsed.scheme == 'sqlite':
            logger.info("检测到 SQLite 数据库")
            run_sqlite_migration()
        else:
            logger.error(f"不支持的数据库类型: {parsed.scheme}")
            sys.exit(1)


def run_sqlite_migration():
    """SQLite 迁移"""
    import sqlite3

    # SQLite 数据库路径
    db_path = "app.db"

    if not os.path.exists(db_path):
        logger.warning(f"数据库文件不存在: {db_path}，跳过迁移")
        return

    conn = None
    cursor = None

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 检查字段是否存在
        cursor.execute("PRAGMA table_info(meetings)")
        columns = [row[1] for row in cursor.fetchall()]

        if 'conversational_summary' not in columns:
            logger.info("conversational_summary 字段不存在，无需迁移")
            return

        # SQLite 不支持直接 DROP COLUMN，需要重建表
        logger.info("开始迁移: 移除 conversational_summary 字段")

        # 1. 创建临时表（不包含 conversational_summary）
        cursor.execute("""
            CREATE TABLE meetings_new (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                folder_id INTEGER,
                title TEXT NOT NULL,
                participants TEXT,
                meeting_date TIMESTAMP,
                audio_url TEXT,
                audio_duration INTEGER,
                transcript TEXT,
                transcript_paragraphs TEXT,
                summary TEXT,
                mind_map TEXT,
                key_points TEXT,
                action_items TEXT,
                is_favorite BOOLEAN DEFAULT 0,
                tags TEXT,
                ai_model_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending',
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (folder_id) REFERENCES folders(id) ON DELETE SET NULL,
                FOREIGN KEY (ai_model_id) REFERENCES ai_models(id) ON DELETE SET NULL
            )
        """)

        # 2. 复制数据（排除 conversational_summary）
        cursor.execute("""
            INSERT INTO meetings_new (
                id, user_id, folder_id, title, participants, meeting_date,
                audio_url, audio_duration, transcript, transcript_paragraphs,
                summary, mind_map, key_points, action_items, is_favorite,
                tags, ai_model_id, created_at, status
            )
            SELECT
                id, user_id, folder_id, title, participants, meeting_date,
                audio_url, audio_duration, transcript, transcript_paragraphs,
                summary, mind_map, key_points, action_items, is_favorite,
                tags, ai_model_id, created_at, status
            FROM meetings
        """)

        # 3. 删除旧表
        cursor.execute("DROP TABLE meetings")

        # 4. 重命名新表
        cursor.execute("ALTER TABLE meetings_new RENAME TO meetings")

        conn.commit()
        logger.info("SQLite 迁移成功：conversational_summary 字段已移除")

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"SQLite 迁移失败: {e}")
        raise

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def run_postgresql_migration(parsed_url):
    """PostgreSQL 迁移"""
    import psycopg2

    conn = None
    cursor = None

    try:
        # 连接 PostgreSQL
        conn = psycopg2.connect(
            host=parsed_url.hostname,
            port=parsed_url.port or 5432,
            user=parsed_url.username,
            password=parsed_url.password,
            database=parsed_url.path.lstrip('/')
        )
        cursor = conn.cursor()

        # 检查字段是否存在
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'meetings' AND column_name = 'conversational_summary'
        """)

        if not cursor.fetchone():
            logger.info("conversational_summary 字段不存在，无需迁移")
            return

        # PostgreSQL 支持直接 DROP COLUMN
        logger.info("开始迁移: 移除 conversational_summary 字段")

        cursor.execute("""
            ALTER TABLE meetings DROP COLUMN IF EXISTS conversational_summary
        """)

        conn.commit()
        logger.info("PostgreSQL 迁移成功：conversational_summary 字段已移除")

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"PostgreSQL 迁移失败: {e}")
        raise

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("开始执行数据库迁移：移除 conversational_summary 字段")
    logger.info("=" * 60)

    try:
        run_migration()
        logger.info("迁移完成！")
    except Exception as e:
        logger.error(f"迁移失败: {e}")
        sys.exit(1)
