"""
数据库迁移脚本：添加 folders 表和 meetings 表的 folder_id 字段

运行方式：
cd backend && python migrations/add_folders_and_folder_id.py
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
    logger.info("开始数据库迁移：添加 folders 表和 meetings 表的 folder_id 字段")
    
    # 创建数据库引擎
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        with engine.connect() as connection:
            # 1. 创建 folders 表
            try:
                connection.execute(text("""
                    CREATE TABLE IF NOT EXISTS folders (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id VARCHAR(36) NOT NULL,
                        name VARCHAR(50) NOT NULL,
                        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    )
                """))
                logger.info("✅ 创建 folders 表成功")
            except Exception as e:
                logger.warning(f"表 folders 可能已存在: {e}")

            # 2. 创建索引
            try:
                connection.execute(text("CREATE INDEX IF NOT EXISTS idx_folders_user_id ON folders(user_id)"))
                logger.info("✅ 创建 folders 表索引成功")
            except Exception as e:
                logger.warning(f"索引可能已存在: {e}")

            # 3. 添加 folder_id 字段到 meetings 表
            try:
                connection.execute(text("ALTER TABLE meetings ADD COLUMN folder_id INTEGER"))
                logger.info("✅ 添加 folder_id 字段到 meetings 表成功")
            except Exception as e:
                logger.warning(f"字段 folder_id 可能已存在: {e}")
            
            # 4. 创建外键约束（SQLite 不支持 ALTER TABLE ADD FOREIGN KEY，需要重建表）
            # 这里我们不强制添加外键约束，保持简单
            # 如果需要，可以在应用层面进行约束
            
            connection.commit()
        
        logger.info("✅ 数据库迁移完成！")
        logger.info("📝 提示：")
        logger.info("   - folders 表已创建，包含 id, user_id, name, created_at, updated_at 字段")
        logger.info("   - meetings 表已添加 folder_id 字段")
        logger.info("   - 现在可以使用知识库功能了！")
        
    except Exception as e:
        logger.error(f"❌ 数据库迁移失败: {e}")
        raise
    finally:
        engine.dispose()

if __name__ == "__main__":
    run_migration()

