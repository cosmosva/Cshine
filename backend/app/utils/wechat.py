"""
微信小程序工具
"""

import httpx
from loguru import logger
from config import settings


async def code2session(code: str) -> dict:
    """
    微信登录凭证校验
    使用 code 换取 openid 和 session_key
    
    Args:
        code: 微信登录凭证
        
    Returns:
        包含 openid 和 session_key 的字典
        
    Raises:
        Exception: 请求失败或返回错误
    """
    
    # 开发环境：如果未配置微信 AppID 或 Secret，使用 mock 模式
    # 检查是否为空、测试值或未配置
    is_dev_mode = (
        not settings.WECHAT_APPID or 
        settings.WECHAT_APPID == "" or 
        settings.WECHAT_APPID.startswith("test_") or
        not settings.WECHAT_SECRET or
        settings.WECHAT_SECRET == "" or
        settings.WECHAT_SECRET.startswith("test_")
    )
    
    if is_dev_mode:
        logger.warning("⚠️  使用 Mock 登录模式（开发测试）")
        # 使用 code 作为唯一标识生成 mock openid
        mock_openid = f"mock_openid_{hash(code) % 100000}"
        return {
            "openid": mock_openid,
            "session_key": "mock_session_key",
            "unionid": None
        }
    
    # 生产环境：调用真实的微信 API
    url = "https://api.weixin.qq.com/sns/jscode2session"
    params = {
        "appid": settings.WECHAT_APPID,
        "secret": settings.WECHAT_SECRET,
        "js_code": code,
        "grant_type": "authorization_code"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            data = response.json()
            
            if "errcode" in data and data["errcode"] != 0:
                error_msg = data.get("errmsg", "Unknown error")
                logger.error(f"WeChat code2session error: {error_msg}")
                raise Exception(f"微信登录失败: {error_msg}")
            
            return {
                "openid": data.get("openid"),
                "session_key": data.get("session_key"),
                "unionid": data.get("unionid")
            }
    
    except httpx.RequestError as e:
        logger.error(f"WeChat API request error: {e}")
        raise Exception(f"微信接口请求失败: {str(e)}")

