# Cshine 快速参考卡片 ⚡

> 服务器上常用命令速查表

## 🚀 更新部署

```bash
# 标准更新（最常用）
bash deploy/update.sh

# 紧急热修复
bash deploy/hotfix.sh

# 快速回滚
bash deploy/rollback.sh
```

---

## 🔧 服务管理

```bash
# 启动服务
sudo systemctl start cshine-api

# 停止服务
sudo systemctl stop cshine-api

# 重启服务
sudo systemctl restart cshine-api

# 重载配置
sudo systemctl reload cshine-api

# 查看状态
sudo systemctl status cshine-api

# 开机自启
sudo systemctl enable cshine-api
```

---

## 📝 日志查看

```bash
# 实时查看应用日志
tail -f ~/Cshine/backend/logs/cshine.log

# 实时查看系统日志
sudo journalctl -u cshine-api -f

# 查看最近 50 行日志
sudo journalctl -u cshine-api -n 50

# 查看 Nginx 访问日志
sudo tail -f /var/log/nginx/cshine_access.log

# 查看 Nginx 错误日志
sudo tail -f /var/log/nginx/cshine_error.log

# 查看错误日志（仅错误）
sudo journalctl -u cshine-api -p err -n 30
```

---

## 🗄️ 数据库操作

```bash
# 连接数据库
psql -h localhost -U cshine_user -d cshine

# 数据库备份
PGPASSWORD='your_password' pg_dump -h localhost -U cshine_user cshine > backup.sql

# 数据库恢复
PGPASSWORD='your_password' psql -h localhost -U cshine_user -d cshine < backup.sql

# 查看数据库大小
psql -h localhost -U cshine_user -d cshine -c "SELECT pg_size_pretty(pg_database_size('cshine'));"
```

---

## 🌐 Nginx 操作

```bash
# 测试配置
sudo nginx -t

# 重载配置
sudo systemctl reload nginx

# 重启 Nginx
sudo systemctl restart nginx

# 查看 Nginx 状态
sudo systemctl status nginx

# 查看配置文件
sudo vim /etc/nginx/sites-available/cshine
```

---

## 🔐 SSL 证书

```bash
# 查看证书信息
sudo certbot certificates

# 手动续期
sudo certbot renew

# 强制续期
sudo certbot renew --force-renewal

# 测试续期（不实际续期）
sudo certbot renew --dry-run
```

---

## 📊 系统监控

```bash
# 查看系统资源
htop

# 查看磁盘使用
df -h

# 查看内存使用
free -h

# 查看进程
ps aux | grep uvicorn

# 查看端口占用
sudo lsof -i :8000
sudo lsof -i :443

# 查看网络连接
sudo netstat -tuln

# 查看网络流量
sudo nethogs
```

---

## 🧹 日志清理

```bash
# 清理 journal 日志（保留最近 7 天）
sudo journalctl --vacuum-time=7d

# 清理应用日志（保留最近 14 天）
find ~/Cshine/backend/logs -name "*.log" -mtime +14 -delete

# 清理 Nginx 日志
sudo rm /var/log/nginx/*.log.*.gz
```

---

## 🔍 故障排查

```bash
# 检查服务是否运行
sudo systemctl is-active cshine-api

# 查看服务启动时间
sudo systemctl show cshine-api --property=ActiveEnterTimestamp

# 检查配置文件
cat ~/Cshine/backend/.env

# 测试 API
curl http://127.0.0.1:8000/health
curl https://api.cshine.com/health

# 查看环境变量
sudo systemctl show cshine-api --property=Environment

# 检查 Python 版本
python3.11 --version

# 检查依赖
cd ~/Cshine/backend
source venv/bin/activate
pip list
```

---

## 📦 代码管理

```bash
# 查看当前分支
cd ~/Cshine
git branch

# 查看最近提交
git log --oneline -10

# 查看文件变化
git status

# 拉取最新代码
git pull origin main

# 查看远程地址
git remote -v

# 重置到某个版本
git reset --hard <commit_hash>
```

---

## 🔑 环境变量

```bash
# 查看 .env 文件
cat ~/Cshine/backend/.env

# 编辑 .env 文件
vim ~/Cshine/backend/.env

# 重启服务使环境变量生效
sudo systemctl restart cshine-api
```

---

## 🔒 安全检查

```bash
# 查看防火墙状态
sudo ufw status

# 查看登录历史
last -20

# 查看失败的登录尝试
sudo grep "Failed password" /var/log/auth.log | tail -20

# 查看进程
ps aux | grep cshine
```

---

## 📈 性能优化

```bash
# 调整 workers 数量
sudo vim /etc/systemd/system/cshine-api.service
# 修改 --workers 参数

# 重载配置
sudo systemctl daemon-reload
sudo systemctl restart cshine-api

# 查看并发连接数
sudo netstat -antp | grep 8000 | grep ESTABLISHED | wc -l
```

---

## 🚨 紧急操作

```bash
# 立即停止服务
sudo systemctl stop cshine-api

# 快速回滚
cd ~/Cshine/backend
bash deploy/rollback.sh

# 查看最近错误
sudo journalctl -u cshine-api -p err -n 20 --no-pager

# 重启所有服务
sudo systemctl restart cshine-api
sudo systemctl reload nginx
```

---

## 📞 关键文件路径

```
配置文件:
  - 应用配置: ~/Cshine/backend/.env
  - Systemd 服务: /etc/systemd/system/cshine-api.service
  - Nginx 配置: /etc/nginx/sites-available/cshine

日志文件:
  - 应用日志: ~/Cshine/backend/logs/cshine.log
  - 系统日志: sudo journalctl -u cshine-api
  - Nginx 访问: /var/log/nginx/cshine_access.log
  - Nginx 错误: /var/log/nginx/cshine_error.log

数据文件:
  - 数据库: PostgreSQL (端口 5432)
  - 上传文件: ~/Cshine/backend/uploads/
  - 备份文件: ~/backups/

部署脚本:
  - ~/Cshine/backend/deploy/update.sh
  - ~/Cshine/backend/deploy/rollback.sh
  - ~/Cshine/backend/deploy/hotfix.sh
```

---

## 💡 快速提示

1. **更新前务必备份**（update.sh 会自动备份）
2. **查看日志是排查问题的第一步**
3. **重启服务后检查健康状态**
4. **定期清理日志文件释放空间**
5. **保持 .env 文件安全（chmod 600）**

---

**快速帮助**: `cat ~/Cshine/backend/QUICKREF.md`

**完整文档**: 
- 部署指南: `~/Cshine/DEPLOYMENT_GUIDE.md`
- 更新指南: `~/Cshine/backend/deploy/UPDATE_GUIDE.md`

