# 🚨 手动执行数据库迁移指南

如果自动脚本失败，请按照以下步骤手动执行迁移。

---

## 方法 1：直接使用 Python 执行（推荐）

```bash
# 1. 进入 backend 目录
cd ~/Cshine/backend

# 2. 查找 Python
which python3
# 或
which python

# 3. 直接执行迁移脚本（使用找到的 Python）
python3 migrations/add_folders_and_folder_id_postgres.py
# 或
python migrations/add_folders_and_folder_id_postgres.py

# 4. 重启服务
sudo systemctl restart cshine-api

# 5. 验证
sudo systemctl status cshine-api
curl http://localhost:8000/health
```

---

## 方法 2：使用正在运行的 Python 环境

```bash
# 1. 查看当前运行的 Python 路径
ps aux | grep uvicorn | grep -v grep

# 输出示例：
# cshine   12345  ... /path/to/python /path/to/uvicorn ...

# 2. 使用相同的 Python 执行迁移
/path/to/python ~/Cshine/backend/migrations/add_folders_and_folder_id_postgres.py

# 3. 重启服务
sudo systemctl restart cshine-api
```

---

## 方法 3：直接连接数据库执行 SQL（最直接）

```bash
# 1. 连接到 PostgreSQL
psql -U <your_db_user> -d <your_db_name>

# 2. 执行以下 SQL：

-- 创建 folders 表
CREATE TABLE IF NOT EXISTS folders (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    name VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_folders_user_id ON folders(user_id);

-- 检查 folder_id 字段是否存在
SELECT column_name 
FROM information_schema.columns 
WHERE table_name='meetings' AND column_name='folder_id';

-- 如果不存在，添加字段
ALTER TABLE meetings ADD COLUMN folder_id INTEGER;

-- 添加外键约束
ALTER TABLE meetings 
ADD CONSTRAINT fk_meetings_folder_id 
FOREIGN KEY (folder_id) REFERENCES folders(id) ON DELETE SET NULL;

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_meetings_folder_id ON meetings(folder_id);

-- 退出
\q

# 3. 重启服务
sudo systemctl restart cshine-api
```

---

## 方法 4：查看数据库配置后手动连接

```bash
# 1. 查看数据库配置
cd ~/Cshine/backend
cat .env | grep DATABASE

# 2. 根据配置连接数据库
# 格式：postgresql://用户名:密码@主机:端口/数据库名

# 3. 使用 psql 连接
psql postgresql://用户名:密码@主机:端口/数据库名

# 4. 执行上面方法 3 中的 SQL
```

---

## 验证迁移成功

```bash
# 1. 连接数据库
psql -U <user> -d <database>

# 2. 检查 folders 表
\d folders

# 3. 检查 meetings 表的 folder_id 字段
\d meetings

# 4. 退出
\q
```

---

## 如果遇到权限问题

```bash
# 如果提示权限不足，可能需要使用 postgres 超级用户
sudo -u postgres psql -d <database_name>

# 然后执行 SQL
```

---

## 最简单的一键命令

```bash
cd ~/Cshine/backend && python3 migrations/add_folders_and_folder_id_postgres.py && sudo systemctl restart cshine-api && sudo systemctl status cshine-api
```

---

## 故障排查

### 问题 1：找不到 Python
```bash
# 安装 Python3
sudo apt update
sudo apt install python3 python3-pip
```

### 问题 2：缺少依赖包
```bash
# 安装依赖
pip3 install sqlalchemy psycopg2-binary loguru python-dotenv
```

### 问题 3：数据库连接失败
```bash
# 检查数据库配置
cat ~/Cshine/backend/.env | grep DATABASE

# 测试数据库连接
psql -U <user> -d <database> -c "SELECT 1;"
```

---

**选择最适合你的方法执行即可！** 🚀

