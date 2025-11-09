# 🚀 Cshine 开发规范

> **必读**：所有开发人员在提交代码前必须遵循的规范  
> 版本：v1.0 | 更新日期：2025-11-09

---

## 📋 目录

- [代码提交规范](#代码提交规范)
- [后端功能更新规范](#后端功能更新规范)
- [文档管理规范](#文档管理规范)
- [分支管理规范](#分支管理规范)

---

## 🔄 代码提交规范

### Commit Message 格式

遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

### Type 类型

| Type | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat: 新增会议纪要功能` |
| `fix` | Bug 修复 | `fix: 修复登录接口认证失败` |
| `docs` | 文档更新 | `docs: 更新部署指南` |
| `style` | 代码格式（不影响功能） | `style: 格式化代码` |
| `refactor` | 代码重构 | `refactor: 重构用户认证模块` |
| `perf` | 性能优化 | `perf: 优化数据库查询` |
| `test` | 测试相关 | `test: 添加单元测试` |
| `chore` | 构建/工具链 | `chore: 更新依赖版本` |

### 示例

```bash
# 好的 commit
feat: 新增会议纪要功能 + 部署文档
fix(auth): 修复 /api/v1/auth/me 接口认证失败问题
docs: 更新后端更新协议和快速上手指南
refactor: 文档结构大重组 - 建立分类管理系统

# 不好的 commit
update
修改了一些东西
fix bug
```

---

## ⚡ 后端功能更新规范 ⭐

> **核心规则**：每次后端功能开发完成，必须提供线上部署方案

### 📝 规则 1：创建部署文档（必须）

每次后端功能更新后，**必须**创建一个部署文档。

#### 步骤

```bash
# 1. 复制模板
cp .github_docs_template.md docs/features/DEPLOY_<功能名>_$(date +%Y%m%d).md

# 2. 填写文档（见模板说明）
# 3. 与代码一起提交
git add docs/features/DEPLOY_*.md
git commit -m "feat: 新功能 + 线上部署方案"
```

#### 文档命名规范

```
docs/features/DEPLOY_<功能名>_<日期>.md

✅ 好的命名：
DEPLOY_MEETING_FEATURE_20251109.md
DEPLOY_AUTH_FIX_20251109.md
DEPLOY_PERFORMANCE_OPTIMIZATION_20251110.md

❌ 不好的命名：
deploy.md
update.md
新功能.md
```

#### 必填内容

- ✅ 更新类型（新功能/Bug修复/性能优化/安全补丁）
- ✅ 是否必须更新（必须🔴/建议🟡/可选🟢）
- ✅ 预计停机时间
- ✅ 涉及的文件变更
- ✅ 数据库变更（如有）
- ✅ 依赖变更（如有）
- ✅ 环境变量变更（如有）
- ✅ 部署步骤（推荐自动脚本）
- ✅ 验证方法
- ✅ 回滚方案

### 📢 规则 2：通知更新（建议）

更新是**建议性而非强制性**的，但需要通知：

```
📢 【后端更新通知】

功能：[功能名称]
类型：[新功能/Bug修复/优化]
紧急度：[必须🔴/建议🟡/可选🟢]
文档：docs/features/DEPLOY_xxx_YYYYMMDD.md

可以在方便的时候更新线上环境 ✨
```

### 🎯 规则 3：更新优先级

| 级别 | 说明 | 更新时间 | 标识 |
|------|------|---------|------|
| **必须** | 安全漏洞、严重Bug、数据丢失 | 立即 | 🔴 |
| **建议** | 新功能、性能优化、用户体验 | 1-3天 | 🟡 |
| **可选** | 代码重构、日志优化、注释 | 下次集中更新 | 🟢 |

### 📚 规则 4：文档生命周期

```
功能开发完成
    ↓
创建 docs/features/DEPLOY_xxx.md
    ↓
与代码一起提交到 git
    ↓
通知需要更新（可选）
    ↓
使用 3 个月
    ↓
自动归档到 docs/archive/
```

### 🔗 完整协议

详见：[后端更新标准协议](../deployment/BACKEND_UPDATE_PROTOCOL.md)

---

## 📚 文档管理规范

### 文档分类

| 分类 | 位置 | 用途 | 何时创建 | 何时删除 |
|------|------|------|---------|---------|
| **核心** | `docs/core/` | README、CHANGELOG、PRD | 项目初期 | 永不删除 |
| **部署** | `docs/deployment/` | 部署指南、配置文档 | 需要时 | 永不删除 |
| **功能** | `docs/features/` | 临时性部署文档 | 功能完成时 | 3个月后归档 |
| **归档** | `docs/archive/` | 过期文档 | 自动归档 | 1年后可删除 |

### 规则 1：新文档放对位置

```bash
# ❌ 错误：不要在根目录创建文档
touch NEW_FEATURE.md

# ✅ 正确：根据类型选择位置
touch docs/features/DEPLOY_NEW_FEATURE_20251109.md  # 功能部署文档
touch docs/deployment/NEW_CONFIG.md                 # 新的配置文档
```

### 规则 2：定期清理

```bash
# 每月第一个周一运行
bash docs/cleanup.sh

# 功能：
# - 移动 3 个月前的功能文档到归档
# - 提示删除 1 年前的归档文档
# - 统计文档数量
```

### 规则 3：使用模板

```bash
# 功能部署文档使用模板
cp .github_docs_template.md docs/features/DEPLOY_xxx.md
```

### 规则 4：文档间引用

```markdown
# ✅ 正确：使用相对路径
详见 [部署指南](../deployment/DEPLOYMENT_GUIDE.md)

# ❌ 错误：使用绝对路径或错误路径
详见 [部署指南](DEPLOYMENT_GUIDE.md)
详见 [部署指南](/docs/deployment/DEPLOYMENT_GUIDE.md)
```

---

## 🌿 分支管理规范

### 分支命名

```
<type>/<description>

示例：
feature/meeting-summary    # 新功能
fix/login-auth            # Bug 修复
refactor/document-system  # 重构
```

### 主分支

- `main` - 生产环境，稳定版本
- `develop` - 开发环境，最新开发版本（可选）

### 开发流程

```bash
# 1. 从 main 创建功能分支
git checkout main
git pull origin main
git checkout -b feature/new-feature

# 2. 开发 + 提交
git add .
git commit -m "feat: 新功能"

# 3. 推送到远程
git push origin feature/new-feature

# 4. 创建 Pull Request
# 5. Code Review
# 6. 合并到 main
```

### 提交前检查清单

```
[ ] 代码已在本地测试通过
[ ] Commit message 符合规范
[ ] 已创建部署文档（如果是后端更新）
[ ] 文档放在正确的位置
[ ] 已更新 CHANGELOG.md
[ ] 没有遗留 console.log / debugger
[ ] 没有提交敏感信息（密钥、密码）
```

---

## 📋 提交代码 Checklist

### 每次提交前必查

```
[ ] ✅ 代码功能完整且测试通过
[ ] ✅ Commit message 符合规范
[ ] ✅ 后端更新已创建部署文档（docs/features/）
[ ] ✅ 部署文档已填写完整
[ ] ✅ 文档间的引用路径正确
[ ] ✅ 更新了 CHANGELOG.md
[ ] ✅ 没有敏感信息（.env、密钥等）
[ ] ✅ 没有调试代码（console.log、debugger）
[ ] ✅ 代码格式化完成
```

### 后端功能更新额外检查

```
[ ] ✅ 部署文档位置正确（docs/features/DEPLOY_*.md）
[ ] ✅ 部署文档命名规范（DEPLOY_功能名_YYYYMMDD.md）
[ ] ✅ 标注了更新优先级（必须🔴/建议🟡/可选🟢）
[ ] ✅ 说明了数据库变更（如有）
[ ] ✅ 说明了依赖变更（如有）
[ ] ✅ 说明了环境变量变更（如有）
[ ] ✅ 提供了部署步骤
[ ] ✅ 提供了验证方法
[ ] ✅ 提供了回滚方案
```

---

## 🎯 快速参考

### 开发新功能的完整流程

```bash
# 1. 创建分支
git checkout -b feature/new-feature

# 2. 开发代码
# ...

# 3. 测试通过后，创建部署文档
cp .github_docs_template.md docs/features/DEPLOY_NEW_FEATURE_$(date +%Y%m%d).md

# 4. 填写部署文档
# 编辑 docs/features/DEPLOY_NEW_FEATURE_YYYYMMDD.md

# 5. 更新 CHANGELOG
# 编辑 docs/core/CHANGELOG.md

# 6. 提交代码
git add .
git commit -m "feat: 新功能 + 线上部署方案

- 实现了 xxx 功能
- 新增了 xxx 接口
- 更新了 xxx 文档

部署文档：docs/features/DEPLOY_NEW_FEATURE_YYYYMMDD.md
更新优先级：建议🟡"

# 7. 推送
git push origin feature/new-feature

# 8. 通知（可选）
# 在团队群发送更新通知
```

---

## 📖 相关文档

- [后端更新标准协议](../deployment/BACKEND_UPDATE_PROTOCOL.md) - 完整的更新协议
- [后端更新快速上手](../deployment/BACKEND_UPDATE_QUICKSTART.md) - 快速上手指南
- [文档结构说明](../README.md) - 文档分类和管理规范
- [部署文档模板](../../.github_docs_template.md) - 标准模板

---

## ❓ 常见问题

### Q1: 每次提交都要创建部署文档吗？

**A**: 只有**后端功能更新**时需要。前端样式调整、文档更新等不需要。

**需要创建部署文档**：
- ✅ 新增后端 API
- ✅ 修改数据库结构
- ✅ 修复后端 Bug
- ✅ 性能优化（涉及后端）

**不需要创建部署文档**：
- ❌ 前端页面调整
- ❌ 样式优化
- ❌ 文档更新
- ❌ 注释补充

---

### Q2: 部署文档放在哪里？

**A**: 放在 `docs/features/` 目录，3 个月后会自动归档。

```bash
# 正确位置
docs/features/DEPLOY_MEETING_20251109.md

# 错误位置
DEPLOY_MEETING.md  # 不要放根目录
docs/DEPLOY_MEETING.md  # 不要直接放 docs/
```

---

### Q3: 更新是强制的吗？

**A**: 不是。更新是**建议性**的，部署人员根据优先级决定何时更新：

- 🔴 必须：安全漏洞 → 立即更新
- 🟡 建议：新功能 → 1-3天内
- 🟢 可选：代码重构 → 下次集中更新

---

### Q4: 忘记创建部署文档怎么办？

**A**: 立即补充：

```bash
# 1. 创建部署文档
cp .github_docs_template.md docs/features/DEPLOY_FIX_$(date +%Y%m%d).md

# 2. 填写内容

# 3. 单独提交
git add docs/features/
git commit -m "docs: 补充部署文档"
git push
```

---

## 🎓 最佳实践

1. ✅ **养成习惯**：功能完成 → 创建部署文档 → 一起提交
2. ✅ **使用模板**：复制 `.github_docs_template.md`，填写完整
3. ✅ **清晰命名**：`DEPLOY_功能名_日期.md`
4. ✅ **标注优先级**：让部署人员知道重要程度
5. ✅ **提供回滚**：出问题能快速恢复
6. ✅ **定期清理**：每月运行 `docs/cleanup.sh`

---

## 🔄 规范更新

本规范会根据项目发展持续更新，请定期查看。

**当前版本**: v1.0  
**更新日期**: 2025-11-09  
**维护团队**: Cshine Dev Team

---

## 💡 记住这些关键点

1. **后端功能更新 = 必须创建部署文档**
2. **部署文档放在 `docs/features/`**
3. **使用模板 `.github_docs_template.md`**
4. **标注优先级：必须🔴/建议🟡/可选🟢**
5. **更新是建议性的，非强制性**
6. **每月运行 `docs/cleanup.sh` 清理**

---

**Let Your Ideas Shine. ✨**

