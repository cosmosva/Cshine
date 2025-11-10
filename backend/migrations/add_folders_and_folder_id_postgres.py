"""
数据库迁移脚本：添加 folders 表和 meetings 表的 folder_id 字段（PostgreSQL 版本）

运行方式：
cd backend && python migrations/add_folders_and_folder_id_postgres.py
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
    """执行数据库迁移（PostgreSQL）"""
    logger.info("开始数据库迁移：添加 folders 表和 meetings 表的 folder_id 字段（PostgreSQL）")
    
    # 创建数据库引擎
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        with engine.connect() as connection:
            # 开始事务
            trans = connection.begin()
            
            try:
                # 1. 创建 folders 表
                logger.info("创建 folders 表...")
                connection.execute(text("""
                    CREATE TABLE IF NOT EXISTS folders (
                        id SERIAL PRIMARY KEY,
                        user_id VARCHAR(36) NOT NULL,
                        name VARCHAR(50) NOT NULL,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    )
                """))
                logger.info("✅ 创建 folders 表成功")

                # 2. 创建索引
                logger.info("创建索引...")
                connection.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_folders_user_id ON folders(user_id)
                """))
                logger.info("✅ 创建 folders 表索引成功")

                # 3. 检查 folder_id 字段是否已存在
                logger.info("检查 meetings 表的 folder_id 字段...")
                result = connection.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='meetings' AND column_name='folder_id'
                """))
                
                if result.fetchone() is None:
                    # 字段不存在，添加它
                    logger.info("添加 folder_id 字段到 meetings 表...")
                    connection.execute(text("""
                        ALTER TABLE meetings ADD COLUMN folder_id INTEGER
                    """))
                    logger.info("✅ 添加 folder_id 字段成功")
                    
                    # 4. 添加外键约束
                    logger.info("添加外键约束...")
                    connection.execute(text("""
                        ALTER TABLE meetings 
                        ADD CONSTRAINT fk_meetings_folder_id 
                        FOREIGN KEY (folder_id) REFERENCES folders(id) ON DELETE SET NULL
                    """))
                    logger.info("✅ 添加外键约束成功")
                    
                    # 5. 创建索引
                    logger.info("创建 folder_id 索引...")
                    connection.execute(text("""
                        CREATE INDEX IF NOT EXISTS idx_meetings_folder_id ON meetings(folder_id)
                    """))
                    logger.info("✅ 创建索引成功")
                else:
                    logger.info("⚠️  folder_id 字段已存在，跳过添加")
                
                # 提交事务
                trans.commit()
                
                logger.info("=" * 60)
                logger.info("✅ 数据库迁移完成！")
                logger.info("=" * 60)
                logger.info("📝 变更摘要：")
                logger.info("   ✓ folders 表已创建")
                logger.info("     - id (SERIAL PRIMARY KEY)")
                logger.info("     - user_id (VARCHAR(36))")
                logger.info("     - name (VARCHAR(50))")
                logger.info("     - created_at (TIMESTAMP)")
                logger.info("     - updated_at (TIMESTAMP)")
                logger.info("   ✓ meetings 表已添加 folder_id 字段 (INTEGER)")
                logger.info("   ✓ 外键约束已创建")
                logger.info("   ✓ 索引已创建")
                logger.info("=" * 60)
                logger.info("🎉 现在可以使用知识库功能了！")
                
            except Exception as e:
                trans.rollback()
                logger.error(f"❌ 迁移过程中出错，已回滚: {e}")
                raise
                
    except Exception as e:
        logger.error(f"❌ 数据库迁移失败: {e}")
        raise
    finally:
        engine.dispose()

if __name__ == "__main__":
    run_migration()

