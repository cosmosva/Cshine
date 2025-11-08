# Cshine 部署脚本使用指南

本目录包含了自动化部署脚本，帮助你快速部署 Cshine 到生产服务器。

## 📂 脚本说明

| 脚本名称 | 用途 | 运行权限 |
|---------|------|---------|
| `server_setup.sh` | 服务器环境初始化（Python、Nginx、PostgreSQL） | root |
| `db_setup.sh` | 数据库配置 | root |
| `app_deploy.sh` | 应用部署（虚拟环境、依赖、迁移） | cshine 用户 |
| `setup_env.sh` | 环境变量配置 | cshine 用户 |
| `setup_systemd.sh` | Systemd 服务配置 | root |
| `setup_nginx.sh` | Nginx 反向代理配置 | root |
| `update.sh` | 一键更新（拉取代码、更新依赖、重启） ⭐ | cshine 用户 |
| `rollback.sh` | 快速回滚到上一版本 | cshine 用户 |
| `hotfix.sh` | 热修复（不拉代码，仅重启） | cshine 用户 |

## 🚀 快速部署流程

### 第一步：服务器环境初始化

以 root 用户登录服务器：

```bash
ssh root@your_server_ip
```

下载项目代码：

```bash
cd /tmp
git clone https://github.com/your-username/Cshine.git
cd Cshine/backend/deploy
```

运行环境安装脚本：

```bash
chmod +x *.sh
sudo bash server_setup.sh
```

这个脚本会安装：
- Python 3.11
- PostgreSQL
- Nginx
- Certbot
- 其他必要工具

并创建 `cshine` 用户。

### 第二步：配置数据库

```bash
sudo bash db_setup.sh
```

按提示输入数据库密码，脚本会自动创建数据库和用户。

### 第三步：切换到 cshine 用户

```bash
su - cshine
```

克隆代码（如果还没有）：

```bash
cd ~
git clone https://github.com/your-username/Cshine.git
cd Cshine/backend
```

### 第四步：部署应用

```bash
chmod +x deploy/*.sh
bash deploy/app_deploy.sh
```

这个脚本会：
1. 创建虚拟环境
2. 安装依赖
3. 配置环境变量（交互式输入）
4. 运行数据库迁移
5. 配置 Systemd 服务

**按提示输入以下信息**：
- 数据库密码
- 微信小程序 AppID 和 AppSecret
- 阿里云 OSS 配置
- 通义听悟配置

### 第五步：配置 Nginx

```bash
sudo bash deploy/setup_nginx.sh
```

输入你的 API 域名（如：`api.cshine.com`）。

### 第六步：申请 SSL 证书

```bash
sudo certbot --nginx -d api.cshine.com
```

按提示输入邮箱，同意服务条款。

### 第七步：验证部署

```bash
# 检查服务状态
sudo systemctl status cshine-api

# 测试 API
curl https://api.cshine.com/health

# 预期输出：
# {"status":"ok","message":"Service is running"}
```

## 🔧 常用命令

### 服务管理

```bash
# 启动服务
sudo systemctl start cshine-api

# 停止服务
sudo systemctl stop cshine-api

# 重启服务
sudo systemctl restart cshine-api

# 查看状态
sudo systemctl status cshine-api

# 查看日志
sudo journalctl -u cshine-api -f
```

### 应用更新 ⭐

```bash
# 🚀 一键更新（推荐）
bash deploy/update.sh

# 🔥 紧急热修复（服务器上直接改代码后用）
bash deploy/hotfix.sh

# ⏮️ 快速回滚
bash deploy/rollback.sh
```

**详细更新指南**: 查看 [UPDATE_GUIDE.md](UPDATE_GUIDE.md)

### Nginx 管理

```bash
# 测试配置
sudo nginx -t

# 重载配置
sudo systemctl reload nginx

# 重启 Nginx
sudo systemctl restart nginx

# 查看日志
sudo tail -f /var/log/nginx/cshine_access.log
sudo tail -f /var/log/nginx/cshine_error.log
```

## 🐛 故障排查

### 服务无法启动

```bash
# 查看详细错误
sudo journalctl -u cshine-api -n 50

# 检查端口占用
sudo lsof -i :8000

# 手动测试
cd ~/Cshine/backend
source venv/bin/activate
python main.py
```

### 数据库连接失败

```bash
# 检查 PostgreSQL 状态
sudo systemctl status postgresql

# 测试连接
psql -h localhost -U cshine_user -d cshine

# 查看日志
sudo tail -f /var/log/postgresql/postgresql-*-main.log
```

### SSL 证书问题

```bash
# 检查证书
sudo certbot certificates

# 强制续期
sudo certbot renew --force-renewal

# 重启 Nginx
sudo systemctl reload nginx
```

## 📋 部署检查清单

- [ ] 服务器环境安装完成
- [ ] 数据库配置完成
- [ ] 应用部署完成
- [ ] Systemd 服务运行正常
- [ ] Nginx 配置完成
- [ ] SSL 证书申请成功
- [ ] 健康检查接口正常
- [ ] 域名解析正确
- [ ] 微信小程序服务器域名配置完成

## ⚠️ 安全建议

1. **不要使用 root 用户运行应用**
   - 使用 cshine 用户运行服务

2. **保护敏感文件**
   ```bash
   chmod 600 ~/Cshine/backend/.env
   ```

3. **定期更新系统**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

4. **配置防火墙**
   ```bash
   sudo ufw status
   ```

5. **定期备份数据库**
   - 已在部署指南中配置了自动备份脚本

## 📚 相关文档

- [完整部署指南](../../DEPLOYMENT_GUIDE.md)
- [后端 README](../README.md)
- [故障排查](../TROUBLESHOOTING.md)

## 💡 提示

- 所有脚本都添加了错误检查（`set -e`）
- 遇到错误会自动停止，不会继续执行
- 可以多次运行脚本，会自动跳过已完成的步骤
- 建议在测试服务器上先运行一遍，熟悉流程

---

**祝部署顺利！🚀**

