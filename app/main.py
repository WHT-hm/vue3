"""考试学员管理系统 - FastAPI 主应用"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routers import students, exams, scores, dashboard, questions, users, student_auth, student_exam
from app.utils.seed import init_db, run_seed


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时：创建数据库表并填充种子数据
    init_db()
    run_seed()
    yield
    # 关闭时：清理资源
    pass


app = FastAPI(
    title="考试学员管理系统",
    description="""
    ## 考试学员管理系统 API

    一个完整的考试学员管理后端系统，提供以下功能：

    ### 功能模块
    - **学员管理**: 学员信息的增删改查，支持搜索和筛选
    - **考试管理**: 考试的创建、管理、状态跟踪
    - **成绩管理**: 成绩录入、查询、批量操作、统计分析
    - **考试报名**: 学员报名考试、座位管理、签到
    - **数据统计**: 仪表盘概览、科目统计、成绩分布、学员排名、趋势分析

    ### 技术栈
    - FastAPI + SQLAlchemy + SQLite
    """,
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境请修改为具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(students.router)
app.include_router(exams.router)
app.include_router(scores.router)
app.include_router(dashboard.router)
app.include_router(questions.router)
app.include_router(users.router)
app.include_router(student_auth.router)
app.include_router(student_exam.router)


@app.get("/", tags=["系统"])
def root():
    """系统根路径"""
    return {
        "system": "考试学员管理系统",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health", tags=["系统"])
def health_check():
    """健康检查"""
    return {"status": "healthy", "message": "系统运行正常"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
