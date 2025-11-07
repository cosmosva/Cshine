"""
FastAPI 依赖项
"""

from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.utils.jwt import verify_token


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

