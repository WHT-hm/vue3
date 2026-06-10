"""学员认证路由"""
import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
import bcrypt

from app.database import get_db
from app.models import Student, User

router = APIRouter(prefix="/api/student", tags=["学员认证"])


class StudentRegisterRequest(BaseModel):
    name: str = Field(..., max_length=50, description="姓名")
    student_no: str = Field(..., max_length=50, description="学号")
    phone: str = Field(..., max_length=20, description="手机号")
    password: str = Field(..., min_length=6, max_length=50, description="密码")


class StudentLoginRequest(BaseModel):
    student_no: str = Field(..., description="学号")
    password: str = Field(..., description="密码")


class StudentInfoResponse(BaseModel):
    id: int
    name: str
    student_no: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    gender: str
    status: str

    class Config:
        from_attributes = True


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def get_current_student(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Student:
    if not authorization:
        raise HTTPException(status_code=401, detail="未提供认证令牌")
    token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
    student = db.query(Student).filter(Student.token == token).first()
    if not student:
        raise HTTPException(status_code=401, detail="认证令牌无效或已过期")
    if student.status != "active":
        raise HTTPException(status_code=403, detail="账号已被禁用")
    return student


@router.post("/register", summary="学员注册")
def register(data: StudentRegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(Student).filter(Student.student_no == data.student_no).first()
    if existing:
        raise HTTPException(status_code=400, detail="该学号已注册")
    existing_phone = db.query(Student).filter(Student.phone == data.phone).first()
    if existing_phone:
        raise HTTPException(status_code=400, detail="该手机号已注册")

    pwd_hash = hash_password(data.password)

    # 创建学员记录
    student = Student(
        name=data.name,
        student_no=data.student_no,
        phone=data.phone,
        password_hash=pwd_hash,
        gender="男",
        status="active",
    )
    db.add(student)

    # 同步创建 User 记录，使其在管理员用户列表可见
    existing_user = db.query(User).filter(User.username == data.student_no).first()
    if not existing_user:
        user = User(
            username=data.student_no,
            password_hash=pwd_hash,
            real_name=data.name,
            phone=data.phone,
            role="user",
            status="active",
        )
        db.add(user)

    db.commit()
    db.refresh(student)
    return {"code": 200, "message": "注册成功", "student_id": student.id}


@router.post("/login", summary="学员登录")
def login(data: StudentLoginRequest, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.student_no == data.student_no).first()
    if not student:
        raise HTTPException(status_code=401, detail="学号或密码错误")
    if not student.password_hash:
        raise HTTPException(status_code=401, detail="该账号未设置密码，请联系管理员")
    if not verify_password(data.password, student.password_hash):
        raise HTTPException(status_code=401, detail="学号或密码错误")
    if student.status != "active":
        raise HTTPException(status_code=403, detail="账号已被禁用")
    token = str(uuid.uuid4())
    student.token = token
    db.commit()
    db.refresh(student)
    return {
        "code": 200,
        "message": "登录成功",
        "token": token,
        "student": StudentInfoResponse.model_validate(student).model_dump(),
    }


@router.post("/logout", summary="学员登出")
def logout(student: Student = Depends(get_current_student), db: Session = Depends(get_db)):
    student.token = None
    db.commit()
    return {"code": 200, "message": "登出成功"}


@router.get("/me", summary="获取当前学员信息")
def get_me(student: Student = Depends(get_current_student)):
    return {"code": 200, "data": StudentInfoResponse.model_validate(student).model_dump()}
