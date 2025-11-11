"""
数据库迁移：添加音频波形数据字段
为 meetings 表添加 waveform_data 字段，用于存储音频波形可视化数据
"""

import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import text
from app.database import engine
from loguru import logger


def migrate():
    """执行迁移"""
    try:
        with engine.begin() as conn:
            # 检查字段是否已存在
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='meetings' 
                AND column_name='waveform_data'
            """))
            
            if result.fetchone():
                logger.info("✅ waveform_data 字段已存在，跳过迁移")
                return
            
            # 添加 waveform_data 字段
            logger.info("开始迁移：添加 waveform_data 字段...")
            conn.execute(text("""
                ALTER TABLE meetings 
                ADD COLUMN waveform_data TEXT;
            """))
            
            logger.info("✅ 迁移完成：waveform_data 字段已添加")
            
    except Exception as e:
        logger.error(f"❌ 迁移失败: {e}")
        raise


def rollback():
    """回滚迁移"""
    try:
        with engine.begin() as conn:
            logger.info("开始回滚：删除 waveform_data 字段...")
            conn.execute(text("""
                ALTER TABLE meetings 
                DROP COLUMN IF EXISTS waveform_data;
            """))
            
            logger.info("✅ 回滚完成：waveform_data 字段已删除")
            
    except Exception as e:
        logger.error(f"❌ 回滚失败: {e}")
        raise


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='音频波形数据字段迁移')
    parser.add_argument('--rollback', action='store_true', help='回滚迁移')
    args = parser.parse_args()
    
    if args.rollback:
        rollback()
    else:
        migrate()

