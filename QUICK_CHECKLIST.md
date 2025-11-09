# ⚡ 提交代码前必读

> 快速检查清单 - 打印出来贴在显示器旁边！

---

## 🔴 后端功能更新必做

```
[ ] 创建部署文档
    cp .github_docs_template.md docs/features/DEPLOY_xxx_$(date +%Y%m%d).md

[ ] 填写完整信息
    - 更新类型
    - 是否必须（必须🔴/建议🟡/可选🟢）
    - 数据库变更
    - 依赖变更
    - 环境变量变更
    - 部署步骤
    - 验证方法
    - 回滚方案

[ ] 与代码一起提交
    git add docs/features/DEPLOY_*.md
```

---

## ✅ 所有提交都要做

```
[ ] 代码测试通过
[ ] Commit message 规范
    格式：feat/fix/docs/refactor: 说明
[ ] 更新 CHANGELOG.md
[ ] 没有敏感信息（密钥、.env）
[ ] 没有调试代码（console.log）
```

---

## 📂 文档位置规则

```
功能部署文档 → docs/features/DEPLOY_*.md
部署配置文档 → docs/deployment/*.md
核心文档     → docs/core/*.md
过期文档     → docs/archive/*.md (自动归档)
```

---

## 🎯 更新优先级

```
🔴 必须：安全漏洞、严重Bug → 立即更新
🟡 建议：新功能、性能优化 → 1-3天内
🟢 可选：代码重构、注释   → 下次集中更新
```

---

## 📋 完整规范

详见：[docs/core/DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md)

---

**记住**：后端功能更新 = 必须创建部署文档！

