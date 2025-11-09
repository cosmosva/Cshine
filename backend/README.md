# Cshine 后端 API

> FastAPI + PostgreSQL + SQLAlchemy

## 📚 项目结构

```
backend/
├── main.py                  # 应用入口
├── config.py                # 配置管理
├── requirements.txt         # 依赖列表
├── .env.example            # 环境变量示例
├── .gitignore              # Git 忽略文件
├── app/
│   ├── __init__.py
│   ├── database.py         # 数据库连接
│   ├── models.py           # 数据库模型
│   ├── schemas.py          # Pydantic schemas
│   ├── dependencies.py     # FastAPI 依赖项
│   ├── api/                # API 路由
│   │   ├── __init__.py
│   │   ├── auth.py         # 认证相关
│   │   ├── flash.py        # 闪记相关
│   │   └── upload.py       # 文件上传
│   └── utils/              # 工具类
│       ├── __init__.py
│       ├── jwt.py          # JWT 工具
│       └── wechat.py       # 微信工具
└── logs/                   # 日志目录
```

## 🚀 快速开始（5分钟）

### 1. 安装依赖

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 创建 .env 文件
cat > .env << EOF
APP_NAME=Cshine API
DEBUG=True
SECRET_KEY=your-secret-key-for-development
DATABASE_URL=sqlite:///./cshine.db
WECHAT_APPID=your_appid
WECHAT_SECRET=your_secret
CORS_ORIGINS=*
EOF
```

### 3. 运行应用

```bash
python main.py
# 应用会在 http://localhost:8000 启动
```

### 4. 访问 API 文档

```
http://localhost:8000/docs       # Swagger UI
http://localhost:8000/redoc      # ReDoc
```

**详细配置说明**：见 [部署文档](../docs/deployment/DEPLOYMENT_GUIDE.md)

## 📡 API 接口

### 认证相关

#### POST /api/v1/auth/login
微信小程序登录

**请求**:
```json
{
  "code": "微信登录凭证",
  "nickname": "用户昵称",
  "avatar": "头像URL"
}
```

**响应**:
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "token": "JWT Token",
    "user_id": "用户ID",
    "is_new_user": true
  }
}
```

---

### 闪记相关

#### POST /api/v1/flash/create
创建闪记

**Headers**:
```
Authorization: Bearer <token>
```

**请求**:
```json
{
  "title": "标题",
  "content": "转写的文字内容",
  "summary": "AI生成的摘要",
  "keywords": ["关键词1", "关键词2"],
  "category": "工作",
  "audio_url": "音频文件URL",
  "audio_duration": 120
}
```

**响应**:
```json
{
  "code": 200,
  "message": "创建成功",
  "data": {
    "id": "闪记ID",
    "title": "标题",
    "content": "内容",
    ...
  }
}
```

#### GET /api/v1/flash/list
获取闪记列表

**参数**:
- `page`: 页码（默认1）
- `page_size`: 每页数量（默认20）
- `category`: 分类筛选
- `keyword`: 关键词搜索
- `is_favorite`: 仅收藏

**响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 100,
    "page": 1,
    "page_size": 20,
    "items": [...]
  }
}
```

#### GET /api/v1/flash/{flash_id}
获取闪记详情

#### PUT /api/v1/flash/{flash_id}
更新闪记

#### DELETE /api/v1/flash/{flash_id}
删除闪记

#### PUT /api/v1/flash/{flash_id}/favorite
切换收藏状态

---

### 文件上传

#### POST /api/v1/upload/audio
上传音频文件

**请求**: `multipart/form-data`
- `file`: 音频文件（mp3/m4a/wav/amr）

**响应**:
```json
{
  "code": 200,
  "message": "上传成功",
  "data": {
    "file_url": "文件URL",
    "file_size": 1024000,
    "duration": 120,
    "task_id": "异步任务ID"
  }
}
```

## 🗄️ 数据库设计

### 用户表 (users)
- `id`: UUID, 主键
- `openid`: 微信 openid
- `unionid`: 微信 unionid
- `nickname`: 昵称
- `avatar`: 头像
- `created_at`: 注册时间
- `last_login`: 最后登录
- `is_active`: 是否激活
- `subscription_tier`: 订阅等级

### 闪记表 (flashes)
- `id`: UUID, 主键
- `user_id`: 用户ID（外键）
- `title`: 标题
- `content`: 内容
- `summary`: 摘要
- `keywords`: 关键词（JSONB）
- `category`: 分类
- `audio_url`: 音频URL
- `audio_duration`: 音频时长
- `is_favorite`: 是否收藏
- `created_at`: 创建时间
- `updated_at`: 更新时间

### 会议表 (meetings)
- `id`: UUID, 主键
- `user_id`: 用户ID（外键）
- `title`: 会议主题
- `participants`: 参会人（JSONB）
- `meeting_date`: 会议日期
- `audio_url`: 音频URL
- `audio_duration`: 音频时长
- `transcript`: 完整转写
- `summary`: 摘要
- `key_points`: 讨论要点（JSONB）
- `action_items`: 行动项（JSONB）
- `status`: 处理状态
- `created_at`: 创建时间

## 🔐 认证说明

所有需要认证的接口都需要在 Header 中携带 JWT Token：

```
Authorization: Bearer <your_jwt_token>
```

Token 有效期：7 天

## 🧪 开发工具

### 格式化代码
```bash
black app/
```

### 代码检查
```bash
flake8 app/
```

### 运行测试
```bash
pytest
```

## 📦 部署

### 使用 Docker（推荐）

```bash
# 构建镜像
docker build -t cshine-api .

# 运行容器
docker run -d \
  -p 8000:8000 \
  --env-file .env \
  --name cshine-api \
  cshine-api
```

### 直接部署

```bash
# 安装依赖
pip install -r requirements.txt

# 使用 gunicorn 运行
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

## ⚠️ 注意事项

1. **生产环境配置**
   - 修改 `SECRET_KEY` 为随机强密钥
   - 使用 PostgreSQL 而非 SQLite
   - 配置 HTTPS
   - 启用日志记录

2. **微信小程序配置**
   - 需要在微信公众平台配置服务器域名
   - 域名必须使用 HTTPS

3. **文件存储**
   - 生产环境建议使用 OSS/COS
   - 本地存储仅用于开发测试

## 🔗 相关链接

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
- [微信小程序开发文档](https://developers.weixin.qq.com/miniprogram/dev/framework/)

## 📝 待办事项

- [ ] 集成 ASR 语音识别服务
- [ ] 集成 LLM 大模型
- [ ] 实现 Celery 异步任务
- [ ] 添加单元测试
- [ ] 添加 API 限流
- [ ] 实现会议纪要功能
- [ ] 添加搜索功能
- [ ] 性能优化

---

**开发者**: Cshine Team  
**版本**: v1.0.0  
**更新日期**: 2025-11-07

