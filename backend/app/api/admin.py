"""
管理员认证 API
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import bcrypt
from loguru import logger

from app.database import get_db
from app.models import AdminUser
from app.schemas import (
    AdminLoginRequest,
    AdminLoginResponse,
    AdminUserResponse,
    ResponseModel
)
from app.utils.jwt import create_access_token
from app.dependencies import get_current_admin, get_current_superuser

router = APIRouter(prefix="/admin", tags=["管理员"])


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


@router.post("/login", response_model=ResponseModel)
async def admin_login(
    request: AdminLoginRequest,
    db: Session = Depends(get_db)
):
    """
    管理员登录
    
    - **username**: 用户名
    - **password**: 密码
    """
    try:
        # 查询管理员
        admin = db.query(AdminUser).filter(
            AdminUser.username == request.username
        ).first()
        
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )
        
        # 验证密码
        if not verify_password(request.password, admin.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )
        
        # 检查账号状态
        if not admin.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="账号已被禁用"
            )
        
        # 生成 Token（存储 admin_id）
        token = create_access_token({"sub": admin.id})
        
        logger.info(f"管理员登录成功: {admin.username} (ID: {admin.id})")
        
        return ResponseModel(
            code=200,
            message="登录成功",
            data=AdminLoginResponse(
                token=token,
                admin_id=admin.id,
                username=admin.username,
                is_superuser=admin.is_superuser
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"管理员登录失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录失败"
        )


@router.get("/me", response_model=ResponseModel)
async def get_admin_info(
    admin: AdminUser = Depends(get_current_admin)
):
    """
    获取当前管理员信息
    """
    return ResponseModel(
        code=200,
        message="success",
        data=AdminUserResponse.from_orm(admin)
    )


@router.post("/logout", response_model=ResponseModel)
async def admin_logout(
    admin: AdminUser = Depends(get_current_admin)
):
    """
    管理员登出（客户端需要删除本地 Token）
    """
    logger.info(f"管理员登出: {admin.username}")
    
    return ResponseModel(
        code=200,
        message="登出成功"
    )

