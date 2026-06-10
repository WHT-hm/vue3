"""统计仪表盘路由"""
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, case

from app.database import get_db
from app.models import Student, Exam, Score, ExamRegistration
from app.schemas import DashboardOverview, SubjectStats, StudentRanking

router = APIRouter(prefix="/api/dashboard", tags=["数据统计"])


@router.get("/overview", summary="仪表盘概览", response_model=DashboardOverview)
def get_overview(db: Session = Depends(get_db)):
    """获取系统整体统计概览"""
    total_students = db.query(func.count(Student.id)).scalar() or 0
    active_students = db.query(func.count(Student.id)).filter(
        Student.status == "active"
    ).scalar() or 0

    total_exams = db.query(func.count(Exam.id)).scalar() or 0
    upcoming_exams = db.query(func.count(Exam.id)).filter(
        Exam.status.in_(["upcoming", "ongoing"]),
        Exam.exam_date > datetime.now()
    ).scalar() or 0

    total_scores = db.query(func.count(Score.id)).scalar() or 0

    overall_avg = db.query(func.avg(Score.score)).scalar()
    overall_avg_score = round(overall_avg, 2) if overall_avg else None

    pass_count = db.query(func.count(Score.id)).filter(Score.passed == True).scalar() or 0
    overall_pass_rate = round(pass_count / total_scores * 100, 2) if total_scores > 0 else None

    return DashboardOverview(
        total_students=total_students,
        active_students=active_students,
        total_exams=total_exams,
        upcoming_exams=upcoming_exams,
        total_scores=total_scores,
        overall_pass_rate=overall_pass_rate,
        overall_avg_score=overall_avg_score,
    )


@router.get("/subject-stats", summary="科目统计")
def get_subject_stats(db: Session = Depends(get_db)):
    """获取各科目的统计数据"""
    stats = db.query(
        Exam.subject,
        func.count(func.distinct(Exam.id)).label("exam_count"),
        func.avg(Score.score).label("avg_score"),
        func.max(Score.score).label("highest"),
        func.min(Score.score).label("lowest"),
        func.count(Score.id).label("total"),
        func.sum(case((Score.passed == True, 1), else_=0)).label("pass_count"),
    ).join(Exam, Score.exam_id == Exam.id) \
        .group_by(Exam.subject) \
        .all()

    results = []
    for subject, exam_count, avg_score, highest, lowest, total, pass_count in stats:
        pass_rate = round(pass_count / total * 100, 2) if total > 0 else 0
        results.append(SubjectStats(
            subject=subject,
            exam_count=exam_count,
            avg_score=round(avg_score, 2) if avg_score else None,
            pass_rate=pass_rate,
            highest_score=round(highest, 2) if highest else None,
            lowest_score=round(lowest, 2) if lowest else None,
        ))

    return {"code": 200, "message": "success", "data": results}


@router.get("/score-distribution/{exam_id}", summary="考试成绩分布")
def get_exam_score_distribution(exam_id: int, db: Session = Depends(get_db)):
    """获取某次考试的成绩分布（分数段统计）"""
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="考试不存在")

    scores = db.query(Score.score).filter(Score.exam_id == exam_id).all()

    # 分数段
    ranges = {
        "0-59": 0,
        "60-69": 0,
        "70-79": 0,
        "80-89": 0,
        "90-100": 0,
    }

    for (score_val,) in scores:
        if score_val < 60:
            ranges["0-59"] += 1
        elif score_val < 70:
            ranges["60-69"] += 1
        elif score_val < 80:
            ranges["70-79"] += 1
        elif score_val < 90:
            ranges["80-89"] += 1
        else:
            ranges["90-100"] += 1

    return {
        "code": 200,
        "message": "success",
        "data": {
            "exam_name": exam.name,
            "subject": exam.subject,
            "total_participants": len(scores),
            "ranges": ranges,
        }
    }


@router.get("/student-ranking", summary="学员成绩排名")
def get_student_ranking(
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    db: Session = Depends(get_db)
):
    """获取学员综合成绩排名"""
    # 按学员分组统计平均分
    ranking_data = db.query(
        Score.student_id,
        func.avg(Score.score).label("avg_score"),
        func.count(Score.id).label("total_exams"),
        func.sum(case((Score.passed == True, 1), else_=0)).label("pass_count"),
    ).group_by(Score.student_id) \
        .order_by(func.avg(Score.score).desc()) \
        .limit(limit) \
        .all()

    results = []
    for student_id, avg_score, total_exams, pass_count in ranking_data:
        student = db.query(Student).filter(Student.id == student_id).first()
        if student:
            results.append(StudentRanking(
                student_id=student_id,
                student_name=student.name,
                school=student.school,
                avg_score=round(avg_score, 2),
                total_exams=total_exams,
                pass_count=pass_count,
            ))

    return {"code": 200, "message": "success", "data": results}


@router.get("/monthly-trend", summary="月度考试趋势")
def get_monthly_trend(db: Session = Depends(get_db)):
    """获取月度考试数量和通过率趋势"""
    # 使用SQLite的strftime函数
    monthly_data = db.query(
        func.strftime("%Y-%m", Exam.exam_date).label("month"),
        func.count(Exam.id).label("exam_count"),
    ).group_by(func.strftime("%Y-%m", Exam.exam_date)) \
        .order_by(func.strftime("%Y-%m", Exam.exam_date)) \
        .all()

    monthly_scores = db.query(
        func.strftime("%Y-%m", Exam.exam_date).label("month"),
        func.avg(Score.score).label("avg_score"),
        func.count(Score.id).label("total_scores"),
        func.sum(case((Score.passed == True, 1), else_=0)).label("pass_count"),
    ).join(Exam, Score.exam_id == Exam.id) \
        .group_by(func.strftime("%Y-%m", Exam.exam_date)) \
        .order_by(func.strftime("%Y-%m", Exam.exam_date)) \
        .all()

    score_map = {}
    for month, avg, total, passed in monthly_scores:
        score_map[month] = {
            "avg_score": round(avg, 2) if avg else 0,
            "pass_rate": round(passed / total * 100, 2) if total > 0 else 0,
        }

    results = []
    for month, exam_count, *_ in monthly_data:
        score_info = score_map.get(month, {"avg_score": 0, "pass_rate": 0})
        results.append({
            "month": month,
            "exam_count": exam_count,
            "avg_score": score_info["avg_score"],
            "pass_rate": score_info["pass_rate"],
        })

    return {"code": 200, "message": "success", "data": results}


@router.get("/recent-activities", summary="最近活动")
def get_recent_activities(
    limit: int = Query(10, ge=1, le=50, description="返回数量"),
    db: Session = Depends(get_db)
):
    """获取最近的系统活动（新增学员、考试、成绩录入等）"""
    activities = []

    # 最近的学员
    recent_students = db.query(Student).order_by(Student.created_at.desc()).limit(5).all()
    for s in recent_students:
        activities.append({
            "type": "student_created",
            "description": f"新学员 {s.name} 注册",
            "time": str(s.created_at),
        })

    # 最近的考试
    recent_exams = db.query(Exam).order_by(Exam.created_at.desc()).limit(5).all()
    for e in recent_exams:
        activities.append({
            "type": "exam_created",
            "description": f"新考试 {e.name} 已创建",
            "time": str(e.created_at),
        })

    # 最近的成绩
    recent_scores = db.query(Score).order_by(Score.created_at.desc()).limit(5).all()
    for s in recent_scores:
        student = db.query(Student).filter(Student.id == s.student_id).first()
        exam = db.query(Exam).filter(Exam.id == s.exam_id).first()
        activities.append({
            "type": "score_added",
            "description": f"{student.name if student else '未知'} 的 {exam.name if exam else '未知考试'} 成绩已录入: {s.score}分",
            "time": str(s.created_at),
        })

    # 按时间排序
    activities.sort(key=lambda x: x["time"], reverse=True)

    return {"code": 200, "message": "success", "data": activities[:limit]}
