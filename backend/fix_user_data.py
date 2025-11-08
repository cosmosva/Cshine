"""
数据库用户数据修复工具

当清除缓存后用户ID变化，使用此脚本快速转移数据到新用户
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from config import settings
from loguru import logger


def get_latest_user_id(engine):
    """获取最新创建的用户ID"""
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT id, openid, created_at FROM users ORDER BY created_at DESC LIMIT 1")
        )
        user = result.fetchone()
        if user:
            return user[0], user[1]
    return None, None


def get_all_users_with_data(engine):
    """获取所有有数据的用户"""
    with engine.connect() as connection:
        result = connection.execute(text("""
            SELECT 
                u.id,
                u.openid,
                u.created_at,
                (SELECT COUNT(*) FROM meetings WHERE user_id = u.id) as meeting_count,
                (SELECT COUNT(*) FROM flashes WHERE user_id = u.id) as flash_count
            FROM users u
            WHERE (SELECT COUNT(*) FROM meetings WHERE user_id = u.id) > 0
               OR (SELECT COUNT(*) FROM flashes WHERE user_id = u.id) > 0
            ORDER BY u.created_at DESC
        """))
        return result.fetchall()


def transfer_data(engine, from_user_id, to_user_id):
    """转移数据从一个用户到另一个用户"""
    with engine.connect() as connection:
        # 转移会议记录
        meetings_result = connection.execute(
            text("UPDATE meetings SET user_id = :to_id WHERE user_id = :from_id"),
            {"to_id": to_user_id, "from_id": from_user_id}
        )
        meetings_count = meetings_result.rowcount
        
        # 转移闪记
        flashes_result = connection.execute(
            text("UPDATE flashes SET user_id = :to_id WHERE user_id = :from_id"),
            {"to_id": to_user_id, "from_id": from_user_id}
        )
        flashes_count = flashes_result.rowcount
        
        connection.commit()
        
        return meetings_count, flashes_count


def main():
    """主函数"""
    engine = create_engine(settings.DATABASE_URL)
    
    print("\n" + "="*60)
    print("📊 Cshine 数据库用户数据修复工具")
    print("="*60 + "\n")
    
    # 获取最新用户
    latest_user_id, latest_openid = get_latest_user_id(engine)
    if not latest_user_id:
        print("❌ 错误：数据库中没有用户")
        return
    
    print(f"🆕 最新用户:")
    print(f"   ID: {latest_user_id}")
    print(f"   OpenID: {latest_openid}")
    print()
    
    # 获取所有有数据的用户
    users_with_data = get_all_users_with_data(engine)
    
    if len(users_with_data) == 0:
        print("✅ 没有需要转移的数据")
        return
    
    print(f"📁 发现 {len(users_with_data)} 个用户有数据:\n")
    
    for idx, user in enumerate(users_with_data, 1):
        user_id, openid, created_at, meeting_count, flash_count = user
        is_latest = user_id == latest_user_id
        
        status = "✅ 当前用户" if is_latest else "⚠️  旧用户"
        print(f"{idx}. {status}")
        print(f"   ID: {user_id[:8]}...")
        print(f"   会议: {meeting_count}条 | 闪记: {flash_count}条")
        print(f"   创建时间: {created_at}")
        print()
    
    # 如果最新用户没有数据，提示转移
    latest_has_data = any(u[0] == latest_user_id for u in users_with_data)
    
    if not latest_has_data and len(users_with_data) > 0:
        print("⚠️  最新用户没有数据，建议转移旧数据\n")
        
        # 自动模式：转移所有旧数据到最新用户
        if "--auto" in sys.argv:
            print("🔄 自动模式：转移所有数据到最新用户...\n")
            total_meetings = 0
            total_flashes = 0
            
            for user in users_with_data:
                user_id = user[0]
                if user_id != latest_user_id:
                    meetings, flashes = transfer_data(engine, user_id, latest_user_id)
                    total_meetings += meetings
                    total_flashes += flashes
                    print(f"✅ 从 {user_id[:8]}... 转移: {meetings}条会议, {flashes}条闪记")
            
            print(f"\n✅ 转移完成！总计: {total_meetings}条会议, {total_flashes}条闪记")
        else:
            print("💡 提示：运行 'python fix_user_data.py --auto' 自动转移所有数据")
            print("或者手动选择要转移的用户（输入序号）：")
            
            try:
                choice = input("\n请输入要转移的用户序号（按Enter跳过）: ").strip()
                if choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(users_with_data):
                        from_user = users_with_data[idx]
                        meetings, flashes = transfer_data(engine, from_user[0], latest_user_id)
                        print(f"\n✅ 转移完成: {meetings}条会议, {flashes}条闪记")
            except KeyboardInterrupt:
                print("\n\n❌ 操作已取消")
    else:
        print("✅ 数据分布正常，无需转移")
    
    print("\n" + "="*60 + "\n")
    engine.dispose()


if __name__ == "__main__":
    main()

