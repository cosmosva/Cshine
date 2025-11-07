# 部署新功能指南

## 🚀 快速开始

### 1. 运行数据库迁移

```bash
cd backend
python migrations/add_meeting_summary_types.py
```

**输出示例：**
```
开始数据库迁移...
添加 conversational_summary 字段...
添加 mind_map 字段...
✅ 数据库迁移完成！
   - 新增字段: conversational_summary (发言总结)
   - 新增字段: mind_map (思维导图)
```

### 2. 重启后端服务

```bash
cd backend
# 如果使用 venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate     # Windows

# 重启服务
python main.py
```

### 3. 验证功能

上传一个会议音频，检查日志输出：

```
✅ "已开启智能摘要: Paragraph, Conversational, MindMap"
✅ "已获取发言总结"
✅ "已获取思维导图"
✅ "摘要解析完成，类型数: 3"
```

## 📋 新增功能清单

### ✨ 发言总结（Conversational Summary）
- **作用**：按发言人汇总主要观点
- **数据库字段**：`conversational_summary`
- **API响应**：`MeetingResponse.conversational_summary`

### ✨ 思维导图（MindMap）
- **作用**：以结构化方式展示会议主题
- **数据库字段**：`mind_map`
- **API响应**：`MeetingResponse.mind_map`

## 📊 完整的摘要类型

现在会议纪要支持 **5种摘要**：

| 类型 | 英文名称 | 用途 | 存储字段 |
|------|---------|------|---------|
| 段落摘要 | Paragraph | 整体概括 | `summary` |
| 发言总结 | Conversational | 按人汇总 | `conversational_summary` ✨ |
| 思维导图 | MindMap | 结构化展示 | `mind_map` ✨ |
| 问答总结 | QuestionsAnswering | Q&A 提炼 | （暂时不存储）|
| 章节摘要 | - | 章节级摘要 | 包含在 `key_points` 中 |

## 🔧 技术实现

### 代码变更文件

1. **`backend/app/models.py`**
   - 添加 `conversational_summary` 字段
   - 添加 `mind_map` 字段

2. **`backend/app/schemas.py`**
   - `MeetingResponse` 添加新字段
   - `from_orm` 方法更新

3. **`backend/app/services/tingwu_service.py`**
   - 添加 `summarization_types` 参数
   - 支持多种摘要类型配置
   - 解析逻辑更新（区分不同摘要类型）

4. **`backend/app/services/meeting_processor.py`**
   - 保存新的摘要字段到数据库

5. **`backend/migrations/add_meeting_summary_types.py`**
   - 新增迁移脚本

## 🧪 测试建议

### 测试场景1：短会议（5-15分钟）
- 2-3人对话
- 预期：发言总结清晰区分发言人

### 测试场景2：长会议（30-60分钟）
- 多人、多议题
- 预期：思维导图展示清晰的主题结构

### 测试场景3：技术讨论会议
- 包含问题和解答
- 预期：问答总结提炼关键Q&A

## 📝 注意事项

1. **数据库迁移**：必须先运行迁移再使用新功能
2. **向后兼容**：旧数据的新字段为 `NULL`，不影响现有功能
3. **API响应**：前端需要更新以展示新字段
4. **日志检查**：确认通义听悟返回了新的摘要类型

## 🐛 常见问题

### Q: 迁移失败怎么办？
A: 检查数据库文件权限，确保 `cshine.db` 可写

### Q: 某些会议没有发言总结？
A: 可能是会议时长太短或音频质量不佳，通义听悟会选择性返回

### Q: 思维导图格式是什么？
A: 纯文本格式，使用缩进和符号表示层级关系

## 📚 相关文档

- [功能更新说明](./MEETING_FEATURE_UPDATE.md)
- [通义听悟文档](https://help.aliyun.com/zh/tingwu/)
- [项目 README](../README.md)

