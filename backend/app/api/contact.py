"""
联系人管理 API
用于管理常用联系人，支持会议说话人标注
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from loguru import logger

from app.database import get_db
from app.models import User, Contact
from app.dependencies import get_current_user
from app.schemas import (
    ContactCreate,
    ContactUpdate,
    ContactResponse,
    ContactListResponse,
    ResponseModel
)

router = APIRouter()


@router.post("/create", response_model=ResponseModel)
async def create_contact(
    contact_data: ContactCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建联系人
    """
    try:
        # 检查是否已存在同名联系人
        existing = db.query(Contact).filter(
            Contact.user_id == current_user.id,
            Contact.name == contact_data.name
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="该联系人已存在")
        
        # 创建联系人
        contact = Contact(
            user_id=current_user.id,
            name=contact_data.name,
            position=contact_data.position,
            phone=contact_data.phone,
            email=contact_data.email,
            avatar=contact_data.avatar
        )
        
        db.add(contact)
        db.commit()
        db.refresh(contact)
        
        logger.info(f"Contact created: {contact.id} by user {current_user.id}")
        
        return ResponseModel(
            code=200,
            message="联系人创建成功",
            data=ContactResponse.from_orm(contact)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Create contact error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list", response_model=ResponseModel)
async def get_contact_list(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取联系人列表
    """
    try:
        # 查询用户的所有联系人
        contacts = db.query(Contact).filter(
            Contact.user_id == current_user.id
        ).order_by(desc(Contact.created_at)).all()
        
        return ResponseModel(
            code=200,
            message="success",
            data=ContactListResponse(
                total=len(contacts),
                items=[ContactResponse.from_orm(c) for c in contacts]
            )
        )
    
    except Exception as e:
        logger.error(f"Get contact list error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{contact_id}", response_model=ResponseModel)
async def get_contact_detail(
    contact_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取联系人详情
    """
    contact = db.query(Contact).filter(
        Contact.id == contact_id,
        Contact.user_id == current_user.id
    ).first()
    
    if not contact:
        raise HTTPException(status_code=404, detail="联系人不存在")
    
    return ResponseModel(
        code=200,
        message="success",
        data=ContactResponse.from_orm(contact)
    )


@router.put("/{contact_id}", response_model=ResponseModel)
async def update_contact(
    contact_id: int,
    contact_data: ContactUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新联系人
    """
    contact = db.query(Contact).filter(
        Contact.id == contact_id,
        Contact.user_id == current_user.id
    ).first()
    
    if not contact:
        raise HTTPException(status_code=404, detail="联系人不存在")
    
    try:
        # 更新字段
        update_data = contact_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(contact, field, value)
        
        db.commit()
        db.refresh(contact)
        
        logger.info(f"Contact updated: {contact_id}")
        
        return ResponseModel(
            code=200,
            message="更新成功",
            data=ContactResponse.from_orm(contact)
        )
    
    except Exception as e:
        db.rollback()
        logger.error(f"Update contact error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{contact_id}", response_model=ResponseModel)
async def delete_contact(
    contact_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除联系人
    """
    contact = db.query(Contact).filter(
        Contact.id == contact_id,
        Contact.user_id == current_user.id
    ).first()
    
    if not contact:
        raise HTTPException(status_code=404, detail="联系人不存在")
    
    try:
        db.delete(contact)
        db.commit()
        
        logger.info(f"Contact deleted: {contact_id}")
        
        return ResponseModel(
            code=200,
            message="删除成功",
            data={"id": contact_id}
        )
    
    except Exception as e:
        db.rollback()
        logger.error(f"Delete contact error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

