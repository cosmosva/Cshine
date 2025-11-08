"""
数据库迁移：为 Meeting 表添加新的摘要类型字段

运行方式：
    python migrations/add_meeting_summary_types.py
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from config import settings


def run_migration():
    """执行数据库迁移"""
    # 创建数据库连接
    engine = create_engine(settings.DATABASE_URL)
    
    print("开始数据库迁移...")
    
    with engine.connect() as connection:
        # 检查字段是否已存在
        check_sql = text("""
            SELECT COUNT(*) as count
            FROM pragma_table_info('meetings')
            WHERE name IN ('conversational_summary', 'mind_map');
        """)
        result = connection.execute(check_sql).fetchone()
        
        if result[0] > 0:
            print(f"⚠️  字段已存在（{result[0]}/2），跳过迁移")
            return
        
        # 添加新字段
        print("添加 conversational_summary 字段...")
        connection.execute(text("""
            ALTER TABLE meetings
            ADD COLUMN conversational_summary TEXT;
        """))
        connection.commit()
        
        print("添加 mind_map 字段...")
        connection.execute(text("""
            ALTER TABLE meetings
            ADD COLUMN mind_map TEXT;
        """))
        connection.commit()
        
        print("✅ 数据库迁移完成！")
        print("   - 新增字段: conversational_summary (发言总结)")
        print("   - 新增字段: mind_map (思维导图)")


def rollback_migration():
    """回滚迁移（SQLite 不支持 DROP COLUMN，需要重建表）"""
    print("⚠️  SQLite 不支持直接删除列，如需回滚请手动操作")
    print("   建议：备份数据 -> 删除表 -> 重新创建")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='数据库迁移工具')
    parser.add_argument('--rollback', action='store_true', help='回滚迁移')
    args = parser.parse_args()
    
    try:
        if args.rollback:
            rollback_migration()
        else:
            run_migration()
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        sys.exit(1)

