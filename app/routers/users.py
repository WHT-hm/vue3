"""用户管理与认证路由"""
import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
import bcrypt

from app.database import get_db
from app.models import User, Student
from app.schemas import (
    LoginRequest, LoginResponse, UserCreate, UserUpdate,
    UserResponse, ChangePassword, ResetPassword, PaginatedResponse
)

router = APIRouter(prefix="/api", tags=["用户管理"])


def hash_password(password: str) -> str:
    """生成密码哈希"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """从 token 获取当前用户（依赖注入）"""
    if not authorization:
        raise HTTPException(status_code=401, detail="未提供认证令牌")

    # 支持 "Bearer xxx" 格式或直接传 token
    token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization

    user = db.query(User).filter(User.token == token).first()
    if not user:
        raise HTTPException(status_code=401, detail="认证令牌无效或已过期")

    if user.status == "disabled":
        raise HTTPException(status_code=403, detail="账号已被禁用")

    return user


def require_super_admin(user: User = Depends(get_current_user)) -> User:
    """要求超级管理员权限"""
    if user.role != "super_admin":
        raise HTTPException(status_code=403, detail="需要超级管理员权限")
    return user


# ==================== 认证接口 ====================

@router.post("/auth/login", summary="用户登录", response_model=LoginResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """用户登录，返回 token 和用户信息"""
    user = db.query(User).filter(User.username == login_data.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    if user.status == "disabled":
        raise HTTPException(status_code=403, detail="账号已被禁用，请联系超级管理员")

    # 生成 token 并更新登录时间
    user.token = str(uuid.uuid4())
    user.last_login = datetime.now()
    db.commit()
    db.refresh(user)

    return LoginResponse(
        token=user.token,
        user=UserResponse.model_validate(user)
    )


@router.post("/auth/logout", summary="用户登出")
def logout(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """用户登出，清除 token"""
    user.token = None
    db.commit()
    return {"code": 200, "message": "登出成功"}


@router.get("/auth/me", summary="获取当前用户信息", response_model=UserResponse)
def get_me(user: User = Depends(get_current_user)):
    """获取当前登录用户的信息"""
    return UserResponse.model_validate(user)


@router.put("/auth/change-password", summary="修改自己的密码")
def change_password(
    password_data: ChangePassword,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """修改当前用户密码"""
    if not verify_password(password_data.old_password, user.password_hash):
        raise HTTPException(status_code=400, detail="旧密码错误")

    user.password_hash = hash_password(password_data.new_password)
    db.commit()
    return {"code": 200, "message": "密码修改成功"}


# ==================== 用户管理接口（需要超级管理员权限） ====================

@router.get("/users", summary="获取用户列表", response_model=PaginatedResponse)
def get_users(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    role: Optional[str] = Query(None, description="角色筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    keyword: Optional[str] = Query(None, description="关键词搜索(用户名/姓名)"),
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """获取用户列表（需要超级管理员权限）"""
    query = db.query(User)

    if role:
        query = query.filter(User.role == role)
    if status:
        query = query.filter(User.status == status)
    if keyword:
        query = query.filter(
            (User.username.contains(keyword)) | (User.real_name.contains(keyword))
        )

    total = query.count()
    total_pages = (total + page_size - 1) // page_size

    users = query.order_by(User.created_at.desc()) \
        .offset((page - 1) * page_size) \
        .limit(page_size) \
        .all()

    items = [UserResponse.model_validate(u) for u in users]

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.post("/users", summary="创建用户", response_model=UserResponse)
def create_user(
    user_data: UserCreate,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """创建新用户（需要超级管理员权限）"""
    # 检查用户名是否已存在
    existing = db.query(User).filter(User.username == user_data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")

    pwd_hash = hash_password(user_data.password)
    user = User(
        username=user_data.username,
        password_hash=pwd_hash,
        real_name=user_data.real_name,
        phone=user_data.phone,
        student_no=user_data.student_no,
        role=user_data.role,
        status="active",
    )
    db.add(user)

    # 如果创建的是普通用户，同步创建 Student 记录，使其可以在学员端登录
    if user_data.role == "user":
        student_no_value = user_data.student_no or user_data.username
        existing_student = db.query(Student).filter(Student.student_no == student_no_value).first()
        if not existing_student:
            student = Student(
                student_no=student_no_value,
                password_hash=pwd_hash,
                name=user_data.real_name or user_data.username,
                phone=user_data.phone or "",
                gender="男",
                status="active",
            )
            db.add(student)

    db.commit()
    db.refresh(user)
    return UserResponse.model_validate(user)


@router.put("/users/{user_id}", summary="更新用户", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """更新用户信息（需要超级管理员权限）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 不允许修改自己的角色
    if user.id == current_user.id and user_data.role and user_data.role != current_user.role:
        raise HTTPException(status_code=400, detail="不能修改自己的角色")

    update_data = user_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return UserResponse.model_validate(user)


@router.delete("/users/{user_id}", summary="删除用户")
def delete_user(
    user_id: int,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """删除用户（需要超级管理员权限）"""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能删除自己")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    db.delete(user)
    db.commit()
    return {"code": 200, "message": "删除成功"}


@router.put("/users/{user_id}/reset-password", summary="重置用户密码")
def reset_password(
    user_id: int,
    password_data: ResetPassword,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """重置用户密码（需要超级管理员权限）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    user.password_hash = hash_password(password_data.new_password)
    # 重置密码后清除 token，强制重新登录
    user.token = None
    db.commit()
    return {"code": 200, "message": "密码重置成功"}


@router.put("/users/{user_id}/toggle-status", summary="切换用户状态")
def toggle_user_status(
    user_id: int,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """启用/禁用用户（需要超级管理员权限）"""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能禁用自己")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    user.status = "disabled" if user.status == "active" else "active"
    # 禁用时清除 token，强制重新登录
    if user.status == "disabled":
        user.token = None

    db.commit()
    return {
        "code": 200,
        "message": f"用户已{'禁用' if user.status == 'disabled' else '启用'}",
        "data": {"status": user.status}
    }
