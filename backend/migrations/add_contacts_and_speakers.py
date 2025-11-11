"""
数据库迁移：新增联系人和说话人映射表
版本：v0.5.10
日期：2025-11-11

变更内容：
1. 新增 contacts 表（常用联系人）
2. 新增 meeting_speakers 表（会议说话人映射）
3. meetings 表新增 transcript_paragraphs 字段
"""

import psycopg2
from loguru import logger
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings


def run_migration():
    """执行迁移"""
    try:
        # 连接数据库
        conn = psycopg2.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            database=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD
        )
        cursor = conn.cursor()
        
        logger.info("开始数据库迁移...")
        
        # 1. 创建 contacts 表
        logger.info("创建 contacts 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL,
                name VARCHAR(50) NOT NULL,
                position VARCHAR(50),
                phone VARCHAR(20),
                email VARCHAR(100),
                avatar VARCHAR(255),
                created_at TIMESTAMP DEFAULT NOW(),
                CONSTRAINT fk_contact_user FOREIGN KEY (user_id) 
                    REFERENCES users(id) ON DELETE CASCADE
            );
        """)
        logger.info("✅ contacts 表创建成功")
        
        # 2. 创建 meeting_speakers 表
        logger.info("创建 meeting_speakers 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS meeting_speakers (
                id SERIAL PRIMARY KEY,
                meeting_id VARCHAR(36) NOT NULL,
                speaker_id VARCHAR(20) NOT NULL,
                contact_id INTEGER,
                custom_name VARCHAR(50),
                created_at TIMESTAMP DEFAULT NOW(),
                CONSTRAINT fk_speaker_meeting FOREIGN KEY (meeting_id) 
                    REFERENCES meetings(id) ON DELETE CASCADE,
                CONSTRAINT fk_speaker_contact FOREIGN KEY (contact_id) 
                    REFERENCES contacts(id) ON DELETE SET NULL,
                CONSTRAINT unique_meeting_speaker UNIQUE(meeting_id, speaker_id)
            );
        """)
        logger.info("✅ meeting_speakers 表创建成功")
        
        # 3. 为 meetings 表添加 transcript_paragraphs 字段
        logger.info("为 meetings 表添加 transcript_paragraphs 字段...")
        cursor.execute("""
            DO $$ 
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='meetings' AND column_name='transcript_paragraphs'
                ) THEN
                    ALTER TABLE meetings ADD COLUMN transcript_paragraphs TEXT;
                END IF;
            END $$;
        """)
        logger.info("✅ transcript_paragraphs 字段添加成功")
        
        # 4. 创建索引
        logger.info("创建索引...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_contacts_user_id ON contacts(user_id);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_meeting_speakers_meeting_id ON meeting_speakers(meeting_id);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_meeting_speakers_contact_id ON meeting_speakers(contact_id);
        """)
        logger.info("✅ 索引创建成功")
        
        # 提交事务
        conn.commit()
        logger.info("✅ 数据库迁移完成！")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 数据库迁移失败: {e}")
        if conn:
            conn.rollback()
        raise
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def rollback_migration():
    """回滚迁移"""
    try:
        conn = psycopg2.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            database=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD
        )
        cursor = conn.cursor()
        
        logger.info("开始回滚迁移...")
        
        # 删除表（注意顺序，先删除有外键依赖的表）
        cursor.execute("DROP TABLE IF EXISTS meeting_speakers CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS contacts CASCADE;")
        
        # 删除字段
        cursor.execute("""
            ALTER TABLE meetings DROP COLUMN IF EXISTS transcript_paragraphs;
        """)
        
        conn.commit()
        logger.info("✅ 回滚完成")
        
    except Exception as e:
        logger.error(f"❌ 回滚失败: {e}")
        if conn:
            conn.rollback()
        raise
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        rollback_migration()
    else:
        run_migration()

