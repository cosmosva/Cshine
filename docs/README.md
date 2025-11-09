# 📚 Cshine 文档结构说明

> 文档分类管理，保持项目整洁有序

---

## 📂 文档结构

```
docs/
├── core/                    # 核心文档（永久保留）
│   ├── README.md            # 项目说明
│   ├── CHANGELOG.md         # 版本更新记录
│   └── PRD-完善版.md        # 产品需求文档
│
├── deployment/              # 部署相关（运维必读）
│   ├── DEPLOYMENT_GUIDE.md  # 完整部署指南
│   ├── BACKEND_UPDATE_PROTOCOL.md    # 后端更新协议
│   ├── BACKEND_UPDATE_QUICKSTART.md  # 快速上手
│   ├── LOGIN.md             # 登录功能文档
│   ├── OSS_ENVIRONMENT_SETUP.md      # OSS 环境配置
│   ├── UPDATE_SERVER.sh     # 服务器更新脚本
│   └── DEBUG_LOGIN.sh       # 登录诊断脚本
│
├── features/                # 功能文档（待清理区）
│   └── DEPLOY_*.md          # 具体功能的部署文档
│                            # 说明：3个月后移到 archive/
│
└── archive/                 # 历史归档（可清理）
    ├── DEPLOYMENT_CHECKLIST.md
    ├── DEPLOYMENT_REPORT.md
    ├── PRODUCTION_DEPLOYMENT_GUIDE.md
    ├── RELEASE_v0.4.5.md
    ├── UPLOAD_FEATURE_IMPLEMENTATION.md
    └── UPLOAD_FEATURE_PLAN.md
```

---

## 📋 文档分类说明

### 1️⃣ core/ - 核心文档
**用途**：项目的核心文档，永久保留  
**维护**：随项目发展持续更新  
**删除规则**：永不删除

**包含文档**：
- `README.md` - 项目说明，所有人的入口
- `CHANGELOG.md` - 版本历史，记录所有重要变更
- `PRD-完善版.md` - 产品需求，功能规划的依据

---

### 2️⃣ deployment/ - 部署文档
**用途**：部署、运维相关的重要文档  
**维护**：保持最新，定期检查更新  
**删除规则**：永久保留，但会持续优化

**包含文档**：
- `DEPLOYMENT_GUIDE.md` - 完整的生产环境部署指南
- `BACKEND_UPDATE_PROTOCOL.md` - 后端更新标准化协议
- `BACKEND_UPDATE_QUICKSTART.md` - 更新协议快速上手
- `LOGIN.md` - 登录功能的配置和使用
- `OSS_ENVIRONMENT_SETUP.md` - OSS 环境隔离配置
- `UPDATE_SERVER.sh` - 自动化更新脚本
- `DEBUG_LOGIN.sh` - 登录问题诊断工具

---

### 3️⃣ features/ - 功能文档（待清理区）
**用途**：具体功能的临时性部署文档  
**维护**：新功能发布时创建  
**删除规则**：3 个月后移到 archive/

**文档命名规范**：
```
DEPLOY_<功能名>_YYYYMMDD.md

示例：
DEPLOY_MEETING_FEATURE_20251109.md
DEPLOY_AUTH_FIX_20251110.md
```

**清理流程**：
1. 每月检查一次
2. 超过 3 个月的文档移到 `archive/`
3. 超过 1 年的可以删除

---

### 4️⃣ archive/ - 历史归档
**用途**：过期的、临时性的、一次性的文档  
**维护**：不维护，只归档  
**删除规则**：可随时清理

**包含内容**：
- 过期的部署报告
- 发布说明（已整合到 CHANGELOG）
- 功能实现文档（代码已完成）
- 临时性的检查清单
- 重复的历史文档

**清理建议**：
- 每季度检查一次
- 超过 6 个月的可以删除
- 或整体打包压缩保存

---

## 🔄 文档生命周期

```
┌─────────────────┐
│  功能开发中      │
│  (无文档)        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  功能完成        │
│  创建部署文档    │ ← 存放到 features/
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  3 个月后        │
│  移到 archive/   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  1 年后          │
│  可以删除        │
└─────────────────┘
```

---

## 📝 创建新文档的规则

### 规则 1：选择正确的位置

| 文档类型 | 存放位置 | 示例 |
|---------|---------|------|
| 项目说明、PRD | `core/` | README.md |
| 部署、运维指南 | `deployment/` | DEPLOYMENT_GUIDE.md |
| 功能部署文档 | `features/` | DEPLOY_xxx.md |
| 临时报告、计划 | `archive/` | FEATURE_PLAN.md |

### 规则 2：命名规范

**核心文档**：使用描述性名称
```
README.md
CHANGELOG.md
PRD-完善版.md
```

**部署文档**：功能 + 类型
```
DEPLOYMENT_GUIDE.md
LOGIN.md
OSS_ENVIRONMENT_SETUP.md
```

**功能文档**：DEPLOY + 功能名 + 日期
```
DEPLOY_MEETING_FEATURE_20251109.md
DEPLOY_AUTH_FIX_20251110.md
```

### 规则 3：定期清理

**每月任务**：
```bash
# 检查 features/ 中的文档
ls -lt docs/features/

# 移动 3 个月前的文档到 archive/
find docs/features -name "*.md" -mtime +90 -exec mv {} docs/archive/ \;
```

**每季度任务**：
```bash
# 检查 archive/ 中的文档
ls -lt docs/archive/

# 删除 1 年前的文档（可选）
find docs/archive -name "*.md" -mtime +365 -delete
```

---

## 🔗 快速访问

为了保持兼容性，根目录保留了关键文档的软链接：

```
Cshine/
├── README.md -> docs/core/README.md  # 软链接
└── docs/
    └── ...
```

这样：
- ✅ GitHub 仍然能正确显示 README
- ✅ 旧的文档链接仍然有效
- ✅ 项目根目录保持整洁

---

## 📖 文档索引

### 给开发人员

1. **项目说明**：[docs/core/README.md](core/README.md)
2. **版本历史**：[docs/core/CHANGELOG.md](core/CHANGELOG.md)
3. **后端更新协议**：[docs/deployment/BACKEND_UPDATE_PROTOCOL.md](deployment/BACKEND_UPDATE_PROTOCOL.md)

### 给部署人员

1. **完整部署指南**：[docs/deployment/DEPLOYMENT_GUIDE.md](deployment/DEPLOYMENT_GUIDE.md)
2. **更新服务器**：[docs/deployment/UPDATE_SERVER.sh](deployment/UPDATE_SERVER.sh)
3. **登录配置**：[docs/deployment/LOGIN.md](deployment/LOGIN.md)

### 给产品经理

1. **产品需求文档**：[docs/core/PRD-完善版.md](core/PRD-完善版.md)
2. **版本更新记录**：[docs/core/CHANGELOG.md](core/CHANGELOG.md)

---

## 🎯 维护最佳实践

### ✅ DO（推���）

1. **核心文档**：随项目发展持续更新
2. **部署文档**：保持最新，定期 review
3. **功能文档**：完成功能时创建，3 个月后归档
4. **归档文档**：定期清理，释放空间

### ❌ DON'T（避免）

1. ❌ 不要在根目录创建新文档
2. ❌ 不要重复创建相似文档
3. ❌ 不要保留过期的临时文档
4. ❌ 不要删除核心和部署文档

---

## 📊 文档清理检查清单

### 每月检查（第一个周一）

```
[ ] 检查 features/ 中的文档日期
[ ] 移动 3 个月前的文档到 archive/
[ ] 更新 CHANGELOG.md
[ ] 检查 deployment/ 文档是否需要更新
```

### 每季度检查（季度末）

```
[ ] 审查 archive/ 中的文档
[ ] 删除 1 年前的临时文档
[ ] 打包压缩重要历史文档
[ ] 更新本文档索引
```

---

## 🔧 自动化脚本

创建 `docs/cleanup.sh` 辅助清理：

```bash
#!/bin/bash
# 文档清理脚本

echo "📚 开始文档清理..."

# 移动 3 个月前的功能文档到归档
echo "1️⃣ 移动旧功能文档到归档..."
find docs/features -name "*.md" -mtime +90 -exec mv {} docs/archive/ \;

# 统计各目录文档数量
echo ""
echo "📊 文档统计："
echo "核心文档: $(ls docs/core | wc -l)"
echo "部署文档: $(ls docs/deployment | wc -l)"
echo "功能文档: $(ls docs/features | wc -l)"
echo "归档文档: $(ls docs/archive | wc -l)"

echo ""
echo "✅ 清理完成！"
```

---

**文档版本**：v1.0  
**创建日期**：2025-11-09  
**维护团队**：Cshine Dev Team

---

**Let Your Ideas Shine. ✨**

