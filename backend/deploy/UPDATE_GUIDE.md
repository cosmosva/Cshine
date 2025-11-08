# Cshine 后端更新指南 🔄

> 快速、安全、可回滚的更新流程

## 🚀 快速更新

### 一键更新（推荐）

```bash
# 1. 登录服务器
ssh cshine@your_server_ip

# 2. 运行更新脚本
cd ~/Cshine/backend
bash deploy/update.sh
```

**就是这么简单！** 🎉

脚本会自动完成：
- ✅ 备份当前代码和配置
- ✅ 拉取最新代码
- ✅ 更新依赖（如果有变化）
- ✅ 运行数据库迁移
- ✅ 重启服务
- ✅ 健康检查

**耗时**: 约 1-2 分钟

---

## 📋 三种更新方式

### 方式 1：标准更新 `update.sh`（最常用）

**适用场景**：正常的功能迭代、Bug 修复

```bash
bash deploy/update.sh
```

**特点**：
- 📦 拉取远程代码
- 🔄 自动检测依赖变化
- 🗄️ 运行数据库迁移
- ✅ 完整的健康检查
- 🔙 更新失败可回滚

---

### 方式 2：热修复 `hotfix.sh`（紧急修复）

**适用场景**：线上紧急修复，直接在服务器上改代码

```bash
bash deploy/hotfix.sh
```

**特点**：
- 🔥 不拉取远程代码
- ⚡ 仅重启服务
- 🎯 可选择性安装依赖/运行迁移
- ⏱️ 最快速度修复问题

**使用场景示例**：
```bash
# 1. 直接在服务器上修改代码
vim ~/Cshine/backend/app/api/flash.py

# 2. 热修复重启
bash deploy/hotfix.sh
```

---

### 方式 3：回滚 `rollback.sh`（出问题时）

**适用场景**：更新后发现问题，需要快速恢复

```bash
bash deploy/rollback.sh
```

**特点**：
- ⏮️ 回退到上一个版本
- 🔄 恢复依赖
- ✅ 自动重启服务
- 📊 显示当前版本

---

## 📖 详细更新流程

### 标准更新详细步骤

#### 1. 在本地开发并测试

```bash
# 本地开发
cd ~/your_local_project/Cshine

# 开发新功能...
# 测试...

# 提交代码
git add .
git commit -m "feat: 添加新功能"
git push origin main
```

#### 2. 登录生产服务器

```bash
ssh cshine@your_server_ip
```

#### 3. 运行更新脚本

```bash
cd ~/Cshine/backend
bash deploy/update.sh
```

#### 4. 查看更新过程

```
==========================================
  🚀 Cshine 后端更新
==========================================

📦 步骤 1/6: 备份当前代码...
✅ 备份完成: /home/cshine/backups/20251108_143025

📦 步骤 2/6: 拉取最新代码...
当前分支: main
remote: Enumerating objects: 5, done.
remote: Counting objects: 100% (5/5), done.
...
✅ 代码更新完成

📦 步骤 3/6: 更新依赖...
检测到依赖变化，正在更新...
✅ 依赖更新完成

📦 步骤 4/6: 运行数据库迁移...
找到 2 个迁移脚本
是否运行所有迁移？(y/N): y
✅ 迁移完成

📦 步骤 5/6: 重启服务...
等待服务启动...
✅ 服务启动成功

📦 步骤 6/6: 健康检查...
✅ 健康检查通过

==========================================
  🎉 更新完成！
==========================================
```

#### 5. 验证功能

```bash
# 查看服务状态
sudo systemctl status cshine-api

# 查看实时日志
tail -f ~/Cshine/backend/logs/cshine.log

# 测试 API
curl https://api.cshine.com/health
```

---

## 🔄 更新流程图

```
┌─────────────────┐
│  本地开发完成    │
│  提交并推送代码  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  登录生产服务器  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ bash update.sh  │
└────────┬────────┘
         │
         ├──► 备份当前代码
         ├──► 拉取最新代码
         ├──► 更新依赖
         ├──► 数据库迁移
         ├──► 重启服务
         └──► 健康检查
         │
         ▼
┌─────────────────┐
│   更新成功 ✅   │
└─────────────────┘
         │
    失败时 ❌
         │
         ▼
┌─────────────────┐
│bash rollback.sh │
└─────────────────┘
```

---

## 🛡️ 安全更新策略

### 1. 灰度发布（推荐）

**步骤**：
1. 先在测试服务器上验证
2. 在生产服务器低峰期更新
3. 监控日志和错误率
4. 逐步放量

### 2. 蓝绿部署（高级）

**需要两台服务器**：
- 🔵 **蓝环境**：当前运行版本
- 🟢 **绿环境**：新版本

**流程**：
1. 在绿环境部署新版本
2. 测试验证通过
3. 切换流量到绿环境
4. 蓝环境保留作为回滚备份

### 3. 金丝雀发布（高级）

**流程**：
1. 先更新一台服务器（金丝雀）
2. 引导 10% 流量到新版本
3. 监控 1-2 小时
4. 无问题后全量更新

---

## 📊 更新前检查清单

### 开发环境

- [ ] 本地测试通过
- [ ] 代码已提交到 Git
- [ ] 版本号已更新
- [ ] CHANGELOG 已更新
- [ ] 文档已同步

### 生产环境

- [ ] 检查当前服务状态正常
- [ ] 检查磁盘空间充足（至少 5GB）
- [ ] 确认数据库备份正常
- [ ] 选择低峰期更新
- [ ] 通知团队成员

### 更新后验证

- [ ] 服务状态正常
- [ ] 健康检查通过
- [ ] 核心功能测试
- [ ] 查看错误日志
- [ ] 监控性能指标

---

## 🔍 更新后监控

### 实时监控命令

```bash
# 查看服务状态
sudo systemctl status cshine-api

# 实时查看应用日志
tail -f ~/Cshine/backend/logs/cshine.log

# 实时查看系统日志
sudo journalctl -u cshine-api -f

# 查看 Nginx 访问日志
sudo tail -f /var/log/nginx/cshine_access.log

# 查看错误日志
sudo tail -f /var/log/nginx/cshine_error.log

# 监控系统资源
htop

# 监控网络流量
sudo nethogs
```

### 关键指标

| 指标 | 正常范围 | 查看命令 |
|------|---------|---------|
| CPU 使用率 | < 70% | `htop` |
| 内存使用率 | < 80% | `free -h` |
| 磁盘使用率 | < 80% | `df -h` |
| 响应时间 | < 500ms | 查看日志 |
| 错误率 | < 0.1% | 查看日志 |

---

## 🐛 常见更新问题

### Q1: 更新后服务无法启动

```bash
# 查看详细错误
sudo journalctl -u cshine-api -n 50

# 常见原因：
# 1. 环境变量缺失 - 检查 .env 文件
# 2. 依赖冲突 - 重新安装依赖
# 3. 端口占用 - 检查端口

# 快速回滚
bash deploy/rollback.sh
```

### Q2: 依赖安装失败

```bash
# 清理并重新安装
cd ~/Cshine/backend
source venv/bin/activate
pip cache purge
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
```

### Q3: 数据库迁移失败

```bash
# 查看数据库日志
sudo tail -f /var/log/postgresql/postgresql-*-main.log

# 检查数据库连接
psql -h localhost -U cshine_user -d cshine

# 手动运行迁移
cd ~/Cshine/backend
source venv/bin/activate
python migrations/xxx.py
```

### Q4: 更新后 API 响应慢

```bash
# 检查 workers 数量
sudo vim /etc/systemd/system/cshine-api.service
# 调整 --workers 参数

# 重启服务
sudo systemctl daemon-reload
sudo systemctl restart cshine-api

# 查看进程
ps aux | grep uvicorn
```

### Q5: Git 拉取代码冲突

```bash
# 如果有未提交的更改
cd ~/Cshine
git status

# 暂存本地更改
git stash

# 拉取代码
git pull origin main

# 恢复更改（如果需要）
git stash pop
```

---

## 📝 更新日志示例

创建 `~/Cshine/UPDATE_LOG.md` 记录每次更新：

```markdown
# 更新日志

## 2025-11-10 14:30 - v0.2.6

**更新内容**：
- 修复会议详情页音频播放问题
- 优化 AI 摘要生成逻辑
- 更新依赖包版本

**操作人**: cosmos
**耗时**: 2 分钟
**状态**: ✅ 成功

**验证**:
- [x] 健康检查通过
- [x] 会议上传功能正常
- [x] AI 摘要生成正常

---

## 2025-11-08 10:15 - v0.2.5

**更新内容**：
- 添加 5 种智能摘要类型
- 数据库添加新字段

**操作人**: cosmos
**耗时**: 5 分钟
**状态**: ✅ 成功

**注意事项**:
- 运行了数据库迁移
- 旧数据新字段为 NULL
```

---

## 🎯 最佳实践

### 1. 定期更新
- 📅 **每周固定时间**更新（如周三下午）
- 🌙 **选择低峰期**（如凌晨或下午）
- 📢 **提前通知**用户可能的短暂维护

### 2. 小步快跑
- 🔄 频繁发布小更新，而不是积累大量更改
- ✅ 每次更新只包含相关的修改
- 📊 更容易定位和回滚问题

### 3. 自动化测试
```bash
# 在更新脚本中添加自动化测试
cd ~/Cshine/backend
source venv/bin/activate
pytest tests/  # 如果有测试
```

### 4. 监控告警
- 📈 配置性能监控
- 🚨 设置错误告警
- 📧 邮件/钉钉通知

### 5. 文档同步
- 📝 更新 CHANGELOG
- 📖 更新 API 文档
- 💡 更新用户指南

---

## 🔧 自动化更新（高级）

### 设置定时自动更新（可选）

⚠️ **注意**：自动更新有风险，建议仅用于开发/测试环境

```bash
# 编辑定时任务
crontab -e

# 添加（每天凌晨 2 点自动更新）
0 2 * * * cd /home/cshine/Cshine/backend && bash deploy/update.sh >> /home/cshine/update.log 2>&1
```

### 使用 CI/CD（推荐）

**GitHub Actions 示例**：

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: cshine
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd ~/Cshine/backend
            bash deploy/update.sh
```

---

## 📞 获取帮助

**更新遇到问题？**

1. 查看本指南的"常见问题"部分
2. 查看 [DEPLOYMENT_GUIDE.md](../../DEPLOYMENT_GUIDE.md)
3. 查看服务器日志
4. 提交 GitHub Issue

---

## 🎉 总结

使用我们提供的脚本，后端更新非常简单：

```bash
# 标准更新（最常用）
bash deploy/update.sh

# 紧急热修复
bash deploy/hotfix.sh

# 出问题回滚
bash deploy/rollback.sh
```

**更新时间**: 1-2 分钟  
**停机时间**: < 5 秒  
**回滚时间**: < 30 秒  

---

**祝更新顺利！🚀**

**版本**: v1.0  
**更新日期**: 2025-11-08

