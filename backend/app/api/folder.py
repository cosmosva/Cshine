"""
知识库（文件夹）管理 API
✨ 新增功能
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.dependencies import get_db, get_current_user
from app.models import User, Folder, Meeting
from app.schemas import FolderCreate, FolderUpdate, FolderResponse, FolderListResponse, ResponseModel

router = APIRouter(prefix="/folders", tags=["folders"])


@router.post("", response_model=ResponseModel)
async def create_folder(
    data: FolderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建知识库"""
    
    # 检查知识库名称是否已存在（同一用户下不能重名）
    existing = db.query(Folder).filter(
        Folder.user_id == current_user.id,
        Folder.name == data.name
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="知识库名称已存在")
    
    # 创建知识库
    folder = Folder(
        user_id=current_user.id,
        name=data.name
    )
    
    db.add(folder)
    db.commit()
    db.refresh(folder)
    
    # 返回响应
    response = FolderResponse(
        id=folder.id,
        name=folder.name,
        count=0,
        created_at=folder.created_at
    )
    
    return ResponseModel(
        code=200,
        message="知识库创建成功",
        data=response.dict()
    )


@router.get("", response_model=ResponseModel)
async def get_folders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取知识库列表（带会议数量统计）"""

    # 查询所有知识库，并关联统计会议数量
    folders_with_count = db.query(
        Folder,
        func.count(Meeting.id).label('meeting_count')
    ).outerjoin(
        Meeting,
        (Meeting.folder_id == Folder.id) & (Meeting.user_id == current_user.id)
    ).filter(
        Folder.user_id == current_user.id
    ).group_by(
        Folder.id
    ).order_by(
        Folder.created_at.desc()
    ).all()

    # 构建响应
    items = []
    for folder, count in folders_with_count:
        items.append(FolderResponse(
            id=folder.id,
            name=folder.name,
            count=count,
            created_at=folder.created_at
        ))

    # 统计未分类的会议数量（folder_id 为 NULL）
    uncategorized_count = db.query(func.count(Meeting.id)).filter(
        Meeting.user_id == current_user.id,
        Meeting.folder_id == None
    ).scalar() or 0

    response = FolderListResponse(items=items)

    return ResponseModel(
        code=200,
        message="success",
        data={
            **response.dict(),
            "total_count": uncategorized_count
        }
    )


@router.get("/{folder_id}", response_model=ResponseModel)
async def get_folder(
    folder_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取知识库详情"""
    
    # 查询知识库
    folder = db.query(Folder).filter(
        Folder.id == folder_id,
        Folder.user_id == current_user.id
    ).first()
    
    if not folder:
        raise HTTPException(status_code=404, detail="知识库不存在")
    
    # 统计会议数量
    count = db.query(func.count(Meeting.id)).filter(
        Meeting.folder_id == folder_id,
        Meeting.user_id == current_user.id
    ).scalar()
    
    response = FolderResponse(
        id=folder.id,
        name=folder.name,
        count=count or 0,
        created_at=folder.created_at
    )
    
    return ResponseModel(
        code=200,
        message="success",
        data=response.dict()
    )


@router.put("/{folder_id}", response_model=ResponseModel)
async def update_folder(
    folder_id: int,
    data: FolderUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新知识库"""
    
    # 查询知识库
    folder = db.query(Folder).filter(
        Folder.id == folder_id,
        Folder.user_id == current_user.id
    ).first()
    
    if not folder:
        raise HTTPException(status_code=404, detail="知识库不存在")
    
    # 检查新名称是否已存在（排除自己）
    existing = db.query(Folder).filter(
        Folder.user_id == current_user.id,
        Folder.name == data.name,
        Folder.id != folder_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="知识库名称已存在")
    
    # 更新
    folder.name = data.name
    db.commit()
    db.refresh(folder)
    
    # 统计会议数量
    count = db.query(func.count(Meeting.id)).filter(
        Meeting.folder_id == folder_id,
        Meeting.user_id == current_user.id
    ).scalar()
    
    response = FolderResponse(
        id=folder.id,
        name=folder.name,
        count=count or 0,
        created_at=folder.created_at
    )
    
    return ResponseModel(
        code=200,
        message="知识库更新成功",
        data=response.dict()
    )


@router.delete("/{folder_id}", response_model=ResponseModel)
async def delete_folder(
    folder_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除知识库（会将该知识库下的会议 folder_id 设置为 NULL）"""
    
    # 查询知识库
    folder = db.query(Folder).filter(
        Folder.id == folder_id,
        Folder.user_id == current_user.id
    ).first()
    
    if not folder:
        raise HTTPException(status_code=404, detail="知识库不存在")
    
    # 删除知识库（由于设置了 ondelete="SET NULL"，相关会议的 folder_id 会自动置空）
    db.delete(folder)
    db.commit()
    
    return ResponseModel(
        code=200,
        message="知识库删除成功",
        data=None
    )

