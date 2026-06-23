---
name: transcribe
description: 使用 MiMo ASR 将音频文件转为文字（云端 AI 模型）
user_invocable: true
---

# MiMo ASR 语音转文字

将音频文件（MP3/WAV）转换为文字，使用**小米云端 AI 模型 MiMo-V2.5-ASR**进行识别。

## ⚠️ 重要说明

### 云端模型
- 本工具使用的是**小米云端 AI 服务**，不是本地模型
- 音频数据会上传到小米服务器进行处理
- 需要联网使用
- 需要 MiMo API Key（Token Plan）

### 大文件处理
- 单次请求 Base64 大小上限：**10MB**
- 超过限制的文件会**自动分割**成 5 分钟片段
- 分割使用 ffmpeg，需要提前安装
- 处理完成后临时文件自动清理

## 使用方式

```
/transcribe [文件或目录路径]
```

## 执行步骤

1. **检查环境**
   - 确认 Python 已安装
   - 确认 ffmpeg 已安装（用于分割大文件）
   - 确认 requests 库已安装

2. **获取配置**
   - 从环境变量 `MIMO_API_KEY` 获取 API Key
   - 如果未设置，提示用户输入
   - Base URL 默认使用 `https://token-plan-cn.xiaomimimo.com/v1`

3. **扫描文件**
   - 如果指定路径是目录，扫描所有 `.mp3` 和 `.wav` 文件
   - 如果指定路径是文件，直接处理该文件

4. **处理音频**
   - 检查文件大小
   - 如果文件 Base64 后超过 8MB，使用 ffmpeg 分割成 5 分钟片段
   - 逐片段调用 MiMo ASR API（云端模型）

5. **保存结果**
   - 将转写结果保存为同名 `.txt` 文件
   - 输出转写完成信息

## API 调用格式

```python
POST https://token-plan-cn.xiaomimimo.com/v1/chat/completions
Authorization: Bearer {API_KEY}
Content-Type: application/json

{
    "model": "mimo-v2.5-asr",  # 云端模型
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "input_audio",
                    "input_audio": {
                        "data": "data:audio/mpeg;base64,{BASE64_AUDIO}"  # 音频数据上传到云端
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

## 注意事项

- **云端服务**：音频会上传到小米服务器，敏感音频请谨慎使用
- **需要联网**：必须保持网络连接
- **Token Plan**：必须使用专属 Base URL：`https://token-plan-cn.xiaomimimo.com/v1`
- **大小限制**：单次请求 Base64 大小上限 10MB
- **自动分割**：大文件会自动分割处理，无需手动操作
- **语种设置**：建议明确指定语种（`zh`/`en`）以提高准确率

## 错误处理

- 401 错误：检查 API Key 和 Base URL
- 400 错误（超过大小限制）：自动分割文件
- 网络错误：自动重试 3 次

## 计费说明

- 按 Token 计费
- Token Plan 用户有专属额度
- 非高峰期（00:00-08:00）消耗系数 0.8x
