# 会议纪要功能更新说明

## 更新时间：2025-11-07

## 🎯 核心改进

### 1. **完整实现说话人分离功能**

根据阿里云通义听悟官方文档，正确实现了说话人分离（Speaker Diarization）功能。

#### 修改的文件：

**`backend/app/services/tingwu_service.py`**
- ✅ 添加 `enable_speaker_diarization` 参数
- ✅ 添加 `speaker_count` 参数（0=不定人数，2=2人）
- ✅ 正确配置 `Transcription.DiarizationEnabled`
- ✅ 正确配置 `Transcription.Diarization.SpeakerCount`
- ✅ 完整实现智能摘要、会议助手、章节划分等功能
- ✅ 解析并保存段落信息（包含 SpeakerId）

**`backend/app/services/meeting_processor.py`**
- ✅ 开启说话人分离：`enable_speaker_diarization=True`
- ✅ 自动识别人数：`speaker_count=0`
- ✅ 从段落信息中提取会议要点（包含发言人）
- ✅ 优先使用通义听悟的行动项识别结果
- ✅ 添加兜底方案确保稳定性

**`backend/app/services/ai_processor.py`**
- ✅ 明确关闭说话人分离（闪记不需要）

### 2. **功能对比**

| 功能 | 闪记 | 会议纪要 |
|------|------|----------|
| 语音转写 | ✅ | ✅ |
| 智能摘要 | ✅ | ✅ |
| 关键词提取 | ✅ | ✅ |
| **发言总结** | ❌ | ✅ **新增** |
| **思维导图** | ❌ | ✅ **新增** |
| **说话人分离** | ❌ | ✅ **新增** |
| **章节划分** | ❌ | ✅ **新增** |
| **行动项识别** | ❌ | ✅ **新增** |

### 3. **多维度智能摘要**

通义听悟现在支持 **5种摘要类型**：

#### 3.1 段落摘要（Paragraph）
- 整体会议的概括性摘要
- 用于快速了解会议整体内容

#### 3.2 发言总结（Conversational）✨ 新增
- 按发言人汇总主要观点
- 示例格式：
```
发言人1：
- 提出了产品功能优化建议
- 强调用户体验的重要性

发言人2：
- 同意优化方案
- 建议增加A/B测试
```

#### 3.3 思维导图（MindMap）✨ 新增
- 以结构化方式展示会议主题
- 适合梳理会议逻辑关系
- 示例格式：
```
会议主题
├── 产品功能讨论
│   ├── 现有问题分析
│   └── 优化方案设计
├── 技术实现方案
│   ├── 前端改造
│   └── 后端接口
└── 项目排期
    ├── 里程碑1
    └── 里程碑2
```

#### 3.4 问答总结（QuestionsAnswering）
- 提炼会议中的问题和答案
- 适合决策会议和技术讨论

### 4. **章节划分效果**

开启章节划分后，通义听悟会自动识别会议议题：

```json
{
  "AutoChapters": [
    {
      "StartTime": 0,
      "EndTime": 180000,
      "Title": "开场介绍",
      "Summary": "会议开场，介绍参会人员和会议议程"
    },
    {
      "StartTime": 180000,
      "EndTime": 600000,
      "Title": "产品功能讨论",
      "Summary": "讨论新功能的设计方案和技术实现"
    },
    {
      "StartTime": 600000,
      "EndTime": 900000,
      "Title": "排期安排",
      "Summary": "确定各项任务的负责人和交付时间"
    }
  ]
}
```

### 5. **说话人分离效果**

开启说话人分离后，返回的数据结构：

```json
{
  "Transcription": {
    "Paragraphs": [
      {
        "ParagraphId": "xxx",
        "SpeakerId": "1",  // 发言人ID
        "Words": [
          {
            "Text": "您好，",
            "Start": 4970,
            "End": 5560
          }
        ]
      },
      {
        "ParagraphId": "yyy",
        "SpeakerId": "2",  // 另一个发言人
        "Words": [...]
      }
    ]
  }
}
```

### 6. **会议要点提取策略**

**三层提取策略**（按优先级）：

1. **策略1：章节模式**（推荐）
   - 如果有章节信息，按章节组织要点
   - 每个章节作为一个大要点
   - 包含：章节标题、时间戳、章节摘要

2. **策略2：段落模式**
   - 如果没有章节但有说话人分离
   - 按发言人段落组织要点
   - 包含：发言人、时间戳、发言内容

3. **策略3：兜底模式**
   - 从摘要或转写文本中提取
   - 确保即使AI功能失败也有基本要点

### 7. **会议要点展示**

现在会议要点会包含：
- ✅ **时间戳**：精确到秒
- ✅ **发言人**：自动识别（发言人1、发言人2...）
- ✅ **主题**：从发言内容提取
- ✅ **内容**：完整发言文本

**章节模式示例**：
```json
{
  "timestamp": "00:03:00",
  "speaker": "多人",
  "topic": "产品功能讨论",
  "content": "讨论新功能的设计方案和技术实现，确定了使用通义听悟API..."
}
```

**段落模式示例**：
```json
{
  "timestamp": "00:05:23",
  "speaker": "发言人1",
  "topic": "关于产品功能的讨论",
  "content": "我认为我们应该优先开发会议纪要功能..."
}
```

### 8. **行动项识别**

优先使用通义听悟的智能识别结果，如果没有则使用关键词规则识别。

示例：
```json
{
  "content": "完成产品原型设计",
  "assignee": "待分配",
  "deadline": null,
  "priority": "medium",
  "status": "pending"
}
```

## 🔧 技术细节

### 通义听悟 API 参数配置

```python
# 会议纪要（完整功能）
task_result = tingwu_service.create_task(
    file_url=audio_url,
    source_language="cn",
    enable_summarization=True,                                      # 智能摘要
    summarization_types=['Paragraph', 'Conversational', 'MindMap'], # 摘要类型 ⭐
    enable_chapters=True,                                          # 章节划分 ⭐
    enable_meeting_assistance=True,                                # 会议助手（行动项）⭐
    enable_speaker_diarization=True,                               # 说话人分离 ⭐
    speaker_count=0                                                # 自动识别人数 ⭐
)

# 闪记
task_result = tingwu_service.create_task(
    file_url=audio_url,
    source_language="cn",
    enable_summarization=True,
    enable_chapters=False,
    enable_meeting_assistance=True,
    enable_speaker_diarization=False    # 不需要说话人分离
)
```

## 📝 使用建议

1. **上传会议音频时**：
   - 确保音频清晰
   - 多人对话效果更好
   - 建议音频时长：3-60分钟

2. **说话人数量**：
   - 设为 0：自动识别（推荐）
   - 设为 2：强制识别为2人
   - 更多人数：通义听悟会自动处理

3. **处理时间**：
   - 短音频（<5分钟）：约30秒-2分钟
   - 中等音频（5-30分钟）：约2-10分钟
   - 长音频（30-60分钟）：约10-30分钟

## 🎉 预期效果

现在会议纪要功能应该能够：
1. ✅ 正确上传音频到 OSS
2. ✅ 提交通义听悟任务（完整的会议功能）
3. ✅ 自动划分会议章节（识别不同议题）
4. ✅ 自动识别不同发言人
5. ✅ 生成 **5种智能摘要**：
   - 段落摘要（整体概括）
   - 发言总结（按人汇总）✨
   - 思维导图（结构化展示）✨
   - 问答总结（Q&A 提炼）
6. ✅ 提取会议要点（按章节或发言人组织）
7. ✅ 智能识别行动项
8. ✅ 完整的会议转写文本

## 📚 参考文档

- [通义听悟 - 语音转写](https://help.aliyun.com/zh/tingwu/voice-transcription)
- [通义听悟 - API 文档](https://help.aliyun.com/zh/tingwu/)

## 🐛 如果还有问题

请查看：
1. **后端日志**：`backend/logs/cshine.log`
2. **控制台输出**：查看详细的错误堆栈
3. **排查指南**：`backend/TROUBLESHOOTING.md`

关键日志信息：
```
✅ "已开启说话人分离: speaker_count=0"
✅ "已开启智能摘要: Paragraph, Conversational, MindMap"
✅ "已开启会议助手"
✅ "已开启章节划分"
✅ "转写文本提取成功，长度: xxx, 段落数: xxx"
✅ "已获取发言总结"
✅ "已获取思维导图"
✅ "摘要解析完成，类型数: 3"
✅ "使用章节信息提取要点: X个章节"（如果有章节）
✅ "从xx个段落中提取了xx个要点"（如果没有章节）
```

## 🔄 数据库迁移

由于添加了新字段，需要运行数据库迁移：

```bash
cd backend
python migrations/add_meeting_summary_types.py
```

迁移会添加以下字段到 `meetings` 表：
- `conversational_summary` TEXT - 发言总结
- `mind_map` TEXT - 思维导图

