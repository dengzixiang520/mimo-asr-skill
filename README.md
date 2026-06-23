# MiMo ASR Skill

Claude Code Skill：使用小米 MiMo-V2.5-ASR 云端模型将音频转为文字。

## 什么是 Skill？

Skill 是 Claude Code 的扩展能力，通过 `/技能名` 调用。本项目提供 `/transcribe` 技能，让 Claude 帮你完成音频转文字。

## 安装 Skill

### 方法 1：克隆到全局 Skills 目录

```bash
# 克隆仓库
git clone https://github.com/dengzixiang520/mimo-asr-skill.git

# 复制 skill 到 Claude Code 配置目录
# Windows
xcopy /E /I mimo-asr-skill\.claude\skills %USERPROFILE%\.claude\skills\mimo-asr

# macOS/Linux
cp -r mimo-asr-skill/.claude/skills ~/.claude/skills/mimo-asr
```

### 方法 2：克隆到项目目录

```bash
cd your-project
git clone https://github.com/dengzixiang520/mimo-asr-skill.git temp
mkdir -p .claude/skills
cp -r temp/.claude/skills/* .claude/skills/
rm -rf temp
```

## 使用方式

在 Claude Code 中输入：

```
/transcribe audio.mp3
/transcribe ./recordings/
/transcribe C:\Users\x\Desktop\interview.mp3
```

Claude 会自动：
1. 检查环境依赖
2. 获取 API Key（或询问你）
3. 调用 MiMo ASR API
4. 保存转写结果

## API 说明

本 Skill 使用小米 MiMo-V2.5-ASR 模型，核心 API 调用：

```python
POST https://token-plan-cn.xiaomimimo.com/v1/chat/completions
Authorization: Bearer {API_KEY}

{
    "model": "mimo-v2.5-asr",
    "messages": [{
        "role": "user",
        "content": [{
            "type": "input_audio",
            "input_audio": {
                "data": "data:audio/mpeg;base64,{BASE64_AUDIO}"
            }
        }]
    }],
    "asr_options": {"language": "zh"}
}
```

### 参数

| 参数 | 说明 | 值 |
|------|------|-----|
| `model` | 模型 | `mimo-v2.5-asr` |
| `language` | 语种 | `zh` / `en` / `auto` |

### 限制

- Base64 大小上限：10MB
- 超过自动分割处理

## 前置条件

1. **MiMo API Key**
   - 访问 https://token-plan-cn.xiaomimimo.com
   - 开通 Token Plan
   - 获取 API Key

2. **Python 3.7+**

3. **ffmpeg**（大文件分割用）
   ```bash
   # Windows (scoop)
   scoop install ffmpeg
   
   # macOS
   brew install ffmpeg
   
   # Ubuntu
   sudo apt install ffmpeg
   ```

4. **requests 库**
   ```bash
   pip install requests
   ```

## 注意事项

- ⚠️ **云端服务**：音频会上传到小米服务器
- ⚠️ **必须联网**：需要稳定的网络连接
- ⚠️ **专属地址**：Token Plan 用户必须使用 `https://token-plan-cn.xiaomimimo.com/v1`

## 许可证

MIT License
