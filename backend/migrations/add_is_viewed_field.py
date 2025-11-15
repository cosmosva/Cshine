"""
添加 is_viewed 字段到 meetings 表
v0.9.10 功能：会议查看状态追踪

执行方式：
python backend/migrations/add_is_viewed_field.py
"""

import os
import sys
import sqlite3
from loguru import logger

# 添加 backend 目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
sys.path.insert(0, backend_dir)

from config import settings


def migrate_postgresql():
    """PostgreSQL 数据库迁移"""
    try:
        import psycopg2
        from urllib.parse import urlparse

        # 解析 DATABASE_URL
        db_url = settings.DATABASE_URL
        if not db_url:
            logger.error("未找到 DATABASE_URL 环境变量")
            return False

        # 解析连接参数
        parsed = urlparse(db_url)

        logger.info(f"连接到 PostgreSQL: {parsed.hostname}:{parsed.port}/{parsed.path[1:]}")

        # 连接数据库
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            user=parsed.username,
            password=parsed.password,
            database=parsed.path[1:]  # 移除开头的 /
        )

        cursor = conn.cursor()

        # 检查字段是否已存在
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name='meetings' AND column_name='is_viewed'
        """)

        if cursor.fetchone():
            logger.info("✅ is_viewed 字段已存在，跳过迁移")
            cursor.close()
            conn.close()
            return True

        # 添加 is_viewed 字段
        logger.info("开始添加 is_viewed 字段...")
        cursor.execute("""
            ALTER TABLE meetings
            ADD COLUMN is_viewed BOOLEAN DEFAULT FALSE NOT NULL
        """)

        conn.commit()

        # 验证字段是否添加成功
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name='meetings' AND column_name='is_viewed'
        """)

        result = cursor.fetchone()
        if result:
            logger.info(f"✅ is_viewed 字段添加成功: {result}")
        else:
            logger.error("❌ is_viewed 字段添加失败")
            cursor.close()
            conn.close()
            return False

        cursor.close()
        conn.close()

        logger.success("PostgreSQL 迁移完成")
        return True

    except Exception as e:
        logger.error(f"PostgreSQL 迁移失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def migrate_sqlite():
    """SQLite 数据库迁移"""
    conn = None
    cursor = None

    try:
        # 尝试多个可能的数据库路径
        possible_paths = [
            "backend/cshine.db",  # 从项目根目录运行
            "cshine.db",          # 从 backend 目录运行
            "app.db"              # 默认位置
        ]

        db_path = None
        for path in possible_paths:
            if os.path.exists(path):
                db_path = path
                logger.info(f"找到数据库文件: {db_path}")
                break

        if not db_path:
            logger.warning(f"数据库文件不存在: {', '.join(possible_paths)}，跳过迁移")
            return True

        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 检查字段是否已存在
        cursor.execute("PRAGMA table_info(meetings)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]

        if 'is_viewed' in column_names:
            logger.info("✅ is_viewed 字段已存在，跳过迁移")
            cursor.close()
            conn.close()
            return True

        # 添加 is_viewed 字段
        logger.info("开始添加 is_viewed 字段...")
        cursor.execute("""
            ALTER TABLE meetings
            ADD COLUMN is_viewed BOOLEAN DEFAULT 0 NOT NULL
        """)

        conn.commit()

        # 验证字段是否添加成功
        cursor.execute("PRAGMA table_info(meetings)")
        columns = cursor.fetchall()

        is_viewed_field = None
        for col in columns:
            if col[1] == 'is_viewed':
                is_viewed_field = col
                break

        if is_viewed_field:
            logger.info(f"✅ is_viewed 字段添加成功: {is_viewed_field}")
        else:
            logger.error("❌ is_viewed 字段添加失败")
            cursor.close()
            conn.close()
            return False

        cursor.close()
        conn.close()

        logger.success("SQLite 迁移完成")
        return True

    except Exception as e:
        logger.error(f"SQLite 迁移失败: {e}")
        import traceback
        traceback.print_exc()

        # 确保关闭连接
        if cursor:
            cursor.close()
        if conn:
            conn.close()

        return False


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("开始数据库迁移: 添加 is_viewed 字段")
    logger.info("=" * 60)

    # 判断使用哪个数据库
    if settings.DATABASE_URL and settings.DATABASE_URL.startswith('postgresql'):
        logger.info("检测到 PostgreSQL 数据库")
        success = migrate_postgresql()
    else:
        logger.info("检测到 SQLite 数据库")
        success = migrate_sqlite()

    if success:
        logger.success("✅ 数据库迁移成功")
        return 0
    else:
        logger.error("❌ 数据库迁移失败")
        return 1


if __name__ == "__main__":
    exit(main())
