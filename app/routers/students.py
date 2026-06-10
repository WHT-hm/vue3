"""学员管理路由"""
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.database import get_db
from app.models import Student, Score
from app.schemas import (
    StudentCreate, StudentUpdate, StudentResponse,
    StudentWithScores, PaginatedResponse
)

router = APIRouter(prefix="/api/students", tags=["学员管理"])


@router.get("", summary="获取学员列表", response_model=PaginatedResponse)
def get_students(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(None, description="搜索关键词(姓名/电话/身份证)"),
    status: Optional[str] = Query(None, description="状态筛选"),
    school: Optional[str] = Query(None, description="学校筛选"),
    db: Session = Depends(get_db)
):
    """分页获取学员列表，支持搜索和筛选"""
    query = db.query(Student)

    # 关键词搜索
    if keyword:
        query = query.filter(
            (Student.name.like(f"%{keyword}%")) |
            (Student.phone.like(f"%{keyword}%")) |
            (Student.id_card.like(f"%{keyword}%")) |
            (Student.email.like(f"%{keyword}%")) |
            (Student.student_no.like(f"%{keyword}%"))
        )

    # 状态筛选
    if status:
        query = query.filter(Student.status == status)

    # 学校筛选
    if school:
        query = query.filter(Student.school.like(f"%{school}%"))

    total = query.count()
    total_pages = (total + page_size - 1) // page_size

    students = query.order_by(Student.created_at.desc()) \
        .offset((page - 1) * page_size) \
        .limit(page_size) \
        .all()

    # 转换为响应格式，附加统计信息
    items = []
    for s in students:
        score_stats = db.query(
            func.count(Score.id).label("count"),
            func.avg(Score.score).label("avg"),
        ).filter(Score.student_id == s.id).first()

        pass_count = db.query(func.count(Score.id)).filter(
            Score.student_id == s.id,
            Score.passed == True
        ).scalar()

        score_count = score_stats.count or 0
        avg_score = round(score_stats.avg, 2) if score_stats.avg else None
        pass_rate = round(pass_count / score_count * 100, 2) if score_count > 0 else None

        items.append(StudentWithScores(
            id=s.id,
            name=s.name,
            gender=s.gender,
            age=s.age,
            phone=s.phone,
            email=s.email,
            id_card=s.id_card,
            school=s.school,
            major=s.major,
            enrollment_date=s.enrollment_date,
            status=s.status,
            remark=s.remark,
            student_no=s.student_no,
            password_hash=s.password_hash,
            created_at=s.created_at,
            updated_at=s.updated_at,
            score_count=score_count,
            avg_score=avg_score,
            pass_rate=pass_rate,
        ))

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{student_id}", summary="获取学员详情", response_model=StudentWithScores)
def get_student(student_id: int, db: Session = Depends(get_db)):
    """根据ID获取学员详情"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学员不存在")

    score_stats = db.query(
        func.count(Score.id).label("count"),
        func.avg(Score.score).label("avg"),
    ).filter(Score.student_id == student.id).first()

    pass_count = db.query(func.count(Score.id)).filter(
        Score.student_id == student.id,
        Score.passed == True
    ).scalar()

    score_count = score_stats.count or 0
    avg_score = round(score_stats.avg, 2) if score_stats.avg else None
    pass_rate = round(pass_count / score_count * 100, 2) if score_count > 0 else None

    return StudentWithScores(
        id=student.id,
        name=student.name,
        gender=student.gender,
        age=student.age,
        phone=student.phone,
        email=student.email,
        id_card=student.id_card,
        school=student.school,
        major=student.major,
        enrollment_date=student.enrollment_date,
        status=student.status,
        remark=student.remark,
        created_at=student.created_at,
        updated_at=student.updated_at,
        score_count=score_count,
        avg_score=avg_score,
        pass_rate=pass_rate,
    )


@router.post("", summary="创建学员", response_model=StudentResponse)
def create_student(student_data: StudentCreate, db: Session = Depends(get_db)):
    """创建新学员"""
    # 检查身份证号唯一性
    if student_data.id_card:
        existing = db.query(Student).filter(Student.id_card == student_data.id_card).first()
        if existing:
            raise HTTPException(status_code=400, detail="该身份证号已存在")

    student = Student(**student_data.model_dump())
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


@router.put("/{student_id}", summary="更新学员信息", response_model=StudentResponse)
def update_student(student_id: int, student_data: StudentUpdate, db: Session = Depends(get_db)):
    """更新学员信息"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学员不存在")

    # 检查身份证号唯一性
    if student_data.id_card and student_data.id_card != student.id_card:
        existing = db.query(Student).filter(Student.id_card == student_data.id_card).first()
        if existing:
            raise HTTPException(status_code=400, detail="该身份证号已存在")

    update_data = student_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(student, key, value)

    db.commit()
    db.refresh(student)
    return student


@router.delete("/{student_id}", summary="删除学员")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    """删除学员（同时删除相关成绩和报名）"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学员不存在")

    db.delete(student)
    db.commit()
    return {"code": 200, "message": "删除成功"}


@router.get("/export/all", summary="导出所有学员数据")
def export_students(db: Session = Depends(get_db)):
    """导出所有学员数据（用于导出功能）"""
    students = db.query(Student).order_by(Student.created_at.desc()).all()
    return {
        "code": 200,
        "message": "success",
        "data": [
            {
                "id": s.id,
                "name": s.name,
                "gender": s.gender,
                "age": s.age,
                "phone": s.phone,
                "email": s.email,
                "id_card": s.id_card,
                "school": s.school,
                "major": s.major,
                "enrollment_date": str(s.enrollment_date) if s.enrollment_date else None,
                "status": s.status,
                "remark": s.remark,
            }
            for s in students
        ]
    }
