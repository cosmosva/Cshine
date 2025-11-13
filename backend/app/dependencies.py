"""
FastAPI 依赖项
"""

from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, AdminUser
from app.utils.jwt import verify_token
from datetime import datetime


async def get_current_user(
    authorization: str = Header(...),
    db: Session = Depends(get_db)
) -> User:
    """
    获取当前登录用户
    从 Authorization Header 中提取 Token 并验证
    
    Args:
        authorization: Authorization Header (格式: Bearer <token>)
        db: 数据库会话
        
    Returns:
        当前用户对象
        
    Raises:
        HTTPException: Token 无效或用户不存在
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # 提取 Token
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise credentials_exception
    except ValueError:
        raise credentials_exception
    
    # 验证 Token
    user_id = verify_token(token)
    if user_id is None:
        raise credentials_exception
    
    # 查询用户
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user


async def get_optional_user(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
) -> User | None:
    """
    获取当前用户（可选）
    如果没有提供 Token 或 Token 无效，返回 None
    
    Args:
        authorization: Authorization Header (可选)
        db: 数据库会话
        
    Returns:
        当前用户对象或 None
    """
    if not authorization:
        return None
    
    try:
        return await get_current_user(authorization, db)
    except HTTPException:
        return None


async def get_current_admin(
    authorization: str = Header(...),
    db: Session = Depends(get_db)
) -> AdminUser:
    """
    获取当前登录管理员
    从 Authorization Header 中提取 Token 并验证
    
    Args:
        authorization: Authorization Header (格式: Bearer <token>)
        db: 数据库会话
        
    Returns:
        当前管理员对象
        
    Raises:
        HTTPException: Token 无效或管理员不存在
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的管理员凭证",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # 提取 Token
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise credentials_exception
    except ValueError:
        raise credentials_exception
    
    # 验证 Token（token中存储的是admin_id）
    admin_id = verify_token(token)
    if admin_id is None:
        raise credentials_exception
    
    # 查询管理员
    admin = db.query(AdminUser).filter(AdminUser.id == admin_id).first()
    if admin is None:
        raise credentials_exception
    
    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="管理员账号已被禁用"
        )
    
    # 更新最后登录时间
    admin.last_login = datetime.utcnow()
    db.commit()
    
    return admin


async def get_current_superuser(
    admin: AdminUser = Depends(get_current_admin)
) -> AdminUser:
    """
    获取当前超级管理员
    
    Args:
        admin: 当前管理员
        
    Returns:
        超级管理员对象
        
    Raises:
        HTTPException: 不是超级管理员
    """
    if not admin.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要超级管理员权限"
        )
    
    return admin

