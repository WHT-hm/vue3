"""学员考试路由"""
import json
import re
import subprocess
import sys
import tempfile
import os
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional

from app.database import get_db
from app.models import Student, Exam, Question, Score, ExamAnswer, ExamRegistration
from app.routers.student_auth import get_current_student
from app.websocket_manager import manager as ws_manager

router = APIRouter(prefix="/api/student", tags=["学员考试"])


@router.websocket("/exams/{exam_id}/ws")
async def exam_websocket(websocket: WebSocket, exam_id: int):
    """学生端 WebSocket 连接，用于实时接收考试状态变更通知"""
    await ws_manager.connect(exam_id, websocket)
    try:
        while True:
            # 保持连接，等待客户端消息（心跳）
            data = await websocket.receive_text()
            # 如果收到 ping，回复 pong
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(exam_id, websocket)
    except Exception:
        ws_manager.disconnect(exam_id, websocket)


def _detect_language(subject: str) -> str:
    """根据考试科目检测编程语言"""
    s = (subject or "").lower().strip()
    if "c++" in s or "cpp" in s:
        return "cpp"
    if "java" in s:
        return "java"
    if "c语言" in s or s == "c" or (s.startswith("c") and not "c#" in s and len(s) <= 10):
        return "c"
    return "python"


def _execute_code(code: str, language: str) -> dict:
    """
    执行代码并返回结果
    返回: {"output": str, "error": str, "success": bool}
    """
    tmp_dir = tempfile.gettempdir()

    try:
        if language == "c":
            # C 语言: 写入 .c 文件，gcc 编译后执行
            src_path = os.path.join(tmp_dir, "_exam_tmp.c")
            exe_path = os.path.join(tmp_dir, "_exam_tmp.exe")

            with open(src_path, "w", encoding="utf-8") as f:
                f.write(code)

            # 编译
            compile_result = subprocess.run(
                ["gcc", src_path, "-o", exe_path],
                capture_output=True, text=True, timeout=10,
                cwd=tmp_dir,
            )
            if compile_result.returncode != 0:
                _cleanup_files([src_path])
                return {"output": "", "error": compile_result.stderr or "编译失败", "success": False}

            # 执行
            result = subprocess.run(
                [exe_path],
                capture_output=True, text=True, timeout=5,
                cwd=tmp_dir,
            )
            _cleanup_files([src_path, exe_path])

        elif language == "java":
            # Java: 写入 Main.java，javac 编译后 java 执行
            java_path = os.path.join(tmp_dir, "Main.java")

            # 如果代码中没有 class 定义，自动包裹
            java_code = code
            if "class" not in code:
                java_code = f"public class Main {{\n    public static void main(String[] args) {{\n        {code}\n    }}\n}}"

            with open(java_path, "w", encoding="utf-8") as f:
                f.write(java_code)

            # 编译
            compile_result = subprocess.run(
                ["javac", java_path],
                capture_output=True, text=True, timeout=10,
                cwd=tmp_dir,
            )
            if compile_result.returncode != 0:
                _cleanup_files([java_path])
                return {"output": "", "error": compile_result.stderr or "编译失败", "success": False}

            # 执行
            result = subprocess.run(
                ["java", "Main"],
                capture_output=True, text=True, timeout=5,
                cwd=tmp_dir,
            )
            _cleanup_files([java_path, os.path.join(tmp_dir, "Main.class")])

        elif language == "cpp":
            # C++: 写入 .cpp 文件，g++ 编译后执行
            src_path = os.path.join(tmp_dir, "_exam_tmp.cpp")
            exe_path = os.path.join(tmp_dir, "_exam_tmp.exe")

            with open(src_path, "w", encoding="utf-8") as f:
                f.write(code)

            compile_result = subprocess.run(
                ["g++", src_path, "-o", exe_path],
                capture_output=True, text=True, timeout=10,
                cwd=tmp_dir,
            )
            if compile_result.returncode != 0:
                _cleanup_files([src_path])
                return {"output": "", "error": compile_result.stderr or "编译失败", "success": False}

            result = subprocess.run(
                [exe_path],
                capture_output=True, text=True, timeout=5,
                cwd=tmp_dir,
            )
            _cleanup_files([src_path, exe_path])

        else:
            # Python (默认)
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                f.write(code)
                tmp_path = f.name

            result = subprocess.run(
                [sys.executable, tmp_path],
                capture_output=True, text=True, timeout=5,
                cwd=tmp_dir,
            )
            _cleanup_files([tmp_path])

        output = result.stdout.strip() if result.stdout else ""
        if result.returncode != 0:
            return {"output": output, "error": result.stderr or "程序运行出错", "success": False}

        return {"output": output, "error": "", "success": True}

    except subprocess.TimeoutExpired:
        return {"output": "", "error": "代码运行超时（超过5秒），请检查是否存在死循环", "success": False}
    except Exception as e:
        return {"output": "", "error": f"运行失败: {str(e)}", "success": False}


def _cleanup_files(paths: list):
    """清理临时文件"""
    for p in paths:
        try:
            if os.path.exists(p):
                os.unlink(p)
        except:
            pass


class AnswerItem(BaseModel):
    question_id: int
    answer: str


class SubmitAnswersRequest(BaseModel):
    answers: List[AnswerItem]


@router.get("/exams", summary="获取学员考试列表")
def get_student_exams(student: Student = Depends(get_current_student), db: Session = Depends(get_db)):
    # 获取已完成的考试ID（有成绩记录的）
    completed_exam_ids = set(
        row[0] for row in db.query(Score.exam_id).filter(Score.student_id == student.id).all()
    )

    # 获取所有进行中的考试 + 已报名的考试
    registered_exam_ids = set(
        row[0] for row in db.query(ExamRegistration.exam_id)
        .filter(ExamRegistration.student_id == student.id)
        .all()
    )

    ongoing_exams = db.query(Exam).filter(Exam.status == "ongoing").all()
    registered_exams = db.query(Exam).filter(Exam.id.in_(registered_exam_ids)).all() if registered_exam_ids else []

    all_exam_ids = {e.id for e in ongoing_exams} | registered_exam_ids
    all_exams = db.query(Exam).filter(Exam.id.in_(all_exam_ids)).all() if all_exam_ids else []

    pending = []
    completed = []

    for exam in all_exams:
        exam_info = {
            "id": exam.id,
            "name": exam.name,
            "subject": exam.subject,
            "exam_date": exam.exam_date.isoformat() if exam.exam_date else None,
            "duration": exam.duration,
            "total_score": exam.total_score,
            "pass_score": exam.pass_score,
            "status": exam.status,
        }
        if exam.id in completed_exam_ids:
            completed.append(exam_info)
        else:
            pending.append(exam_info)

    return {"code": 200, "data": {"pending": pending, "completed": completed}}


@router.get("/exams/{exam_id}/status", summary="查询考试状态")
def check_exam_status(
    exam_id: int,
    student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """供学生端轮询考试状态，检测管理端是否已结束考试"""
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="考试不存在")
    return {
        "code": 200,
        "data": {
            "status": exam.status,
            "name": exam.name,
        }
    }


@router.get("/exams/{exam_id}/questions", summary="获取考试题目(不含答案)")
def get_exam_questions(
    exam_id: int,
    student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="考试不存在")

    # 检查考试状态
    if exam.status != "ongoing":
        raise HTTPException(status_code=400, detail=f"考试状态为「{exam.status}」，无法获取题目")

    # 检查是否已完成
    existing_score = db.query(Score).filter(
        Score.student_id == student.id,
        Score.exam_id == exam_id
    ).first()
    if existing_score:
        raise HTTPException(status_code=400, detail="您已完成该考试")

    questions = db.query(Question).filter(Question.exam_id == exam_id).order_by(Question.order_num).all()
    result = []
    for q in questions:
        item = {
            "id": q.id,
            "question_type": q.question_type,
            "content": q.content,
            "options": json.loads(q.options) if q.options else None,
            "score": q.score,
            "order_num": q.order_num,
        }
        # 编程题返回语言信息（answer 字段存储语言标识）
        if q.question_type == "programming":
            lang = (q.answer or "").strip().lower()
            if lang in ("python", "c", "java", "cpp", "c++"):
                item["language"] = lang
            else:
                # 回退到考试科目检测
                item["language"] = _detect_language(exam.subject)
        result.append(item)

    return {
        "code": 200,
        "data": {
            "exam": {
                "id": exam.id,
                "name": exam.name,
                "subject": exam.subject,
                "duration": exam.duration,
                "total_score": exam.total_score,
                "pass_score": exam.pass_score,
                "status": exam.status,
            },
            "questions": result,
        }
    }


@router.post("/exams/{exam_id}/submit", summary="提交答案")
def submit_exam(
    exam_id: int,
    data: SubmitAnswersRequest,
    student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="考试不存在")

    existing_score = db.query(Score).filter(
        Score.student_id == student.id,
        Score.exam_id == exam_id
    ).first()
    if existing_score:
        raise HTTPException(status_code=400, detail="您已提交过该考试")

    questions = db.query(Question).filter(Question.exam_id == exam_id).all()
    question_map = {q.id: q for q in questions}

    # 计算题目总分（所有题目的分值之和）
    total_possible = sum(q.score for q in questions)

    actual_score = 0.0
    answer_records = []

    for ans in data.answers:
        q = question_map.get(ans.question_id)
        if not q:
            continue

        is_correct = None
        score_obtained = 0.0
        student_answer = (ans.answer or "").strip()
        exec_output = None
        exec_error = None

        if not student_answer:
            # 未作答 → 0分
            is_correct = False
            score_obtained = 0.0
        elif q.question_type in ("choice", "true_false"):
            # 自动批改选择题/判断题
            correct_answer = (q.answer or "").strip()
            if correct_answer and student_answer.upper() == correct_answer.upper():
                is_correct = True
                score_obtained = q.score
            else:
                is_correct = False
                score_obtained = 0.0
        elif q.question_type == "fill_blank":
            # 填空题：精确匹配正确答案
            correct_answer = (q.answer or "").strip()
            if correct_answer and student_answer.lower().strip() == correct_answer.lower().strip():
                is_correct = True
                score_obtained = q.score
            else:
                is_correct = False
                score_obtained = 0.0
        elif q.question_type == "programming":
            # 编程题：从题目 answer 字段检测语言，运行代码与测试用例对比
            q_answer = (q.answer or "").strip().lower()
            # 判断 answer 是语言标识还是期望输出
            if q_answer in ("python", "c", "java", "cpp", "c++"):
                lang = q_answer
            else:
                lang = _detect_language(exam.subject)

            # 从 options 获取测试用例
            test_cases = []
            if q.options:
                try:
                    test_cases = json.loads(q.options) if isinstance(q.options, str) else q.options
                except:
                    test_cases = []

            exec_output = None
            exec_error = None
            if student_answer:
                try:
                    exec_result = _execute_code(student_answer, lang)
                    exec_output = exec_result.get("output", "")
                    exec_error = exec_result.get("error", "")
                    if exec_result["success"]:
                        if test_cases:
                            # 与测试用例的期望输出对比
                            passed_count = 0
                            for tc in test_cases:
                                expected = (tc.get("expected_output") or "").strip()
                                if expected and exec_output.strip() == expected:
                                    passed_count += 1
                            if passed_count == len(test_cases) and len(test_cases) > 0:
                                is_correct = True
                                score_obtained = q.score
                            else:
                                is_correct = False
                                score_obtained = 0.0
                        elif q_answer and q_answer not in ("python", "c", "java", "cpp", "c++"):
                            # answer 不是语言标识，视为期望输出
                            if exec_output.strip() == q_answer:
                                is_correct = True
                                score_obtained = q.score
                            else:
                                is_correct = False
                                score_obtained = 0.0
                        else:
                            # 没有测试用例，只要能运行就算通过
                            is_correct = True
                            score_obtained = q.score
                    else:
                        is_correct = False
                        score_obtained = 0.0
                except Exception as ex:
                    exec_error = str(ex)
                    is_correct = False
                    score_obtained = 0.0
            else:
                is_correct = False
                score_obtained = 0.0
        else:
            # 简答题等其他类型：0分（需人工批改）
            is_correct = None
            score_obtained = 0.0

        actual_score += score_obtained

        answer_record = ExamAnswer(
            student_id=student.id,
            exam_id=exam_id,
            question_id=q.id,
            student_answer=ans.answer,
            is_correct=is_correct,
            score_obtained=score_obtained,
            execution_output=exec_output,
            execution_error=exec_error,
        )
        answer_records.append(answer_record)

    # 保存答题记录
    for record in answer_records:
        db.add(record)

    # 及格线 = 总分的60%
    pass_threshold = total_possible * 0.6
    passed = actual_score >= pass_threshold

    # 保存成绩
    score_record = Score(
        student_id=student.id,
        exam_id=exam_id,
        score=actual_score,
        passed=passed,
        remarks="学员在线提交",
    )
    db.add(score_record)
    db.commit()

    return {
        "code": 200,
        "message": "提交成功",
        "data": {
            "score": actual_score,
            "total_score": total_possible,
            "pass_score": round(pass_threshold, 1),
            "passed": passed,
        }
    }


@router.get("/exams/{exam_id}/result", summary="获取考试结果")
def get_exam_result(
    exam_id: int,
    student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="考试不存在")

    score_record = db.query(Score).filter(
        Score.student_id == student.id,
        Score.exam_id == exam_id
    ).first()
    if not score_record:
        raise HTTPException(status_code=404, detail="未找到考试成绩")

    answer_records = db.query(ExamAnswer).filter(
        ExamAnswer.student_id == student.id,
        ExamAnswer.exam_id == exam_id
    ).all()

    questions = db.query(Question).filter(Question.exam_id == exam_id).order_by(Question.order_num).all()
    question_map = {q.id: q for q in questions}

    # 计算题目实际总分
    total_possible = sum(q.score for q in questions)

    details = []
    for ar in answer_records:
        q = question_map.get(ar.question_id)
        if not q:
            continue
        details.append({
            "question_id": q.id,
            "content": q.content,
            "question_type": q.question_type,
            "options": json.loads(q.options) if q.options else None,
            "student_answer": ar.student_answer,
            "correct_answer": q.answer,
            "is_correct": ar.is_correct,
            "score_obtained": ar.score_obtained,
            "score_total": q.score,
            "analysis": q.analysis,
            "execution_output": ar.execution_output,
            "execution_error": ar.execution_error,
        })

    return {
        "code": 200,
        "data": {
            "exam": {
                "id": exam.id,
                "name": exam.name,
                "subject": exam.subject,
                "total_score": total_possible,
            },
            "score": score_record.score,
            "passed": score_record.passed,
            "details": details,
        }
    }


class RunCodeRequest(BaseModel):
    code: str = Field(..., description="学生代码")
    question_id: int = Field(..., description="题目ID")


@router.post("/run-code", summary="运行代码测试")
def run_code(
    data: RunCodeRequest,
    student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """运行学生提交的代码，根据题目设置的语言运行，与测试用例对比"""
    # 获取题目
    question = db.query(Question).filter(Question.id == data.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")

    if question.question_type != "programming":
        raise HTTPException(status_code=400, detail="只能测试编程题")

    # 获取考试（用于回退语言检测）
    exam = db.query(Exam).filter(Exam.id == question.exam_id).first()

    # 从题目 answer 字段检测语言
    q_answer = (question.answer or "").strip().lower()
    if q_answer in ("python", "c", "java", "cpp", "c++"):
        language = q_answer
    else:
        language = _detect_language(exam.subject if exam else "")

    # 从 options 获取测试用例
    test_cases = []
    if question.options:
        try:
            test_cases = json.loads(question.options) if isinstance(question.options, str) else question.options
        except:
            test_cases = []

    # 获取期望输出（优先用测试用例，否则用 answer 字段）
    expected_output = ""
    if test_cases:
        expected_output = (test_cases[0].get("expected_output") or "").strip() if test_cases else ""
    elif q_answer not in ("python", "c", "java", "cpp", "c++"):
        expected_output = q_answer

    # 运行代码
    exec_result = _execute_code(data.code, language)

    correct = False
    if exec_result["success"] and test_cases:
        # 与所有测试用例对比
        passed_count = 0
        for tc in test_cases:
            tc_expected = (tc.get("expected_output") or "").strip()
            if tc_expected and exec_result["output"].strip() == tc_expected:
                passed_count += 1
        correct = passed_count == len(test_cases) and len(test_cases) > 0
    elif exec_result["success"] and expected_output:
        correct = exec_result["output"].strip() == expected_output

    return {
        "code": 200,
        "data": {
            "output": exec_result["output"],
            "error": exec_result["error"],
            "correct": correct,
            "expected": expected_output,
            "language": language,
        }
    }
