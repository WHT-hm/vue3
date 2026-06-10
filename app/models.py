"""数据库模型定义"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Date, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.database import Base


class Student(Base):
    """学员模型"""
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), nullable=False, comment="姓名")
    gender = Column(String(10), nullable=False, comment="性别: 男/女")
    age = Column(Integer, nullable=True, comment="年龄")
    phone = Column(String(20), nullable=True, comment="联系电话")
    email = Column(String(100), nullable=True, comment="邮箱")
    id_card = Column(String(18), unique=True, nullable=True, comment="身份证号")
    school = Column(String(100), nullable=True, comment="学校/单位")
    major = Column(String(100), nullable=True, comment="专业")
    enrollment_date = Column(Date, nullable=True, comment="报名日期")
    status = Column(String(20), default="active", comment="状态: active/inactive/graduated")
    remark = Column(Text, nullable=True, comment="备注")
    student_no = Column(String(50), unique=True, nullable=True, comment="学号")
    password_hash = Column(String(255), nullable=True, comment="密码哈希")
    token = Column(String(100), nullable=True, comment="登录令牌")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系
    scores = relationship("Score", back_populates="student", cascade="all, delete-orphan")
    registrations = relationship("ExamRegistration", back_populates="student", cascade="all, delete-orphan")
    exam_answers = relationship("ExamAnswer", back_populates="student", cascade="all, delete-orphan")


class Exam(Base):
    """考试模型"""
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(200), nullable=False, comment="考试名称")
    subject = Column(String(100), nullable=False, comment="科目")
    exam_type = Column(String(20), nullable=False, default="formal", comment="考试类型: mock/formal")
    exam_date = Column(DateTime, nullable=False, comment="考试时间")
    duration = Column(Integer, nullable=True, comment="考试时长(分钟)")
    location = Column(String(200), nullable=True, comment="考试地点")
    total_score = Column(Float, default=100.0, comment="总分")
    pass_score = Column(Float, default=60.0, comment="及格分数")
    status = Column(String(20), default="upcoming", comment="状态: upcoming/ongoing/finished/cancelled")
    description = Column(Text, nullable=True, comment="考试描述")
    max_participants = Column(Integer, nullable=True, comment="最大参与人数")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系
    scores = relationship("Score", back_populates="exam", cascade="all, delete-orphan")
    registrations = relationship("ExamRegistration", back_populates="exam", cascade="all, delete-orphan")
    questions = relationship("Question", back_populates="exam", cascade="all, delete-orphan")


class Score(Base):
    """成绩模型"""
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, comment="学员ID")
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False, comment="考试ID")
    score = Column(Float, nullable=False, default=0, comment="得分")
    passed = Column(Boolean, default=False, comment="是否及格")
    rank = Column(Integer, nullable=True, comment="排名")
    remarks = Column(Text, nullable=True, comment="备注")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系
    student = relationship("Student", back_populates="scores")
    exam = relationship("Exam", back_populates="scores")


class ExamRegistration(Base):
    """考试报名模型"""
    __tablename__ = "exam_registrations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, comment="学员ID")
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False, comment="考试ID")
    registration_time = Column(DateTime, default=datetime.now, comment="报名时间")
    status = Column(String(20), default="registered", comment="状态: registered/checked_in/absent/cancelled")
    seat_number = Column(String(20), nullable=True, comment="座位号")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    # 关系
    student = relationship("Student", back_populates="registrations")
    exam = relationship("Exam", back_populates="registrations")


class Question(Base):
    """考试题目模型"""
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False, comment="考试ID")
    question_type = Column(String(30), nullable=False, default="choice", comment="题目类型: choice/fill_blank/short_answer/true_false/programming")
    content = Column(Text, nullable=False, comment="题目内容")
    options = Column(Text, nullable=True, comment="选项(JSON格式, 用于选择题)")
    answer = Column(Text, nullable=True, comment="正确答案")
    score = Column(Float, default=0, comment="分值")
    order_num = Column(Integer, default=0, comment="排序号")
    analysis = Column(Text, nullable=True, comment="解析")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系
    exam = relationship("Exam", back_populates="questions")


class User(Base):
    """系统用户模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, comment="用户名")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    real_name = Column(String(50), nullable=True, comment="真实姓名")
    phone = Column(String(20), nullable=True, comment="联系电话")
    student_no = Column(String(50), nullable=True, comment="学号")
    role = Column(String(20), default="admin", comment="角色: super_admin/admin/user")
    status = Column(String(20), default="active", comment="状态: active/disabled")
    token = Column(String(100), nullable=True, comment="登录令牌")
    last_login = Column(DateTime, nullable=True, comment="最后登录时间")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")


class ExamAnswer(Base):
    """答题记录模型"""
    __tablename__ = "exam_answers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, comment="学员ID")
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False, comment="考试ID")
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False, comment="题目ID")
    student_answer = Column(Text, nullable=True, comment="学员答案")
    is_correct = Column(Boolean, nullable=True, comment="是否正确")
    score_obtained = Column(Float, default=0, comment="得分")
    execution_output = Column(Text, nullable=True, comment="代码实际运行输出")
    execution_error = Column(Text, nullable=True, comment="代码运行错误信息")
    submitted_at = Column(DateTime, default=datetime.now, comment="提交时间")

    # 关系
    student = relationship("Student", back_populates="exam_answers")
    exam = relationship("Exam")
    question = relationship("Question")
