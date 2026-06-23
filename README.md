# MiMo ASR 语音转文字

使用小米 MiMo-V2.5-ASR 模型将音频转换为文字。

## 🎯 核心用法

### 1. 获取 API 凭证

访问 [MiMo Token Plan](https://token-plan-cn.xiaomimimo.com)，获取：
- **API Key**：格式 `tp-xxxx...xxxx`
- **Base URL**：`https://token-plan-cn.xiaomimimo.com/v1`

### 2. 调用 API 转换音频

```python
import requests
import base64

# 读取音频文件并转为 Base64
with open("audio.mp3", "rb") as f:
    audio_base64 = base64.b64encode(f.read()).decode("utf-8")

# 调用 MiMo ASR API
response = requests.post(
    "https://token-plan-cn.xiaomimimo.com/v1/chat/completions",
    headers={
        "Content-Type": "application/json",
        "Authorization": "Bearer tp-your-api-key"
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

# 获取转写结果
text = response.json()["choices"][0]["message"]["content"]
print(text)
```

### 3. 关键参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `model` | 模型名称 | `mimo-v2.5-asr` |
| `input_audio.data` | Base64 音频 | `data:audio/mpeg;base64,{base64}` |
| `asr_options.language` | 语种 | `zh` / `en` / `auto` |

### 4. 大小限制与分割

**限制**：Base64 后不超过 10MB

**超过时分割**：
```python
import subprocess

# 分割成 5 分钟片段
subprocess.run([
    "ffmpeg", "-i", "large_audio.mp3",
    "-ss", "0", "-t", "300",
    "-c", "copy", "chunk_001.mp3"
])
```

逐片段调用 API，最后拼接结果。

---

## 📦 封装工具

为了方便使用，提供了命令行工具：

```bash
# 安装
git clone https://github.com/dengzixiang520/mimo-asr-skill.git
cd mimo-asr-skill
pip install requests

# 设置 API Key
export MIMO_API_KEY="tp-your-api-key"

# 使用
python transcribe.py audio.mp3
python transcribe.py ./audio_folder/
```

工具自动处理：
- ✅ 文件大小检测
- ✅ 大文件自动分割
- ✅ 逐片段转写
- ✅ 结果拼接保存

---

## 🔧 完整 API 参考

### 请求格式

```
POST https://token-plan-cn.xiaomimimo.com/v1/chat/completions
Authorization: Bearer {API_KEY}
Content-Type: application/json
```

### 请求体

```json
{
    "model": "mimo-v2.5-asr",
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "input_audio",
                    "input_audio": {
                        "data": "data:audio/mpeg;base64,{BASE64_AUDIO}"
                    }
                }
            ]
        }
    ],
    "asr_options": {
        "language": "zh"
    }
}
```

### 响应格式

```json
{
    "choices": [
        {
            "message": {
                "content": "转写的文字内容..."
            }
        }
    ]
}
```

### 音频格式

| 格式 | MIME 类型 |
|------|-----------|
| MP3 | `audio/mpeg` |
| WAV | `audio/wav` |

### 语种选项

| 值 | 说明 |
|----|------|
| `zh` | 中文（及方言：粤语、吴语、闽南语、四川话等） |
| `en` | 英文 |
| `auto` | 自动检测 |

---

## ⚠️ 注意事项

1. **云端服务**：音频会上传到小米服务器，敏感音频慎用
2. **必须联网**：需要稳定的网络连接
3. **Token Plan 专属**：必须使用 `https://token-plan-cn.xiaomimimo.com/v1`
4. **计费**：按 Token 计费，非高峰期（00:00-08:00）0.8x 系数

---

## 📋 完整示例

### 示例 1：转写单个文件

```python
import requests
import base64

API_KEY = "tp-your-api-key"
BASE_URL = "https://token-plan-cn.xiaomimimo.com/v1"

def transcribe(audio_file, language="zh"):
    with open(audio_file, "rb") as f:
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
            "asr_options": {"language": language}
        }
    )
    
    return response.json()["choices"][0]["message"]["content"]

# 使用
text = transcribe("interview.mp3")
print(text)
```

### 示例 2：转写大文件（自动分割）

```python
import os
import subprocess
import shutil

def transcribe_large(audio_file, language="zh", chunk_duration=300):
    # 获取时长
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", audio_file],
        capture_output=True, text=True
    )
    duration = float(result.stdout.strip())
    
    # 分割并转写
    full_text = []
    start = 0
    index = 0
    
    while start < duration:
        # 分割
        chunk_file = f"chunk_{index:03d}.mp3"
        subprocess.run([
            "ffmpeg", "-i", audio_file, "-ss", str(start),
            "-t", str(chunk_duration), "-c", "copy", chunk_file,
            "-y", "-loglevel", "error"
        ])
        
        # 转写
        text = transcribe(chunk_file, language)
        full_text.append(text)
        
        # 清理
        os.remove(chunk_file)
        
        start += chunk_duration
        index += 1
    
    return "\n\n".join(full_text)

# 使用
text = transcribe_large("long_lecture.mp3")
with open("output.txt", "w", encoding="utf-8") as f:
    f.write(text)
```

### 示例 3：批量转写

```python
import glob

def batch_transcribe(directory, language="zh"):
    results = {}
    
    for audio_file in glob.glob(f"{directory}/*.mp3"):
        print(f"处理: {audio_file}")
        text = transcribe(audio_file, language)
        results[audio_file] = text
        
        # 保存
        output_file = audio_file.replace(".mp3", ".txt")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(text)
    
    return results

# 使用
batch_transcribe("./recordings/")
```

---

## 🔗 相关链接

- [MiMo 官方文档](https://mimo.mi.com/docs/zh-CN/quick-start/usage-guide/audio/Speech-Recognition)
- [MiMo Token Plan](https://token-plan-cn.xiaomimimo.com)
- [ffmpeg 下载](https://www.gyan.dev/ffmpeg/builds/)

## 📄 许可证

MIT License
