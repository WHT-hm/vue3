# 🎓 考试学员管理系统

一个基于 **FastAPI + Vue3 + Element Plus** 的全栈考试学员管理系统，提供学员管理、考试管理、题目管理、成绩管理、考试报名、用户管理和数据统计等完整功能，包含后端 RESTful API、管理员前端和学员前端。

---

## 📑 目录

- [功能模块](#-功能模块)
- [技术栈](#-技术栈)
- [环境要求](#-环境要求)
- [快速启动](#-快速启动)
  - [第一步：获取项目代码](#第一步获取项目代码)
  - [第二步：启动后端服务](#第二步启动后端服务)
  - [第三步：启动管理员前端](#第三步启动管理员前端)
  - [第四步：启动学员前端](#第四步启动学员前端)
  - [第五步：访问系统](#第五步访问系统)
- [前端页面说明](#-前端页面说明)
- [API 端点一览](#-api-端点一览)
- [项目结构](#-项目结构)
- [数据库说明](#-数据库说明)
- [常见问题](#-常见问题)
- [停止服务](#-停止服务)

---

## 📋 功能模块

### 🧑‍🎓 学员管理
- 学员信息的增删改查（CRUD）
- 支持关键词搜索（姓名、电话、学号、邮箱）
- 状态筛选（活跃、停用、已毕业）
- 学校筛选
- 每个学员附带成绩统计（考试次数、平均分、通过率）

### 📝 考试管理
- 考试创建与管理
- 考试状态跟踪（即将开始、进行中、已结束、已取消）
- 考试类型区分（正式考试、模拟考试）
- 每场考试附带统计（报名人数、平均分、通过率、最高/最低分）
- 即将开始的考试查询

### 📋 题目管理
- 题目的创建、编辑、删除
- 支持多种题目类型：选择题、判断题、填空题、简答题
- 选择题支持 JSON 格式选项
- 题目排序、分值设置、解析填写
- 按考试筛选题目
- 批量导入题目

### 📊 成绩管理
- 成绩录入（单条 & 批量）
- 自动判断及格状态
- 多条件筛选（学员、考试、及格状态、分数范围）
- 学员成绩历史查询
- 学员在线提交的答案自动记录并批改

### 📬 考试报名
- 学员报名考试
- 报名状态管理（已报名、已签到、缺考、已取消）
- 座位号分配
- 人数限制检查

### 👤 用户管理（管理员）
- Token 认证登录（UUID Token 存储在数据库）
- 超级管理员创建和管理普通管理员账号
- 用户启用/禁用
- 重置密码
- 修改密码
- 角色区分（super_admin / admin）

### 🎓 学员端功能
- 学员自主注册（姓名、学号、手机号、密码）
- 学号 + 密码登录
- 查看待做考试和已完成考试
- 在线答题（倒计时、多种题型）
- 提交后查看批改结果（逐题详情）
- 选择题/判断题自动批改

###  数据统计仪表盘
- 系统概览（学员数、考试数、通过率等）
- 科目统计分析
- 考试成绩分布（分数段统计）
- 学员综合排名
- 月度趋势分析
- 最近活动记录

---

## 🛠 技术栈

### 后端

| 技术 | 版本 | 说明 |
|------|------|------|
| **FastAPI** | 0.115+ | 高性能异步 Web 框架 |
| **SQLAlchemy** | 2.0+ | Python ORM 框架 |
| **SQLite** | 内置 | 轻量级数据库（无需额外安装） |
| **Pydantic** | 2.0+ | 数据验证与序列化 |
| **Uvicorn** | 0.34+ | ASGI 服务器 |
| **bcrypt** | 4.0+ | 密码加密 |

### 前端（管理员端 + 学员端）

| 技术 | 版本 | 说明 |
|------|------|------|
| **Vue 3** | 3.4+ | 渐进式 JavaScript 框架 |
| **Vue Router** | 4.3+ | 官方路由管理 |
| **Pinia** | 2.1+ | 新一代状态管理 |
| **Element Plus** | 2.8+ | Vue3 UI 组件库 |
| **Axios** | 1.7+ | HTTP 请求库 |
| **Vite** | 5.4+ | 前端构建工具 |

---

## ✅ 环境要求

在启动本项目之前，请确保你的电脑已安装以下软件：

| 软件 | 最低版本 | 验证命令 | 下载地址 |
|------|---------|---------|---------|
| **Python** | 3.9+ | `python --version` | [python.org](https://www.python.org/downloads/) |
| **Node.js** | 16+ | `node --version` | [nodejs.org](https://nodejs.org/) |
| **npm** | 8+ | `npm --version` | 随 Node.js 自动安装 |

> **提示**：如果 `python` 命令不可用，请尝试使用 `python3` 或 `py`。本 README 统一使用 `python` 命令。

---

## 🚀 快速启动

按照以下步骤，从零开始启动考试学员管理系统。整个流程分为 **5 个步骤**：

```
第一步（进入目录）→ 第二步（启动后端）→ 第三步（管理员前端）→ 第四步（学员前端）→ 第五步（访问系统）
```

---

### 第一步：进入项目目录

> **🎯 目的**：将终端工作目录切换到项目根目录，以便后续命令能正确找到项目文件。

```bash
cd d:\vscode\python\exam_manager
```

> 如果你已经在本项目目录中，可以跳过此步骤。

---

### 第二步：启动后端服务

后端服务需要 3 个子步骤：**创建隔离环境 → 安装依赖 → 启动服务**。

#### 2.1 创建并激活 Python 虚拟环境

> **🎯 目的**：创建一个独立的 Python 运行环境，将本项目的依赖包与系统全局 Python 环境隔离，避免与其他项目产生依赖冲突。

**创建虚拟环境：**

```bash
python -m venv venv
```

**激活虚拟环境：**

```bash
# Windows CMD
venv\Scripts\activate.bat

# Windows PowerShell
venv\Scripts\Activate.ps1

# Linux / macOS
source venv/bin/activate
```

> ✅ 激活成功标志：终端提示符前面会出现 `(venv)` 标识。

#### 2.2 安装 Python 依赖包

```bash
pip install -r requirements.txt
```

> 🐌 如果下载速度慢，可以使用清华大学国内镜像源加速：
> ```bash
> pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
> ```

#### 2.3 启动后端 API 服务

> **🎯 目的**：在 8000 端口启动后端 API 服务，提供数据接口供前端调用。首次启动会自动创建数据库并填充示例数据。

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

> 📦 **首次启动**时系统会自动：
> 1. 创建 SQLite 数据库文件 `exam_manager.db`
> 2. 自动迁移数据库（为已有表添加新字段）
> 3. 填充示例数据（15 个学员、7 场考试、成绩及报名记录）
> 4. 创建超级管理员账号（test / 123456）

✅ 启动成功后，终端会显示：

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

> 🔒 **保持此终端窗口运行**，不要关闭。接下来打开一个新的终端窗口执行第三步。

---

### 第三步：启动管理员前端

> ⚠️ **请打开一个新的终端窗口**执行以下操作，后端服务终端保持运行不要关闭。

#### 3.1 进入前端目录并安装依赖

```bash
cd d:\vscode\python\exam_manager\frontend
npm install
```

#### 3.2 启动管理员前端开发服务器

```bash
npm run dev
```

✅ 启动成功后，终端会显示：

```
➜  Local:   http://localhost:3000/
```

---

### 第四步：启动学员前端

> ⚠️ **再打开一个新的终端窗口**。

#### 4.1 进入学员前端目录并安装依赖

```bash
cd d:\vscode\python\exam_manager\student-frontend
npm install
```

#### 4.2 启动学员前端开发服务器

```bash
npm run dev
```

✅ 启动成功后，终端会显示：

```
➜  Local:   http://localhost:3001/
```

---

### 第五步：访问系统

| 地址 | 用途 |
|------|------|
| **http://localhost:3000** | **🎨 管理员前端界面** |
| **http://localhost:3001** | **🎓 学员前端界面** |
| http://localhost:8000/docs | 📖 Swagger UI 交互式 API 文档 |
| http://localhost:8000/redoc | ReDoc 格式 API 文档 |
| http://localhost:8000/health | 后端健康检查 |

**🔑 管理员登录信息：**

| 用户名 | 密码 | 角色 | 说明 |
|--------|------|------|------|
| `test` | `123456` | super_admin | 超级管理员（可管理其他管理员） |

**🎓 学员登录信息：**

| 学号 | 密码 | 说明 |
|------|------|------|
| `S2024001` | `123456` | 测试学员账号 |
| — | — | 也可通过注册页面创建新学员 |

---

### 🔄 启动流程总结

| 步骤 | 操作 | 命令 | 端口 |
|------|------|------|------|
| 第一步 | 进入项目目录 | `cd d:\vscode\python\exam_manager` | - |
| 第二步 | 启动后端服务 | `uvicorn app.main:app --port 8000 --reload` | 8000 |
| 第三步 | 启动管理员前端 | `cd frontend` → `npm install` → `npm run dev` | 3000 |
| 第四步 | 启动学员前端 | `cd student-frontend` → `npm install` → `npm run dev` | 3001 |
| 第五步 | 访问系统 | 浏览器打开对应地址 | - |

---

## 🖥️ 前端页面说明

### 管理员前端（http://localhost:3000）

#### 登录页面 (`/login`)
- 渐变背景登录界面
- Token 认证登录（连接后端 API）
- 表单验证（用户名 + 密码必填）
- 默认账号：test / 123456

#### 仪表盘 (`/dashboard`)
- **统计卡片**：学员总数、考试总数、成绩记录数、总体通过率
- **学员排名 TOP 10**：按平均分排名，金银铜牌标识
- **科目统计**：各科目考试数、平均分、通过率
- **最近活动**：系统操作时间线
- **即将开始的考试**：最近即将开始的考试列表

#### 学员管理 (`/students`)
- 关键词搜索（姓名/电话/学号）、状态筛选、学校筛选
- 学员信息 CRUD + 成绩统计
- 分页支持

#### 考试管理 (`/exams`)
- 考试名称、科目、状态、类型多条件筛选
- 考试信息 CRUD + 统计数据
- 报名管理

#### 成绩管理 (`/scores`)
- 按学员、考试、及格状态筛选
- 单条 & 批量录入成绩
- 学员在线提交的成绩也会显示在此

#### 用户管理 (`/users`)
- **仅超级管理员可见**
- 管理员账号 CRUD
- 启用/禁用账号
- 重置密码
- 角色分配（super_admin / admin）

### 学员前端（http://localhost:3001）

#### 登录页面 (`/login`)
- 学号 + 密码登录
- "去注册"链接跳转到注册页面

#### 注册页面 (`/register`)
- 填写姓名、学号、手机号、密码、确认密码
- 注册成功自动跳转登录页面

#### 首页 (`/home`)
- **待做考试**：显示进行中且未完成的考试
- **已完成考试**：显示已提交的考试及得分
- 点击考试卡片进入答题或查看结果

#### 答题页面 (`/exam/:id`)
- 进入前弹出考试信息确认（名称、时长、总分）
- 倒计时显示，结束自动提交
- 按题型展示不同输入控件（选择题选项、判断题对错、填空/简答文本框）
- 手动提交按钮

#### 结果页面 (`/result/:id`)
- 总分、及格线、是否及格
- 逐题详情：题目、学生答案、正确答案、得分、是否正确

---

## 📡 API 端点一览

### 系统接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 系统信息 |
| GET | `/health` | 健康检查 |

### 管理员认证 `/api/auth`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/login` | 管理员登录 |
| POST | `/api/auth/logout` | 管理员登出 |
| GET | `/api/auth/me` | 获取当前管理员信息 |
| PUT | `/api/auth/change-password` | 修改密码 |

### 用户管理 `/api/users`（需超级管理员权限）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/users` | 用户列表 |
| POST | `/api/users` | 创建用户 |
| PUT | `/api/users/{id}` | 更新用户 |
| DELETE | `/api/users/{id}` | 删除用户 |
| PUT | `/api/users/{id}/reset-password` | 重置密码 |
| PUT | `/api/users/{id}/toggle-status` | 启用/禁用用户 |

### 学员管理 `/api/students`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/students` | 学员列表（分页、搜索、筛选） |
| GET | `/api/students/{id}` | 学员详情 |
| POST | `/api/students` | 创建学员 |
| PUT | `/api/students/{id}` | 更新学员 |
| DELETE | `/api/students/{id}` | 删除学员 |
| GET | `/api/students/export/all` | 导出所有学员 |

### 考试管理 `/api/exams`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/exams` | 考试列表 |
| GET | `/api/exams/upcoming` | 即将开始的考试 |
| GET | `/api/exams/{id}` | 考试详情 |
| POST | `/api/exams` | 创建考试 |
| PUT | `/api/exams/{id}` | 更新考试 |
| DELETE | `/api/exams/{id}` | 删除考试 |
| POST | `/api/exams/{id}/register` | 报名考试 |
| GET | `/api/exams/{id}/registrations` | 报名列表 |

### 题目管理 `/api/questions`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/questions` | 题目列表（支持 exam_id 筛选） |
| GET | `/api/questions/{id}` | 题目详情 |
| POST | `/api/questions` | 创建题目 |
| PUT | `/api/questions/{id}` | 更新题目 |
| DELETE | `/api/questions/{id}` | 删除题目 |
| POST | `/api/questions/batch` | 批量导入题目 |

### 成绩管理 `/api/scores`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/scores` | 成绩列表 |
| GET | `/api/scores/{id}` | 成绩详情 |
| POST | `/api/scores` | 录入成绩 |
| POST | `/api/scores/batch` | 批量录入成绩 |
| PUT | `/api/scores/{id}` | 更新成绩 |
| DELETE | `/api/scores/{id}` | 删除成绩 |
| GET | `/api/scores/student/{id}/history` | 学员成绩历史 |

### 数据统计 `/api/dashboard`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/dashboard/overview` | 系统概览 |
| GET | `/api/dashboard/subject-stats` | 科目统计 |
| GET | `/api/dashboard/score-distribution/{exam_id}` | 成绩分布 |
| GET | `/api/dashboard/student-ranking` | 学员排名 |
| GET | `/api/dashboard/monthly-trend` | 月度趋势 |
| GET | `/api/dashboard/recent-activities` | 最近活动 |

### 学员认证 `/api/student`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/student/register` | 学员注册 |
| POST | `/api/student/login` | 学员登录 |
| POST | `/api/student/logout` | 学员登出 |
| GET | `/api/student/me` | 获取当前学员信息 |

### 学员考试 `/api/student`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/student/exams` | 获取考试列表（待做/已完成） |
| GET | `/api/student/exams/{id}/questions` | 获取考试题目（不含答案） |
| POST | `/api/student/exams/{id}/submit` | 提交答案（自动批改） |
| GET | `/api/student/exams/{id}/result` | 查看考试结果 |

---

## 📁 项目结构

```
exam_manager/
├── app/                              # 后端 Python 应用
│   ├── __init__.py                   # 应用包初始化
│   ├── main.py                       # FastAPI 主应用入口
│   ├── database.py                   # 数据库配置（SQLite 连接）
│   ├── models.py                     # SQLAlchemy 数据模型（Student/Exam/Score/Question/User/ExamAnswer/ExamRegistration）
│   ├── schemas.py                    # Pydantic 数据验证模型
│   ├── routers/                      # 路由模块（按功能拆分）
│   │   ├── __init__.py
│   │   ├── students.py               # 学员管理路由
│   │   ├── exams.py                  # 考试管理路由
│   │   ├── scores.py                 # 成绩管理路由
│   │   ├── questions.py              # 题目管理路由
│   │   ├── dashboard.py              # 统计仪表盘路由
│   │   ├── users.py                  # 管理员用户管理 & 认证路由
│   │   ├── student_auth.py           # 学员认证路由（注册/登录/登出）
│   │   └── student_exam.py           # 学员考试路由（答题/提交/查看结果）
│   └── utils/                        # 工具模块
│       ├── __init__.py
│       └── seed.py                   # 数据库种子数据 + 自动迁移
├── frontend/                         # 管理员前端 Vue3 应用（端口 3000）
│   ├── index.html                    # 入口 HTML
│   ├── package.json                  # 前端依赖配置
│   ├── vite.config.js                # Vite 配置（API 代理到后端 8000）
│   └── src/
│       ├── main.js                   # 应用入口
│       ├── App.vue                   # 根组件
│       ├── api/                      # API 请求模块
│       │   ├── index.js              # Axios 实例和拦截器
│       │   ├── auth.js               # 管理员认证 API
│       │   ├── users.js              # 用户管理 API
│       │   ├── students.js           # 学员 API
│       │   ├── exams.js              # 考试 API
│       │   ├── scores.js             # 成绩 API
│       │   ├── questions.js          # 题目 API
│       │   └── dashboard.js          # 仪表盘 API
│       ├── stores/                   # Pinia 状态管理
│       │   └── auth.js               # 认证状态
│       ├── router/                   # 路由配置
│       │   └── index.js              # 路由定义 + 导航守卫
│       ├── layout/                   # 布局组件
│       │   └── MainLayout.vue        # 主布局（侧边栏 + 顶部导航栏）
│       └── views/                    # 页面组件
│           ├── Login.vue             # 登录页面
│           ├── Dashboard.vue         # 仪表盘
│           ├── Students.vue          # 学员管理
│           ├── Exams.vue             # 考试管理
│           ├── Scores.vue            # 成绩管理
│           └── Users.vue             # 用户管理（仅超级管理员）
├── student-frontend/                 # 学员前端 Vue3 应用（端口 3001）
│   ├── README.md                     # 学员端说明文档
│   ├── index.html                    # 入口 HTML
│   ├── package.json                  # 依赖配置
│   ├── vite.config.js                # Vite 配置（端口 3001，API 代理）
│   └── src/
│       ├── main.js                   # 应用入口
│       ├── App.vue                   # 根组件
│       ├── api/
│       │   ├── index.js              # Axios 实例和拦截器
│       │   └── student.js            # 学员 API
│       ├── stores/
│       │   └── auth.js               # 学员认证状态
│       ├── router/
│       │   └── index.js              # 路由配置
│       └── views/
│           ├── Login.vue             # 学员登录
│           ├── Register.vue          # 学员注册
│           ├── Home.vue              # 考试列表（待做/已完成）
│           ├── TakeExam.vue          # 在线答题
│           └── ExamResult.vue        # 答题结果
├── exam_manager.db                   # SQLite 数据库文件（首次启动自动生成）
├── requirements.txt                  # Python 依赖清单
└── README.md                         # 项目说明文档（本文件）
```

---

## 💾 数据库说明

- 本项目使用 **SQLite** 作为数据库，数据存储在项目根目录下的 `exam_manager.db` 文件中
- **无需额外安装数据库软件**，SQLite 数据库文件会在首次启动时自动创建
- 系统启动时会自动执行数据库迁移（为已有表添加新字段）
- 系统启动时会自动填充示例数据，包含：
  - 15 名学员
  - 7 场考试
  - 题目、成绩记录和报名记录
  - 1 个超级管理员账号（test / 123456）

**数据模型：**

| 模型 | 说明 |
|------|------|
| `Student` | 学员（含学号、密码哈希、登录令牌） |
| `Exam` | 考试 |
| `Question` | 题目（选择题/判断题/填空题/简答题） |
| `Score` | 成绩 |
| `ExamRegistration` | 考试报名 |
| `ExamAnswer` | 答题记录（学员在线提交的逐题答案） |
| `User` | 管理员用户（super_admin / admin） |

**如果想重置数据库：**

1. 先停止服务
2. 删除项目根目录下的 `exam_manager.db` 文件
3. 重新启动服务，系统会自动创建新数据库并填充示例数据

```bash
# Windows CMD 删除数据库文件
del exam_manager.db

# Linux / macOS
rm exam_manager.db
```

---

## ❓ 常见问题

### 1. `pip install` 安装依赖失败

**解决方案**：
```bash
# 升级 pip
python -m pip install --upgrade pip

# 使用国内镜像源安装
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2. `npm install` 安装依赖慢或失败

**解决方案**：
```bash
# 使用国内镜像源安装
npm install --registry=https://registry.npmmirror.com
```

### 3. 启动时报错 `ModuleNotFoundError: No module named 'app'`

**解决方案**：
```bash
# 确保在 exam_manager 目录下启动
cd d:\vscode\python\exam_manager
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 启动报错 `no such column: students.student_no`

**原因**：旧版数据库缺少新字段。

**解决方案**：系统已内置自动迁移逻辑，正常启动即可自动添加。如果仍有问题，删除 `exam_manager.db` 重新创建。

### 5. 端口被占用

```bash
# 查找占用端口的进程（Windows CMD）
netstat -ano | findstr :8000
taskkill /PID <进程ID> /F
```

### 6. 前端页面打开后数据加载失败

**排查步骤**：
1. 确认后端服务正在运行（终端显示 `Uvicorn running on http://0.0.0.0:8000`）
2. 在浏览器中访问 http://localhost:8000/health 确认后端正常
3. 如果后端使用非 8000 端口，需修改 `vite.config.js` 中的代理配置

### 7. PowerShell 虚拟环境激活失败

**报错信息**：`无法加载文件，因为在此系统上禁止运行脚本`

**解决方案**：以管理员身份打开 PowerShell，执行：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 8. bcrypt 安装失败

**解决方案**：确保系统已安装 C++ 编译工具。Windows 用户可安装 Microsoft Visual C++ Build Tools。

---

## 🛑 停止服务

- **停止学员前端**：在学员前端终端窗口中按下 `Ctrl + C`
- **停止管理员前端**：在管理员前端终端窗口中按下 `Ctrl + C`
- **停止后端**：在后端终端窗口中按下 `Ctrl + C`

> 或者通过命令强制关闭：
> ```bash
> # 查找并关闭所有服务（Windows CMD）
> netstat -ano | findstr "8000 3000 3001"
> taskkill /PID <进程ID> /F
> ```

> 如果使用了虚拟环境，停止服务后可以执行 `deactivate` 命令退出虚拟环境。
