"""
API 路由模块
"""

from fastapi import APIRouter
from app.api import auth, flash, upload, meeting, folder, contact, admin, ai_models, ai_prompts

# 创建主路由
api_router = APIRouter()

# 注册子路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(flash.router, prefix="/flash", tags=["闪记"])
api_router.include_router(meeting.router, prefix="/meeting", tags=["会议纪要"])
api_router.include_router(upload.router, prefix="/upload", tags=["文件上传"])
api_router.include_router(folder.router, tags=["知识库"])  # ✨新增
api_router.include_router(contact.router, prefix="/contacts", tags=["联系人"])  # ✨新增

# 管理员相关路由 ✨新增
api_router.include_router(admin.router)
api_router.include_router(ai_models.admin_router)
api_router.include_router(ai_prompts.router)

# 用户端 AI 模型路由 ✨新增
api_router.include_router(ai_models.user_router)


