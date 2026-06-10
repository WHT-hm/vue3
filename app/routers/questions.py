"""考试题目管理路由"""
import json
import shutil
import subprocess
import tempfile
import os
import sys
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Question, Exam
from app.schemas import (
    QuestionCreate, QuestionUpdate, QuestionResponse,
    QuestionBatchImport, ApiResponse
)

# ==================== 编译器路径配置 ====================
# 自动检测 GCC、JDK 路径，添加到 PATH 以便 subprocess 调用
_EXTRA_PATHS = []
_MINGW_BIN = r"C:\msys64\mingw64\bin"
_JDK_BIN = r"C:\Program Files\Eclipse Adoptium\jdk-17.0.19.10-hotspot\bin"

if os.path.isdir(_MINGW_BIN):
    _EXTRA_PATHS.append(_MINGW_BIN)
if os.path.isdir(_JDK_BIN):
    _EXTRA_PATHS.append(_JDK_BIN)

if _EXTRA_PATHS:
    # 将编译器路径追加到当前进程 PATH（对子进程生效）
    os.environ["PATH"] = ";".join(_EXTRA_PATHS) + ";" + os.environ.get("PATH", "")

router = APIRouter(prefix="/api/questions", tags=["题目管理"])

# 题目类型映射
QUESTION_TYPES = {
    "choice": "选择题",
    "fill_blank": "填空题",
    "short_answer": "简答题",
    "true_false": "判断题",
    "programming": "编程题",
}


# ==================== 题目 CRUD ====================

@router.get("", summary="获取题目列表")
def get_questions(
    exam_id: int = Query(..., description="考试ID"),
    question_type: Optional[str] = Query(None, description="题目类型筛选"),
    db: Session = Depends(get_db)
):
    """获取指定考试的题目列表"""
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="考试不存在")

    query = db.query(Question).filter(Question.exam_id == exam_id)
    if question_type:
        query = query.filter(Question.question_type == question_type)

    questions = query.order_by(Question.order_num.asc(), Question.id.asc()).all()

    return {
        "code": 200,
        "message": "success",
        "data": [
            {
                "id": q.id,
                "exam_id": q.exam_id,
                "question_type": q.question_type,
                "content": q.content,
                "options": q.options,
                "answer": q.answer,
                "score": q.score,
                "order_num": q.order_num,
                "analysis": q.analysis,
                "created_at": str(q.created_at),
                "updated_at": str(q.updated_at),
            }
            for q in questions
        ]
    }


@router.get("/{question_id}", summary="获取题目详情", response_model=QuestionResponse)
def get_question(question_id: int, db: Session = Depends(get_db)):
    """根据ID获取题目详情"""
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    return question


@router.post("", summary="创建题目")
def create_question(data: QuestionCreate, db: Session = Depends(get_db)):
    """创建单个题目"""
    exam = db.query(Exam).filter(Exam.id == data.exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="考试不存在")

    question = Question(
        exam_id=data.exam_id,
        question_type=data.question_type,
        content=data.content,
        options=data.options,
        answer=data.answer,
        score=data.score,
        order_num=data.order_num,
        analysis=data.analysis,
    )
    db.add(question)
    db.commit()
    db.refresh(question)

    return {
        "code": 200,
        "message": "题目创建成功",
        "data": {
            "id": question.id,
            "exam_id": question.exam_id,
            "question_type": question.question_type,
            "content": question.content,
            "options": question.options,
            "answer": question.answer,
            "score": question.score,
            "order_num": question.order_num,
            "analysis": question.analysis,
        }
    }


@router.put("/{question_id}", summary="更新题目")
def update_question(question_id: int, data: QuestionUpdate, db: Session = Depends(get_db)):
    """更新题目信息"""
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(question, key, value)

    db.commit()
    db.refresh(question)

    return {
        "code": 200,
        "message": "题目更新成功",
        "data": {
            "id": question.id,
            "exam_id": question.exam_id,
            "question_type": question.question_type,
            "content": question.content,
            "options": question.options,
            "answer": question.answer,
            "score": question.score,
            "order_num": question.order_num,
            "analysis": question.analysis,
        }
    }


@router.delete("/{question_id}", summary="删除题目")
def delete_question(question_id: int, db: Session = Depends(get_db)):
    """删除题目"""
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")

    db.delete(question)
    db.commit()

    return {"code": 200, "message": "题目删除成功"}


# ==================== 批量操作 ====================

@router.post("/batch", summary="批量创建题目")
def batch_create_questions(data: QuestionBatchImport, db: Session = Depends(get_db)):
    """批量创建题目"""
    exam = db.query(Exam).filter(Exam.id == data.exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="考试不存在")

    created = []
    for idx, q_data in enumerate(data.questions):
        question = Question(
            exam_id=data.exam_id,
            question_type=q_data.question_type,
            content=q_data.content,
            options=q_data.options,
            answer=q_data.answer,
            score=q_data.score,
            order_num=q_data.order_num or idx + 1,
            analysis=q_data.analysis,
        )
        db.add(question)
        created.append(question)

    db.commit()

    return {
        "code": 200,
        "message": f"成功创建 {len(created)} 道题目",
        "data": {"count": len(created)}
    }


@router.post("/import", summary="从JSON文件导入题目")
async def import_questions_from_file(
    exam_id: int = Query(..., description="考试ID"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """从JSON文件导入题目"""
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="考试不存在")

    if not file.filename.endswith('.json'):
        raise HTTPException(status_code=400, detail="仅支持JSON格式文件")

    try:
        content = await file.read()
        data = json.loads(content.decode('utf-8'))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"文件解析失败: {str(e)}")

    # 支持两种格式：直接数组 或 { "questions": [...] }
    if isinstance(data, list):
        questions_data = data
    elif isinstance(data, dict) and "questions" in data:
        questions_data = data["questions"]
    else:
        raise HTTPException(status_code=400, detail="JSON格式错误，应为题目数组或包含questions字段的对象")

    created = []
    for idx, q_data in enumerate(questions_data):
        question = Question(
            exam_id=exam_id,
            question_type=q_data.get("question_type", "choice"),
            content=q_data.get("content", ""),
            options=json.dumps(q_data.get("options"), ensure_ascii=False) if isinstance(q_data.get("options"), (list, dict)) else q_data.get("options"),
            answer=q_data.get("answer", ""),
            score=q_data.get("score", 0),
            order_num=q_data.get("order_num", idx + 1),
            analysis=q_data.get("analysis", ""),
        )
        db.add(question)
        created.append(question)

    db.commit()

    return {
        "code": 200,
        "message": f"成功导入 {len(created)} 道题目",
        "data": {"count": len(created)}
    }


@router.delete("/exam/{exam_id}", summary="清空考试的所有题目")
def clear_exam_questions(exam_id: int, db: Session = Depends(get_db)):
    """清空指定考试的所有题目"""
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="考试不存在")

    count = db.query(Question).filter(Question.exam_id == exam_id).delete()
    db.commit()

    return {"code": 200, "message": f"已删除 {count} 道题目"}


# ==================== 编程题 - 代码执行 ====================

class CodeExecuteRequest(BaseModel):
    """代码执行请求"""
    code: str = Field(..., description="用户提交的代码")
    language: str = Field("python", description="编程语言: python/c/java")
    test_cases: Optional[str] = Field(None, description="测试用例JSON字符串")
    expected_output: Optional[str] = Field(None, description="期望输出")


class TestCaseItem(BaseModel):
    """单个测试用例"""
    input: str = ""
    expected_output: str = ""


@router.post("/execute", summary="执行代码并测试")
def execute_code(req: CodeExecuteRequest):
    """执行用户提交的代码，运行测试用例，返回结果和得分"""
    results = []
    test_cases_list = []

    # 解析测试用例
    if req.test_cases:
        try:
            test_cases_list = json.loads(req.test_cases)
        except json.JSONDecodeError:
            test_cases_list = []
    elif req.expected_output:
        test_cases_list = [{"input": "", "expected_output": req.expected_output}]

    if not test_cases_list:
        # 没有测试用例，直接运行代码看输出
        result = _run_code(req.code, req.language, "")
        return {
            "code": 200,
            "message": "执行完成",
            "data": {
                "passed": None,
                "total": 0,
                "results": [result],
                "score": 0,
            }
        }

    # 逐个运行测试用例
    passed_count = 0
    for tc in test_cases_list:
        inp = tc.get("input", "")
        expected = tc.get("expected_output", "").strip()
        result = _run_code(req.code, req.language, inp)
        actual = result.get("output", "").strip()

        is_passed = actual == expected
        if is_passed:
            passed_count += 1

        results.append({
            "input": inp,
            "expected_output": expected,
            "actual_output": actual,
            "passed": is_passed,
            "error": result.get("error", None),
        })

    total = len(test_cases_list)
    score = round(passed_count / total * 100, 2) if total > 0 else 0

    return {
        "code": 200,
        "message": "测试完成",
        "data": {
            "passed": passed_count,
            "total": total,
            "results": results,
            "score": score,
        }
    }


def _run_code(code: str, language: str, stdin_data: str) -> dict:
    """在子进程中运行代码，返回输出和错误"""
    try:
        if language == "python":
            # 使用临时文件运行Python代码
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                f.write(code)
                temp_path = f.name

            try:
                proc = subprocess.run(
                    [sys.executable, temp_path],
                    input=stdin_data,
                    capture_output=True,
                    text=True,
                    timeout=10,
                    cwd=tempfile.gettempdir(),
                )
                return {
                    "output": proc.stdout,
                    "error": proc.stderr if proc.stderr else None,
                    "exit_code": proc.returncode,
                }
            except subprocess.TimeoutExpired:
                return {"output": "", "error": "代码执行超时（10秒限制）", "exit_code": -1}
            finally:
                os.unlink(temp_path)

        elif language == "c":
            # C语言：写入临时文件 -> gcc编译 -> 运行
            temp_dir = tempfile.gettempdir()
            c_path = os.path.join(temp_dir, "solution.c")
            exe_path = os.path.join(temp_dir, "solution.exe")

            with open(c_path, 'w', encoding='utf-8') as f:
                f.write(code)

            try:
                # 编译
                compile_proc = subprocess.run(
                    ["gcc", c_path, "-o", exe_path],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    cwd=temp_dir,
                )
                if compile_proc.returncode != 0:
                    return {"output": "", "error": f"编译错误:\n{compile_proc.stderr}", "exit_code": compile_proc.returncode}

                # 运行
                proc = subprocess.run(
                    [exe_path],
                    input=stdin_data,
                    capture_output=True,
                    text=True,
                    timeout=10,
                    cwd=temp_dir,
                )
                return {
                    "output": proc.stdout,
                    "error": proc.stderr if proc.stderr else None,
                    "exit_code": proc.returncode,
                }
            except subprocess.TimeoutExpired:
                return {"output": "", "error": "代码执行超时（10秒限制）", "exit_code": -1}
            except FileNotFoundError:
                return {"output": "", "error": "未检测到GCC编译器，请安装MinGW或GCC并添加到PATH", "exit_code": -1}
            finally:
                for p in [c_path, exe_path]:
                    if os.path.exists(p):
                        try:
                            os.unlink(p)
                        except:
                            pass

        elif language == "java":
            # Java：写入临时文件 -> javac编译 -> java运行
            temp_dir = tempfile.gettempdir()
            java_path = os.path.join(temp_dir, "Solution.java")

            with open(java_path, 'w', encoding='utf-8') as f:
                f.write(code)

            try:
                # 编译
                compile_proc = subprocess.run(
                    ["javac", java_path],
                    capture_output=True,
                    text=True,
                    timeout=15,
                    cwd=temp_dir,
                )
                if compile_proc.returncode != 0:
                    return {"output": "", "error": f"编译错误:\n{compile_proc.stderr}", "exit_code": compile_proc.returncode}

                # 运行
                proc = subprocess.run(
                    ["java", "-cp", temp_dir, "Solution"],
                    input=stdin_data,
                    capture_output=True,
                    text=True,
                    timeout=10,
                    cwd=temp_dir,
                )
                return {
                    "output": proc.stdout,
                    "error": proc.stderr if proc.stderr else None,
                    "exit_code": proc.returncode,
                }
            except subprocess.TimeoutExpired:
                return {"output": "", "error": "代码执行超时（10秒限制）", "exit_code": -1}
            except FileNotFoundError:
                return {"output": "", "error": "未检测到Java环境，请安装JDK并添加到PATH", "exit_code": -1}
            finally:
                class_file = os.path.join(temp_dir, "Solution.class")
                for p in [java_path, class_file]:
                    if os.path.exists(p):
                        try:
                            os.unlink(p)
                        except:
                            pass

        else:
            return {"output": "", "error": f"不支持的语言: {language}", "exit_code": -1}

    except Exception as e:
        return {"output": "", "error": f"执行异常: {str(e)}", "exit_code": -1}
