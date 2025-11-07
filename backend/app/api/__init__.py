"""
API 路由模块
"""

from fastapi import APIRouter
from app.api import auth, flash, upload, meeting

# 创建主路由
api_router = APIRouter()

# 注册子路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(flash.router, prefix="/flash", tags=["闪记"])
api_router.include_router(meeting.router, prefix="/meeting", tags=["会议纪要"])
api_router.include_router(upload.router, prefix="/upload", tags=["文件上传"])

