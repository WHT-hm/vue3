"""数据库种子数据 - 初始化示例数据"""
from datetime import datetime, date, timedelta
import random
import bcrypt
from app.database import SessionLocal, engine, Base
from app.models import Student, Exam, Score, ExamRegistration, User, ExamAnswer


def init_db():
    """初始化数据库表"""
    Base.metadata.create_all(bind=engine)
    _migrate_db()


def _migrate_db():
    """数据库迁移 - 为已有表添加新字段"""
    import sqlite3
    db_path = engine.url.database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 获取 students 表的列名
    cursor.execute("PRAGMA table_info(students)")
    existing_columns = {row[1] for row in cursor.fetchall()}

    # 需要添加的新字段（SQLite ALTER TABLE 不支持 UNIQUE，先添加普通列）
    new_columns = [
        ("student_no", "VARCHAR(50)"),
        ("password_hash", "VARCHAR(255)"),
        ("token", "VARCHAR(100)"),
    ]
    for col_name, col_type in new_columns:
        if col_name not in existing_columns:
            try:
                cursor.execute(f"ALTER TABLE students ADD COLUMN {col_name} {col_type}")
                print(f"  数据库迁移: 添加 students.{col_name}")
            except sqlite3.OperationalError as e:
                print(f"  数据库迁移跳过 students.{col_name}: {e}")

    conn.commit()
    conn.close()


def seed_students(db):
    """创建示例学员数据"""
    students_data = [
        {"name": "张三", "gender": "男", "age": 22, "phone": "13800138001", "email": "zhangsan@example.com",
         "id_card": "110101200001011234", "school": "北京大学", "major": "计算机科学与技术",
         "enrollment_date": date(2024, 3, 1), "status": "active"},
        {"name": "李四", "gender": "女", "age": 21, "phone": "13800138002", "email": "lisi@example.com",
         "id_card": "110101200102021235", "school": "清华大学", "major": "软件工程",
         "enrollment_date": date(2024, 3, 5), "status": "active"},
        {"name": "王五", "gender": "男", "age": 23, "phone": "13800138003", "email": "wangwu@example.com",
         "id_card": "110101199903031236", "school": "北京大学", "major": "人工智能",
         "enrollment_date": date(2024, 2, 20), "status": "active"},
        {"name": "赵六", "gender": "女", "age": 20, "phone": "13800138004", "email": "zhaoliu@example.com",
         "id_card": "110101200204041237", "school": "复旦大学", "major": "数据科学",
         "enrollment_date": date(2024, 3, 10), "status": "active"},
        {"name": "孙七", "gender": "男", "age": 24, "phone": "13800138005", "email": "sunqi@example.com",
         "id_card": "110101199805051238", "school": "浙江大学", "major": "信息安全",
         "enrollment_date": date(2024, 2, 15), "status": "active"},
        {"name": "周八", "gender": "女", "age": 22, "phone": "13800138006", "email": "zhouba@example.com",
         "id_card": "110101200006061239", "school": "上海交通大学", "major": "计算机科学与技术",
         "enrollment_date": date(2024, 3, 8), "status": "active"},
        {"name": "吴九", "gender": "男", "age": 25, "phone": "13800138007", "email": "wujiu@example.com",
         "id_card": "110101199707071240", "school": "南京大学", "major": "网络工程",
         "enrollment_date": date(2024, 1, 20), "status": "graduated"},
        {"name": "郑十", "gender": "女", "age": 21, "phone": "13800138008", "email": "zhengshi@example.com",
         "id_card": "110101200108081241", "school": "武汉大学", "major": "软件工程",
         "enrollment_date": date(2024, 3, 12), "status": "active"},
        {"name": "陈晓明", "gender": "男", "age": 23, "phone": "13800138009", "email": "chenxm@example.com",
         "id_card": "110101199909091242", "school": "北京大学", "major": "人工智能",
         "enrollment_date": date(2024, 2, 28), "status": "active"},
        {"name": "林小红", "gender": "女", "age": 22, "phone": "13800138010", "email": "linxh@example.com",
         "id_card": "110101200010101243", "school": "清华大学", "major": "数据科学",
         "enrollment_date": date(2024, 3, 3), "status": "active"},
        {"name": "黄大伟", "gender": "男", "age": 26, "phone": "13800138011", "email": "huangdw@example.com",
         "id_card": "110101199611111244", "school": "浙江大学", "major": "计算机科学与技术",
         "enrollment_date": date(2024, 1, 10), "status": "inactive"},
        {"name": "刘美丽", "gender": "女", "age": 20, "phone": "13800138012", "email": "liuml@example.com",
         "id_card": "110101200212121245", "school": "复旦大学", "major": "信息安全",
         "enrollment_date": date(2024, 3, 15), "status": "active"},
        {"name": "杨建国", "gender": "男", "age": 24, "phone": "13800138013", "email": "yangjg@example.com",
         "id_card": "110101199813131246", "school": "上海交通大学", "major": "网络工程",
         "enrollment_date": date(2024, 2, 5), "status": "active"},
        {"name": "何晓峰", "gender": "男", "age": 22, "phone": "13800138014", "email": "hexf@example.com",
         "id_card": "110101200014141247", "school": "南京大学", "major": "软件工程",
         "enrollment_date": date(2024, 3, 1), "status": "active"},
        {"name": "马丽华", "gender": "女", "age": 21, "phone": "13800138015", "email": "malh@example.com",
         "id_card": "110101200115151248", "school": "武汉大学", "major": "人工智能",
         "enrollment_date": date(2024, 3, 7), "status": "active"},
    ]

    students = []
    for data in students_data:
        student = Student(**data)
        db.add(student)
        students.append(student)

    db.flush()
    return students


def seed_exams(db):
    """创建示例考试数据"""
    now = datetime.now()
    exams_data = [
        {"name": "2024年春季Python编程考试", "subject": "Python编程", "exam_type": "formal",
         "exam_date": now - timedelta(days=30), "duration": 120, "location": "教学楼A-101",
         "total_score": 100, "pass_score": 60, "status": "finished",
         "description": "Python编程基础能力测试", "max_participants": 50},
        {"name": "2024年春季数据结构考试", "subject": "数据结构", "exam_type": "formal",
         "exam_date": now - timedelta(days=15), "duration": 90, "location": "教学楼B-203",
         "total_score": 100, "pass_score": 60, "status": "finished",
         "description": "数据结构与算法基础测试", "max_participants": 40},
        {"name": "2024年算法模拟测试", "subject": "算法设计", "exam_type": "mock",
         "exam_date": now - timedelta(days=7), "duration": 60, "location": "机房C-301",
         "total_score": 100, "pass_score": 60, "status": "finished",
         "description": "算法设计模拟考试", "max_participants": 30},
        {"name": "2024年夏季数据库原理考试", "subject": "数据库原理", "exam_type": "formal",
         "exam_date": now + timedelta(days=7), "duration": 120, "location": "教学楼A-201",
         "total_score": 100, "pass_score": 60, "status": "upcoming",
         "description": "数据库系统原理考试", "max_participants": 45},
        {"name": "2024年夏季网络技术考试", "subject": "网络技术", "exam_type": "formal",
         "exam_date": now + timedelta(days=14), "duration": 90, "location": "教学楼B-105",
         "total_score": 100, "pass_score": 60, "status": "upcoming",
         "description": "计算机网络技术考试", "max_participants": 50},
        {"name": "2024年秋季综合测试", "subject": "综合", "exam_type": "formal",
         "exam_date": now + timedelta(days=30), "duration": 180, "location": "大礼堂",
         "total_score": 150, "pass_score": 90, "status": "upcoming",
         "description": "秋季学期综合能力测试", "max_participants": 100},
        {"name": "机器学习入门模拟考", "subject": "机器学习", "exam_type": "mock",
         "exam_date": now + timedelta(days=3), "duration": 60, "location": "机房C-302",
         "total_score": 100, "pass_score": 60, "status": "upcoming",
         "description": "机器学习基础模拟测试", "max_participants": 25},
    ]

    exams = []
    for data in exams_data:
        exam = Exam(**data)
        db.add(exam)
        exams.append(exam)

    db.flush()
    return exams


def seed_scores(db, students, exams):
    """创建示例成绩数据"""
    finished_exams = [e for e in exams if e.status == "finished"]

    for exam in finished_exams:
        # 随机选择部分学员参加考试
        participants = random.sample(students, min(random.randint(8, 13), len(students)))

        for student in participants:
            # 生成正态分布的随机分数
            score_val = max(0, min(exam.total_score, random.gauss(70, 15)))
            score_val = round(score_val, 1)
            passed = score_val >= exam.pass_score

            score = Score(
                student_id=student.id,
                exam_id=exam.id,
                score=score_val,
                passed=passed,
                remarks="系统自动生成" if random.random() > 0.7 else None,
            )
            db.add(score)

            # 创建报名记录
            reg = ExamRegistration(
                student_id=student.id,
                exam_id=exam.id,
                status="checked_in",
                seat_number=f"A-{random.randint(1, 50):03d}",
            )
            db.add(reg)


def seed_registrations(db, students, exams):
    """为即将到来的考试创建报名记录"""
    upcoming_exams = [e for e in exams if e.status == "upcoming"]

    for exam in upcoming_exams:
        participants = random.sample(students, min(random.randint(5, 10), len(students)))

        for student in participants:
            # 检查是否已有报名
            existing = db.query(ExamRegistration).filter(
                ExamRegistration.student_id == student.id,
                ExamRegistration.exam_id == exam.id
            ).first()
            if not existing:
                reg = ExamRegistration(
                    student_id=student.id,
                    exam_id=exam.id,
                    status="registered",
                )
                db.add(reg)
def seed_super_admin(db):
    """创建默认超级管理员账号"""
    existing = db.query(User).filter(User.username == "test").first()
    if existing:
        print("  - 超级管理员账号已存在，跳过创建")
        return

    admin = User(
        username="test",
        password_hash=bcrypt.hashpw("123456".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
        real_name="超级管理员",
        role="super_admin",
        status="active",
    )
    db.add(admin)
    print("  - 创建了默认超级管理员账号 (用户名: test, 密码: 123456)")


def run_seed():
    """执行种子数据填充"""
    db = SessionLocal()
    try:
        # 始终确保超级管理员存在
        seed_super_admin(db)

        # 检查是否已有数据
        if db.query(Student).count() > 0:
            print("数据库已有数据，跳过种子数据填充")
            db.commit()
            return

        print("开始填充种子数据...")

        students = seed_students(db)
        print(f"  - 创建了 {len(students)} 个学员")

        exams = seed_exams(db)
        print(f"  - 创建了 {len(exams)} 个考试")

        seed_scores(db, students, exams)
        print("  - 创建了成绩数据")

        seed_registrations(db, students, exams)
        print("  - 创建了报名数据")

        db.commit()
        print("种子数据填充完成！")

    except Exception as e:
        db.rollback()
        print(f"种子数据填充失败: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    run_seed()
