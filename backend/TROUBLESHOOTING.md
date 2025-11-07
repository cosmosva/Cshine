# 会议纪要功能故障排查指南

## 问题：会议纪要显示"处理失败"

### 排查步骤

#### 1. 查看后端日志

会议处理失败时，后端会记录详细的错误信息。

**查看日志：**
```bash
cd backend

# 查看最新日志
tail -f logs/cshine.log

# 或者查看控制台输出
# 如果你是用 python main.py 启动的，错误会直接显示在控制台
```

**关键日志信息：**
- `提交会议转写任务` - 任务是否成功提交
- `会议转写任务已提交` - 获得了 task_id
- `任务处理中...` - 轮询状态
- `会议 AI 处理失败` - 失败原因和堆栈信息

---

#### 2. 验证音频上传是否成功

**检查点：**
1. 音频是否成功上传到 OSS？
2. OSS URL 是否可以公网访问？

**测试方法：**
```bash
# 在后端日志中找到上传的 OSS URL，类似：
# 用户 xxx 上传音频到 OSS: https://xxx.oss-cn-xxx.aliyuncs.com/xxx.mp3

# 用浏览器或 curl 访问该 URL
curl -I "你的OSS_URL"

# 应该返回 200 OK
```

**常见问题：**
- OSS Bucket 权限设置不正确（需要公共读权限）
- 音频文件格式不支持
- 文件上传失败但前端没有捕获错误

---

#### 3. 测试闪记功能

闪记和会议纪要使用相同的通义听悟 API，如果闪记能正常工作，说明 API 配置是正确的。

**测试步骤：**
1. 在小程序首页长按录音按钮
2. 说一段话（5-10秒）
3. 松开按钮
4. 观察是否能成功转写

**如果闪记失败：**
说明通义听悟 API 配置有问题，检查：
```bash
# backend/config.py
ALIBABA_CLOUD_ACCESS_KEY_ID = "你的AccessKeyId"
ALIBABA_CLOUD_ACCESS_KEY_SECRET = "你的AccessKeySecret"
TINGWU_APP_KEY = "你的通义听悟AppKey"
```

---

#### 4. 检查数据库状态

查看会议记录的实际状态：

```bash
cd backend

# 进入 Python shell
python

# 执行以下代码
from app.database import SessionLocal
from app.models import Meeting

db = SessionLocal()
meetings = db.query(Meeting).order_by(Meeting.created_at.desc()).limit(5).all()

for m in meetings:
    print(f"ID: {m.id}")
    print(f"标题: {m.title}")
    print(f"状态: {m.status}")
    print(f"音频URL: {m.audio_url}")
    print(f"转写文本长度: {len(m.transcript) if m.transcript else 0}")
    print("-" * 50)

db.close()
```

---

#### 5. 手动测试通义听悟 API

创建测试脚本验证 API 是否正常：

```python
# test_tingwu.py
from app.services.tingwu_service import tingwu_service

# 使用一个已知的公开可访问的音频URL测试
# 注意：这个URL需要是你OSS上的一个有效音频文件
test_url = "https://你的OSS地址/test.mp3"

try:
    # 创建任务
    result = tingwu_service.create_task(
        file_url=test_url,
        source_language="cn",
        enable_summarization=True,
        enable_chapters=False,
        enable_meeting_assistance=True
    )
    
    print("✅ 任务创建成功:")
    print(f"Task ID: {result['task_id']}")
    print(f"Status: {result['status']}")
    
    # 等待完成
    print("\n等待处理完成...")
    final_result = tingwu_service.wait_for_completion(
        task_id=result['task_id'],
        max_wait_seconds=600,
        poll_interval=5
    )
    
    print("\n✅ 处理完成:")
    parsed = final_result.get('result', {})
    print(f"转写文本长度: {len(parsed.get('transcription', ''))}")
    print(f"摘要: {parsed.get('summary', '无')[:100]}")
    
except Exception as e:
    print(f"❌ 测试失败: {e}")
```

运行测试：
```bash
cd backend
source venv/bin/activate
python test_tingwu.py
```

---

## 常见错误及解决方案

### 错误 1: "OSS 上传失败"
**原因：** OSS 配置不正确
**解决：**
```python
# 检查 backend/config.py
OSS_ACCESS_KEY_ID = "你的AccessKeyId"
OSS_ACCESS_KEY_SECRET = "你的AccessKeySecret"
OSS_BUCKET_NAME = "你的Bucket名称"
OSS_ENDPOINT = "oss-cn-beijing.aliyuncs.com"  # 确认区域正确
```

### 错误 2: "任务失败: 无法访问音频文件"
**原因：** 音频 URL 不是公网可访问
**解决：** 
1. 登录阿里云 OSS 控制台
2. 找到你的 Bucket
3. 权限管理 → 读写权限 → 设置为"公共读"

### 错误 3: "create_task() got an unexpected keyword argument 'enable_speaker_diarization'"
**原因：** 这个参数不存在
**解决：** 已在代码中修复，不再使用该参数

### 错误 4: 处理时间过长
**原因：** 会议音频可能很长
**解决：** 
- 等待更长时间（最长60分钟）
- 或先用较短的音频测试（1-2分钟）

---

## 快速验证步骤

1. **确认后端运行正常：**
   ```bash
   curl http://localhost:8000/health
   # 应返回: {"status":"healthy"}
   ```

2. **确认能登录：**
   小程序能否正常打开首页

3. **确认能上传文件：**
   后端日志中能看到 "OSS 上传成功" 的日志

4. **确认能创建会议记录：**
   后端日志中能看到 "Meeting created" 的日志

5. **确认 AI 处理启动：**
   后端日志中能看到 "会议 AI 处理已启动" 的日志

6. **查看处理进度：**
   后端日志中能看到 "任务处理中..." 的日志

---

## 获取帮助

如果以上步骤都无法解决问题，请提供：

1. **后端日志**（最近50行）
   ```bash
   tail -n 50 backend/logs/cshine.log
   ```

2. **会议记录信息**
   - 会议 ID
   - 音频 URL
   - 数据库状态

3. **测试音频信息**
   - 音频格式（mp3/m4a/wav）
   - 音频时长
   - 文件大小

4. **错误截图**
   - 小程序错误提示
   - 后端控制台错误信息

