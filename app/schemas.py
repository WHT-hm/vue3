"""Pydantic 数据验证模型"""
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, model_validator


# ==================== 学员相关 Schema ====================

class StudentBase(BaseModel):
    name: str = Field(..., max_length=50, description="姓名")
    gender: str = Field(..., max_length=10, description="性别")
    age: Optional[int] = Field(None, description="年龄")
    phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    email: Optional[str] = Field(None, max_length=100, description="邮箱")
    id_card: Optional[str] = Field(None, max_length=18, description="身份证号")
    school: Optional[str] = Field(None, max_length=100, description="学校/单位")
    major: Optional[str] = Field(None, max_length=100, description="专业")
    enrollment_date: Optional[date] = Field(None, description="报名日期")
    status: Optional[str] = Field("active", description="状态")
    remark: Optional[str] = Field(None, description="备注")


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=50)
    gender: Optional[str] = Field(None, max_length=10)
    age: Optional[int] = None
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    id_card: Optional[str] = Field(None, max_length=18)
    school: Optional[str] = Field(None, max_length=100)
    major: Optional[str] = Field(None, max_length=100)
    enrollment_date: Optional[date] = None
    status: Optional[str] = None
    remark: Optional[str] = None


class StudentResponse(StudentBase):
    id: int
    student_no: Optional[str] = Field(None, description="学号")
    is_registered: bool = Field(False, description="是否已注册(学员端)")

    @model_validator(mode='before')
    @classmethod
    def compute_is_registered(cls, data):
        """根据 password_hash 判断是否已在学员端注册"""
        if hasattr(data, 'password_hash'):
            # SQLAlchemy 模型对象
            object.__setattr__(data, 'is_registered', bool(data.password_hash))
        elif isinstance(data, dict):
            data['is_registered'] = bool(data.get('password_hash'))
        return data

    class Config:
        from_attributes = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StudentWithScores(StudentResponse):
    """带成绩信息的学员响应"""
    score_count: int = 0
    avg_score: Optional[float] = None
    pass_rate: Optional[float] = None


# ==================== 考试相关 Schema ====================

class ExamBase(BaseModel):
    name: str = Field(..., max_length=200, description="考试名称")
    subject: str = Field(..., max_length=100, description="科目")
    exam_type: str = Field("formal", max_length=20, description="考试类型: mock/formal")
    exam_date: datetime = Field(..., description="考试时间")
    duration: Optional[int] = Field(None, description="考试时长(分钟)")
    location: Optional[str] = Field(None, max_length=200, description="考试地点")
    total_score: float = Field(100.0, description="总分")
    pass_score: float = Field(60.0, description="及格分数")
    status: Optional[str] = Field("upcoming", description="状态")
    description: Optional[str] = Field(None, description="考试描述")
    max_participants: Optional[int] = Field(None, description="最大参与人数")


class ExamCreate(ExamBase):
    pass


class ExamUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    subject: Optional[str] = Field(None, max_length=100)
    exam_type: Optional[str] = Field(None, max_length=20)
    exam_date: Optional[datetime] = None
    duration: Optional[int] = None
    location: Optional[str] = Field(None, max_length=200)
    total_score: Optional[float] = None
    pass_score: Optional[float] = None
    status: Optional[str] = None
    description: Optional[str] = None
    max_participants: Optional[int] = None


class ExamResponse(ExamBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ExamWithStats(ExamResponse):
    """带统计信息的考试响应"""
    registered_count: int = 0
    scored_count: int = 0
    avg_score: Optional[float] = None
    pass_rate: Optional[float] = None
    highest_score: Optional[float] = None
    lowest_score: Optional[float] = None


# ==================== 成绩相关 Schema ====================

class ScoreBase(BaseModel):
    student_id: int = Field(..., description="学员ID")
    exam_id: int = Field(..., description="考试ID")
    score: float = Field(..., ge=0, description="得分")
    passed: Optional[bool] = Field(None, description="是否及格")
    rank: Optional[int] = Field(None, description="排名")
    remarks: Optional[str] = Field(None, description="备注")


class ScoreCreate(ScoreBase):
    pass


class ScoreUpdate(BaseModel):
    score: Optional[float] = Field(None, ge=0)
    passed: Optional[bool] = None
    rank: Optional[int] = None
    remarks: Optional[str] = None


class ScoreResponse(ScoreBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ScoreDetailResponse(ScoreResponse):
    """带详细信息的成绩响应"""
    student_name: Optional[str] = None
    exam_name: Optional[str] = None
    subject: Optional[str] = None


# ==================== 考试报名相关 Schema ====================

class ExamRegistrationBase(BaseModel):
    student_id: int = Field(..., description="学员ID")
    exam_id: int = Field(..., description="考试ID")
    seat_number: Optional[str] = Field(None, max_length=20, description="座位号")


class ExamRegistrationCreate(ExamRegistrationBase):
    pass


class ExamRegistrationUpdate(BaseModel):
    status: Optional[str] = Field(None, description="状态")
    seat_number: Optional[str] = Field(None, max_length=20)


class ExamRegistrationResponse(ExamRegistrationBase):
    id: int
    registration_time: datetime
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class ExamRegistrationDetail(ExamRegistrationResponse):
    """带详细信息的报名响应"""
    student_name: Optional[str] = None
    exam_name: Optional[str] = None


# ==================== 统计相关 Schema ====================

class DashboardOverview(BaseModel):
    """仪表盘概览"""
    total_students: int = 0
    active_students: int = 0
    total_exams: int = 0
    upcoming_exams: int = 0
    total_scores: int = 0
    overall_pass_rate: Optional[float] = None
    overall_avg_score: Optional[float] = None


class SubjectStats(BaseModel):
    """科目统计"""
    subject: str
    exam_count: int = 0
    avg_score: Optional[float] = None
    pass_rate: Optional[float] = None
    highest_score: Optional[float] = None
    lowest_score: Optional[float] = None


class ExamScoreDistribution(BaseModel):
    """考试成绩分布"""
    exam_name: str
    ranges: dict  # {"0-59": 5, "60-69": 10, ...}


class StudentRanking(BaseModel):
    """学员排名"""
    student_id: int
    student_name: str
    school: Optional[str] = None
    avg_score: float
    total_exams: int
    pass_count: int


# ==================== 题目相关 Schema ====================

class QuestionBase(BaseModel):
    question_type: str = Field("choice", max_length=30, description="题目类型: choice/fill_blank/short_answer/true_false/programming")
    content: str = Field(..., description="题目内容")
    options: Optional[str] = Field(None, description="选项(JSON格式, 用于选择题)")
    answer: Optional[str] = Field(None, description="正确答案")
    score: float = Field(0, description="分值")
    order_num: int = Field(0, description="排序号")
    analysis: Optional[str] = Field(None, description="解析")


class QuestionCreate(QuestionBase):
    exam_id: int = Field(..., description="考试ID")


class QuestionUpdate(BaseModel):
    question_type: Optional[str] = Field(None, max_length=30)
    content: Optional[str] = None
    options: Optional[str] = None
    answer: Optional[str] = None
    score: Optional[float] = None
    order_num: Optional[int] = None
    analysis: Optional[str] = None


class QuestionResponse(QuestionBase):
    id: int
    exam_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class QuestionBatchImport(BaseModel):
    """批量导入题目"""
    exam_id: int = Field(..., description="考试ID")
    questions: List[QuestionBase] = Field(..., description="题目列表")


# ==================== 用户认证相关 Schema ====================

class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., min_length=1, max_length=50, description="用户名")
    password: str = Field(..., min_length=1, description="密码")


class LoginResponse(BaseModel):
    """登录响应"""
    token: str = Field(..., description="登录令牌")
    user: "UserResponse" = Field(..., description="用户信息")


class UserCreate(BaseModel):
    """创建用户"""
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    password: str = Field(..., min_length=4, description="密码")
    real_name: Optional[str] = Field(None, max_length=50, description="真实姓名")
    phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    student_no: Optional[str] = Field(None, max_length=50, description="学号")
    role: str = Field("admin", max_length=20, description="角色: super_admin/admin/user")


class UserUpdate(BaseModel):
    """更新用户"""
    real_name: Optional[str] = Field(None, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    student_no: Optional[str] = Field(None, max_length=50)
    role: Optional[str] = Field(None, max_length=20)


class ChangePassword(BaseModel):
    """修改密码"""
    old_password: str = Field(..., min_length=1, description="旧密码")
    new_password: str = Field(..., min_length=4, description="新密码")


class ResetPassword(BaseModel):
    """重置密码（超级管理员用）"""
    new_password: str = Field(..., min_length=4, description="新密码")


class UserResponse(BaseModel):
    """用户响应"""
    id: int
    username: str
    real_name: Optional[str] = None
    phone: Optional[str] = None
    student_no: Optional[str] = None
    role: str
    status: str
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 更新前向引用
LoginResponse.model_rebuild()


# ==================== 通用响应 Schema ====================

class ApiResponse(BaseModel):
    """统一API响应格式"""
    code: int = 200
    message: str = "success"
    data: Optional[dict | list | None] = None


class PaginatedResponse(BaseModel):
    """分页响应"""
    items: List = []
    total: int = 0
    page: int = 1
    page_size: int = 20
    total_pages: int = 0
