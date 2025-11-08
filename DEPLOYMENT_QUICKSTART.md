# Cshine 部署快速指南 ⚡

> 5 步快速部署到生产服务器

## 📋 前置准备

### 需要购买/准备的资源

| 资源 | 推荐方案 | 预估费用 |
|------|---------|---------|
| 云服务器 | 阿里云 ECS 2核4GB | ¥100/月 |
| 域名 | .com 域名 | ¥60/年 |
| SSL 证书 | Let's Encrypt（免费） | ¥0 |
| 阿里云 OSS | 标准存储 | 按量付费 |
| 通义听悟 | API 调用 | 按量付费 |

**总计**: 约 ¥100-150/月

### 检查清单

- [ ] 已购买云服务器
- [ ] 已购买域名
- [ ] 域名已完成备案（必须！）
- [ ] 域名已解析到服务器 IP
- [ ] 已有阿里云 OSS 配置
- [ ] 已有通义听悟 API 密钥
- [ ] 已有微信小程序 AppID 和 AppSecret

---

## 🚀 部署步骤

### Step 1️⃣ : 服务器环境初始化

**用时**: 约 10-15 分钟

```bash
# SSH 登录服务器
ssh root@your_server_ip

# 下载代码
git clone https://github.com/your-username/Cshine.git
cd Cshine/backend/deploy

# 运行环境安装脚本
chmod +x *.sh
sudo bash server_setup.sh
```

**这个脚本会安装**：Python 3.11、PostgreSQL、Nginx、Certbot

---

### Step 2️⃣ : 配置数据库

**用时**: 约 2 分钟

```bash
sudo bash db_setup.sh
```

按提示输入数据库密码（请记住，后面要用）。

---

### Step 3️⃣ : 部署应用

**用时**: 约 5-10 分钟

```bash
# 切换到 cshine 用户
su - cshine

# 进入项目目录
cd ~/Cshine/backend

# 运行部署脚本
bash deploy/app_deploy.sh
```

**按提示输入以下信息**：
- ✅ 数据库密码
- ✅ 微信小程序 AppID 和 AppSecret
- ✅ 阿里云 OSS 配置（AccessKeyId、AccessKeySecret、Bucket、Endpoint）
- ✅ 通义听悟配置（AppKey、AccessKeyId、AccessKeySecret）

---

### Step 4️⃣ : 配置 Nginx + SSL

**用时**: 约 5 分钟

```bash
# 配置 Nginx
sudo bash deploy/setup_nginx.sh
# 输入域名：api.cshine.com

# 申请 SSL 证书
sudo certbot --nginx -d api.cshine.com
# 输入邮箱，同意条款
```

---

### Step 5️⃣ : 验证部署

**用时**: 约 2 分钟

```bash
# 检查服务状态
sudo systemctl status cshine-api

# 测试 API（本地）
curl http://127.0.0.1:8000/health

# 测试 API（外网）
curl https://api.cshine.com/health
```

**预期输出**：
```json
{"status":"ok","message":"Service is running"}
```

✅ **如果看到这个输出，说明部署成功！**

---

## 📱 微信小程序配置

### 修改前端 API 地址

编辑 `utils/config.js`：

```javascript
const ENV = 'production';

const API_CONFIG = {
  production: {
    baseURL: 'https://api.cshine.com',  // 改成你的域名
  }
};
```

### 配置服务器域名白名单

登录微信公众平台：https://mp.weixin.qq.com/

进入"开发" → "开发管理" → "开发设置" → "服务器域名"

**request 合法域名**：
```
https://api.cshine.com
```

**uploadFile 合法域名**：
```
https://api.cshine.com
https://your-bucket.oss-cn-hangzhou.aliyuncs.com
```

**downloadFile 合法域名**：
```
https://api.cshine.com
https://your-bucket.oss-cn-hangzhou.aliyuncs.com
```

### 上传小程序代码

1. 在微信开发者工具中打开项目
2. 修改 `project.config.json` 中的 `appid`
3. 点击"上传"按钮
4. 填写版本号（如：v1.0.0）
5. 提交审核

---

## 🔧 常用命令

### 服务管理

```bash
# 查看状态
sudo systemctl status cshine-api

# 重启服务
sudo systemctl restart cshine-api

# 查看日志
sudo journalctl -u cshine-api -f

# 查看应用日志
tail -f ~/Cshine/backend/logs/cshine.log
```

### 代码更新

```bash
# 切换到 cshine 用户
su - cshine

# 拉取最新代码
cd ~/Cshine
git pull origin main

# 重启服务
sudo systemctl restart cshine-api
```

### Nginx 管理

```bash
# 重载配置
sudo systemctl reload nginx

# 查看访问日志
sudo tail -f /var/log/nginx/cshine_access.log

# 查看错误日志
sudo tail -f /var/log/nginx/cshine_error.log
```

---

## 🐛 常见问题

### Q1: 服务无法启动？

```bash
# 查看错误日志
sudo journalctl -u cshine-api -n 50

# 检查环境变量
cat ~/Cshine/backend/.env

# 手动测试
cd ~/Cshine/backend
source venv/bin/activate
python main.py
```

### Q2: 数据库连接失败？

```bash
# 检查 PostgreSQL
sudo systemctl status postgresql

# 测试连接
psql -h localhost -U cshine_user -d cshine
```

### Q3: Nginx 502 错误？

```bash
# 检查 FastAPI 是否运行
sudo systemctl status cshine-api

# 查看 Nginx 错误
sudo tail -f /var/log/nginx/cshine_error.log
```

### Q4: SSL 证书过期？

```bash
# 手动续期
sudo certbot renew

# 重启 Nginx
sudo systemctl reload nginx
```

### Q5: 微信小程序请求失败？

1. 检查域名是否在白名单
2. 检查域名是否使用 HTTPS
3. 检查域名是否备案
4. 在开发者工具中查看详细错误

---

## 📊 监控指标

### 服务器资源

```bash
# CPU 和内存
htop

# 磁盘使用
df -h

# 网络流量
sudo nethogs
```

### 应用性能

```bash
# 查看进程
ps aux | grep uvicorn

# 查看端口
sudo lsof -i :8000

# 查看连接数
sudo netstat -antp | grep 8000 | wc -l
```

---

## 🔐 安全建议

1. **定期更新系统**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **修改 SSH 端口**（可选）
   ```bash
   sudo vim /etc/ssh/sshd_config
   # Port 22 改为其他端口
   ```

3. **配置 fail2ban**（防止暴力破解）
   ```bash
   sudo apt install fail2ban -y
   ```

4. **定期备份数据库**
   ```bash
   # 已配置自动备份，检查：
   crontab -l
   ```

5. **监控日志文件**
   ```bash
   # 查看可疑访问
   sudo tail -f /var/log/nginx/cshine_access.log | grep -v "200"
   ```

---

## 📚 完整文档

- 📖 [完整部署指南](DEPLOYMENT_GUIDE.md) - 详细的部署说明
- 🔧 [部署脚本说明](backend/deploy/README.md) - 脚本使用指南
- 🐛 [故障排查](backend/TROUBLESHOOTING.md) - 问题解决方案
- 📝 [后端 README](backend/README.md) - API 文档

---

## 🎯 部署检查清单

**服务器准备**
- [ ] 云服务器已购买
- [ ] 域名已购买并备案
- [ ] DNS 解析已配置

**环境安装**
- [ ] Python 3.11 安装成功
- [ ] PostgreSQL 安装并运行
- [ ] Nginx 安装并运行
- [ ] 防火墙配置完成

**应用部署**
- [ ] 代码拉取成功
- [ ] 虚拟环境创建
- [ ] 依赖安装完成
- [ ] 环境变量配置
- [ ] 数据库迁移完成
- [ ] Systemd 服务运行

**网络配置**
- [ ] Nginx 反向代理配置
- [ ] SSL 证书申请成功
- [ ] HTTPS 访问正常
- [ ] 健康检查接口正常

**小程序配置**
- [ ] API 地址修改
- [ ] 服务器域名配置
- [ ] 代码上传成功
- [ ] 审核提交

---

## 💰 成本预估

### 初期（1-100 用户）

| 项目 | 费用 |
|------|------|
| 服务器（2核4GB） | ¥100/月 |
| 域名 | ¥60/年 |
| OSS 存储（10GB） | ¥2/月 |
| 通义听悟（100小时） | ¥30/月 |
| **总计** | **约 ¥135/月** |

### 发展期（100-1000 用户）

| 项目 | 费用 |
|------|------|
| 服务器（4核8GB） | ¥200/月 |
| OSS 存储（100GB） | ¥20/月 |
| 通义听悟（500小时） | ¥150/月 |
| CDN 流量 | ¥50/月 |
| **总计** | **约 ¥420/月** |

---

## 📞 获取帮助

- 📖 查看完整文档：[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- 🐛 提交问题：[GitHub Issues](https://github.com/your-username/Cshine/issues)
- 💬 讨论交流：[GitHub Discussions](https://github.com/your-username/Cshine/discussions)

---

**祝部署顺利！🚀**

**下一步**：部署完成后，建议先做小范围测试，验证所有功能正常后再正式上线。

