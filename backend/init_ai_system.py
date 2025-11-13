#!/usr/bin/env python3
"""
AI 模型管理系统初始化脚本
用于快速初始化数据库和创建默认数据

运行方式：
    python backend/init_ai_system.py
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from loguru import logger
from config import settings


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("AI 模型管理系统 - 初始化")
    logger.info("=" * 60)
    
    # 检查数据库类型
    if "sqlite" in settings.DATABASE_URL.lower():
        logger.info("检测到 SQLite 数据库")
        logger.info("SQLite 数据库会自动创建表结构")
        logger.info("但需要手动运行迁移脚本来添加 AI 管理相关表")
        logger.info("")
        logger.info("请运行以下命令：")
        logger.info("  python backend/migrations/add_ai_models_and_prompts.py")
        
    elif "postgresql" in settings.DATABASE_URL.lower():
        logger.info("检测到 PostgreSQL 数据库")
        logger.info("请运行以下命令完成初始化：")
        logger.info("  python backend/migrations/add_ai_models_and_prompts.py")
        
    else:
        logger.warning(f"未知的数据库类型: {settings.DATABASE_URL}")
        logger.info("请手动运行迁移脚本")
    
    logger.info("")
    logger.info("=" * 60)
    logger.info("初始化完成后：")
    logger.info(f"1. 默认管理员账号: admin")
    logger.info(f"2. 默认管理员密码: {settings.ADMIN_DEFAULT_PASSWORD}")
    logger.info("3. 管理员登录接口: POST /api/v1/api/admin/login")
    logger.info("4. API 文档: http://localhost:8000/docs")
    logger.info("")
    logger.info("⚠️  请尽快登录后台修改默认密码！")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()

