"""成绩管理路由"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import Score, Student, Exam
from app.schemas import (
    ScoreCreate, ScoreUpdate, ScoreResponse,
    ScoreDetailResponse, PaginatedResponse
)

router = APIRouter(prefix="/api/scores", tags=["成绩管理"])


@router.get("", summary="获取成绩列表", response_model=PaginatedResponse)
def get_scores(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    student_id: Optional[int] = Query(None, description="学员ID筛选"),
    exam_id: Optional[int] = Query(None, description="考试ID筛选"),
    passed: Optional[bool] = Query(None, description="是否及格筛选"),
    min_score: Optional[float] = Query(None, description="最低分筛选"),
    max_score: Optional[float] = Query(None, description="最高分筛选"),
    db: Session = Depends(get_db)
):
    """分页获取成绩列表，支持多条件筛选"""
    query = db.query(Score)

    if student_id:
        query = query.filter(Score.student_id == student_id)
    if exam_id:
        query = query.filter(Score.exam_id == exam_id)
    if passed is not None:
        query = query.filter(Score.passed == passed)
    if min_score is not None:
        query = query.filter(Score.score >= min_score)
    if max_score is not None:
        query = query.filter(Score.score <= max_score)

    total = query.count()
    total_pages = (total + page_size - 1) // page_size

    scores = query.order_by(Score.created_at.desc()) \
        .offset((page - 1) * page_size) \
        .limit(page_size) \
        .all()

    items = []
    for s in scores:
        student = db.query(Student).filter(Student.id == s.student_id).first()
        exam = db.query(Exam).filter(Exam.id == s.exam_id).first()

        items.append(ScoreDetailResponse(
            id=s.id,
            student_id=s.student_id,
            exam_id=s.exam_id,
            score=s.score,
            passed=s.passed,
            rank=s.rank,
            remarks=s.remarks,
            created_at=s.created_at,
            updated_at=s.updated_at,
            student_name=student.name if student else None,
            exam_name=exam.name if exam else None,
            subject=exam.subject if exam else None,
        ))

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{score_id}", summary="获取成绩详情", response_model=ScoreDetailResponse)
def get_score(score_id: int, db: Session = Depends(get_db)):
    """根据ID获取成绩详情"""
    score = db.query(Score).filter(Score.id == score_id).first()
    if not score:
        raise HTTPException(status_code=404, detail="成绩记录不存在")

    student = db.query(Student).filter(Student.id == score.student_id).first()
    exam = db.query(Exam).filter(Exam.id == score.exam_id).first()

    return ScoreDetailResponse(
        id=score.id,
        student_id=score.student_id,
        exam_id=score.exam_id,
        score=score.score,
        passed=score.passed,
        rank=score.rank,
        remarks=score.remarks,
        created_at=score.created_at,
        updated_at=score.updated_at,
        student_name=student.name if student else None,
        exam_name=exam.name if exam else None,
        subject=exam.subject if exam else None,
    )


@router.post("", summary="录入成绩", response_model=ScoreResponse)
def create_score(score_data: ScoreCreate, db: Session = Depends(get_db)):
    """录入学员考试成绩"""
    # 验证学员存在
    student = db.query(Student).filter(Student.id == score_data.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学员不存在")

    # 验证考试存在
    exam = db.query(Exam).filter(Exam.id == score_data.exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="考试不存在")

    # 检查是否已有成绩
    existing = db.query(Score).filter(
        Score.student_id == score_data.student_id,
        Score.exam_id == score_data.exam_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="该学员此考试已有成绩记录")

    # 自动判断是否及格
    if score_data.passed is None:
        score_data.passed = score_data.score >= exam.pass_score

    score = Score(**score_data.model_dump())
    db.add(score)
    db.commit()
    db.refresh(score)
    return score


@router.post("/batch", summary="批量录入成绩")
def batch_create_scores(scores_data: list[ScoreCreate], db: Session = Depends(get_db)):
    """批量录入成绩"""
    results = []
    errors = []

    for i, score_data in enumerate(scores_data):
        try:
            student = db.query(Student).filter(Student.id == score_data.student_id).first()
            if not student:
                errors.append({"index": i, "error": f"学员ID {score_data.student_id} 不存在"})
                continue

            exam = db.query(Exam).filter(Exam.id == score_data.exam_id).first()
            if not exam:
                errors.append({"index": i, "error": f"考试ID {score_data.exam_id} 不存在"})
                continue

            existing = db.query(Score).filter(
                Score.student_id == score_data.student_id,
                Score.exam_id == score_data.exam_id
            ).first()
            if existing:
                errors.append({"index": i, "error": f"学员 {student.name} 此考试已有成绩"})
                continue

            if score_data.passed is None:
                score_data.passed = score_data.score >= exam.pass_score

            score = Score(**score_data.model_dump())
            db.add(score)
            results.append({"student_name": student.name, "score": score_data.score})
        except Exception as e:
            errors.append({"index": i, "error": str(e)})

    db.commit()
    return {
        "code": 200,
        "message": f"成功录入 {len(results)} 条，失败 {len(errors)} 条",
        "data": {"success": results, "errors": errors}
    }


@router.put("/{score_id}", summary="更新成绩", response_model=ScoreResponse)
def update_score(score_id: int, score_data: ScoreUpdate, db: Session = Depends(get_db)):
    """更新成绩信息"""
    score = db.query(Score).filter(Score.id == score_id).first()
    if not score:
        raise HTTPException(status_code=404, detail="成绩记录不存在")

    update_data = score_data.model_dump(exclude_unset=True)

    # 如果更新了分数，自动更新及格状态
    if "score" in update_data and update_data["score"] is not None:
        exam = db.query(Exam).filter(Exam.id == score.exam_id).first()
        if exam and "passed" not in update_data:
            update_data["passed"] = update_data["score"] >= exam.pass_score

    for key, value in update_data.items():
        setattr(score, key, value)

    db.commit()
    db.refresh(score)
    return score


@router.delete("/{score_id}", summary="删除成绩")
def delete_score(score_id: int, db: Session = Depends(get_db)):
    """删除成绩记录"""
    score = db.query(Score).filter(Score.id == score_id).first()
    if not score:
        raise HTTPException(status_code=404, detail="成绩记录不存在")

    db.delete(score)
    db.commit()
    return {"code": 200, "message": "删除成功"}



@router.get("/student/{student_id}/history", summary="获取学员成绩历史")
def get_student_score_history(student_id: int, db: Session = Depends(get_db)):
    """获取某学员的所有成绩历史"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学员不存在")

    scores = db.query(Score).filter(Score.student_id == student_id).all()

    items = []
    for s in scores:
        exam = db.query(Exam).filter(Exam.id == s.exam_id).first()
        items.append({
            "score_id": s.id,
            "exam_id": s.exam_id,
            "exam_name": exam.name if exam else None,
            "subject": exam.subject if exam else None,
            "exam_date": str(exam.exam_date) if exam else None,
            "score": s.score,
            "total_score": exam.total_score if exam else 100,
            "passed": s.passed,
            "rank": s.rank,
        })

    # 统计
    total_exams = len(items)
    avg_score = round(sum(s.score for s in scores) / total_exams, 2) if total_exams > 0 else 0
    pass_count = sum(1 for s in scores if s.passed)
    pass_rate = round(pass_count / total_exams * 100, 2) if total_exams > 0 else 0

    return {
        "code": 200,
        "message": "success",
        "data": {
            "student": {
                "id": student.id,
                "name": student.name,
                "school": student.school,
                "major": student.major,
            },
            "summary": {
                "total_exams": total_exams,
                "avg_score": avg_score,
                "pass_count": pass_count,
                "pass_rate": pass_rate,
            },
            "scores": items,
        }
    }
