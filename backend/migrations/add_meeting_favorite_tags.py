"""
数据库迁移脚本：为 meetings 表添加 is_favorite 和 tags 字段

运行方式：
cd backend && python migrations/add_meeting_favorite_tags.py
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from config import settings
from loguru import logger

def run_migration():
    """执行数据库迁移"""
    logger.info("开始数据库迁移：添加 is_favorite 和 tags 字段到 meetings 表")
    
    # 创建数据库引擎
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        with engine.connect() as connection:
            # 添加 is_favorite 字段
            try:
                connection.execute(text("ALTER TABLE meetings ADD COLUMN is_favorite BOOLEAN DEFAULT 0 NOT NULL"))
                logger.info("✅ 添加 is_favorite 字段成功")
            except Exception as e:
                logger.warning(f"字段 is_favorite 可能已存在: {e}")

            # 添加 tags 字段
            try:
                connection.execute(text("ALTER TABLE meetings ADD COLUMN tags TEXT"))
                logger.info("✅ 添加 tags 字段成功")
            except Exception as e:
                logger.warning(f"字段 tags 可能已存在: {e}")
            
            connection.commit()
        
        logger.info("✅ 数据库迁移完成！")
        
    except Exception as e:
        logger.error(f"❌ 数据库迁移失败: {e}")
        raise
    finally:
        engine.dispose()

if __name__ == "__main__":
    run_migration()

