---
name: transcribe
description: 使用 MiMo ASR 云端模型将音频文件转为文字
user_invocable: true
---

# 语音转文字

当用户调用 `/transcribe` 时，使用小米 MiMo-V2.5-ASR 云端模型将音频转换为文字。

## 前置条件

检查以下环境：
1. Python 是否可用：`python --version`
2. ffmpeg 是否可用：`ffmpeg -version`
3. requests 库是否安装：`pip show requests`

如果缺少依赖，提示用户安装。

## 获取 API Key

询问用户获取 API Key，或检查环境变量：
- 环境变量：`MIMO_API_KEY`
- Token Plan 专属 Base URL：`https://token-plan-cn.xiaomimimo.com/v1`

## 执行转写

根据用户提供的文件路径，执行以下操作：

### 单个文件（< 8MB）

```python
import requests
import base64

API_KEY = "{用户提供的 API Key}"
BASE_URL = "https://token-plan-cn.xiaomimimo.com/v1"

with open("{文件路径}", "rb") as f:
    audio_base64 = base64.b64encode(f.read()).decode("utf-8")

response = requests.post(
    f"{BASE_URL}/chat/completions",
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    },
    json={
        "model": "mimo-v2.5-asr",
        "messages": [{
            "role": "user",
            "content": [{
                "type": "input_audio",
                "input_audio": {
                    "data": f"data:audio/mpeg;base64,{audio_base64}"
                }
            }]
        }],
        "asr_options": {"language": "zh"}
    }
)

result = response.json()["choices"][0]["message"]["content"]
print(result)
```

### 大文件（>= 8MB）

需要先用 ffmpeg 分割：
```bash
ffmpeg -i input.mp3 -ss 0 -t 300 -c copy chunk_001.mp3
ffmpeg -i input.mp3 -ss 300 -t 300 -c copy chunk_002.mp3
# 依此类推
```

逐片段调用 API，最后拼接结果。

### 批量处理（目录）

扫描目录下所有 `.mp3` 和 `.wav` 文件，逐个处理。

## 输出结果

1. 在终端显示转写文字
2. 保存为同名 `.txt` 文件
3. 告知用户文件位置

## 注意事项

- 这是**云端服务**，音频会上传到小米服务器
- 单次请求 Base64 大小上限 10MB
- 建议指定语种：`zh`（中文）、`en`（英文）、`auto`（自动）
- Token Plan 用户必须使用专属 Base URL
