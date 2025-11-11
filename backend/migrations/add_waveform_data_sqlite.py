"""
数据库迁移（SQLite版）：添加音频波形数据字段
为 meetings 表添加 waveform_data 字段，用于存储音频波形可视化数据
"""

import os
import sys
import sqlite3

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from loguru import logger


def migrate():
    """执行迁移"""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'cshine.db')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查字段是否已存在
        cursor.execute("PRAGMA table_info(meetings)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'waveform_data' in columns:
            logger.info("✅ waveform_data 字段已存在，跳过迁移")
            conn.close()
            return
        
        # 添加 waveform_data 字段
        logger.info("开始迁移：添加 waveform_data 字段...")
        cursor.execute("""
            ALTER TABLE meetings 
            ADD COLUMN waveform_data TEXT;
        """)
        
        conn.commit()
        conn.close()
        
        logger.info("✅ 迁移完成：waveform_data 字段已添加")
        
    except Exception as e:
        logger.error(f"❌ 迁移失败: {e}")
        raise


def rollback():
    """回滚迁移"""
    logger.warning("⚠️  SQLite 不支持 DROP COLUMN，无法回滚")
    logger.info("如需回滚，请手动重建数据库")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='音频波形数据字段迁移（SQLite）')
    parser.add_argument('--rollback', action='store_true', help='回滚迁移')
    args = parser.parse_args()
    
    if args.rollback:
        rollback()
    else:
        migrate()

