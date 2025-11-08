"""
认证相关 API
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from loguru import logger

from app.database import get_db
from app.models import User
from app.dependencies import get_current_user
from app.schemas import WeChatLoginRequest, LoginResponse, ResponseModel, UserResponse
from app.utils.jwt import create_access_token
from app.utils.wechat import code2session

router = APIRouter()


@router.post("/login", response_model=ResponseModel)
async def wechat_login(
    login_data: WeChatLoginRequest,
    db: Session = Depends(get_db)
):
    """
    微信小程序登录
    
    使用微信登录凭证(code)换取 openid，然后创建或更新用户信息
    """
    try:
        # 调用微信接口获取 openid
        wx_data = await code2session(login_data.code)
        openid = wx_data.get("openid")
        unionid = wx_data.get("unionid")
        
        if not openid:
            raise HTTPException(status_code=400, detail="Invalid WeChat code")
        
        # 查询用户是否已存在
        user = db.query(User).filter(User.openid == openid).first()
        is_new_user = user is None
        
        if is_new_user:
            # 创建新用户
            user = User(
                openid=openid,
                unionid=unionid,
                nickname=login_data.nickname,
                avatar=login_data.avatar,
                last_login=datetime.utcnow()
            )
            db.add(user)
            logger.info(f"New user created: {openid}")
        else:
            # 更新用户信息
            user.last_login = datetime.utcnow()
            if login_data.nickname:
                user.nickname = login_data.nickname
            if login_data.avatar:
                user.avatar = login_data.avatar
            if unionid:
                user.unionid = unionid
            logger.info(f"User logged in: {openid}")
        
        db.commit()
        db.refresh(user)
        
        # 生成 JWT Token
        access_token = create_access_token(data={"sub": user.id})
        
        return ResponseModel(
            code=200,
            message="登录成功",
            data=LoginResponse(
                token=access_token,
                user_id=user.id,
                is_new_user=is_new_user
            )
        )
    
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/me", response_model=ResponseModel)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    获取当前登录用户信息
    需要登录：通过 JWT Token 验证
    """
    return ResponseModel(
        code=200,
        message="success",
        data=UserResponse.from_orm(current_user)
    )

