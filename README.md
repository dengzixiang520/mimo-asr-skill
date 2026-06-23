# MiMo ASR Skill

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Claude Code Skill：使用小米 MiMo-V2.5-ASR 模型将音频文件转换为文字。

## ✨ 功能特性

- 🎤 支持 MP3、WAV 音频格式
- 📦 大文件自动分割处理（超过 8MB 自动用 ffmpeg 分割）
- 🌍 支持中英文及方言识别
- 📁 支持单文件和批量处理
- 🔄 自动重试机制

## 📋 前置条件

1. **Python 3.7+**
2. **ffmpeg**（用于分割大文件）
   ```bash
   # Windows (scoop)
   scoop install ffmpeg
   
   # Windows (chocolatey)
   choco install ffmpeg
   
   # macOS
   brew install ffmpeg
   
   # Ubuntu/Debian
   sudo apt install ffmpeg
   ```
3. **MiMo Token Plan 账号**
   - 访问 https://token-plan-cn.xiaomimimo.com
   - 开通 Token Plan
   - 获取 API Key

## 🚀 安装

### 作为 Claude Code Skill 使用

1. 克隆仓库到本地：
   ```bash
   git clone https://github.com/YOUR_USERNAME/mimo-asr-skill.git
   cd mimo-asr-skill
   ```

2. 将 skill 文件复制到你的项目：
   ```bash
   cp -r .claude/skills /path/to/your/project/.claude/
   ```

3. 在 Claude Code 中使用：
   ```
   /transcribe audio.mp3
   /transcribe ./audio_directory/
   ```

### 作为命令行工具使用

1. 克隆仓库：
   ```bash
   git clone https://github.com/YOUR_USERNAME/mimo-asr-skill.git
   cd mimo-asr-skill
   ```

2. 安装依赖：
   ```bash
   pip install requests
   ```

3. 设置环境变量：
   ```bash
   # Windows PowerShell
   $env:MIMO_API_KEY="tp-your-api-key"
   
   # Windows CMD
   set MIMO_API_KEY=tp-your-api-key
   
   # Linux/macOS
   export MIMO_API_KEY="tp-your-api-key"
   ```

4. 运行脚本：
   ```bash
   python transcribe.py audio.mp3
   python transcribe.py ./audio_directory/
   ```

## 📖 使用方法

### 命令行参数

```bash
python transcribe.py [OPTIONS] PATH

参数:
  PATH                  音频文件或目录路径

选项:
  --api-key TEXT       API Key（或设置 MIMO_API_KEY 环境变量）
  --base-url TEXT      Base URL（默认使用 Token Plan 专属地址）
  --language TEXT       语种：zh/en/auto（默认：zh）
  --chunk-duration INT 分割时长秒数（默认：300）
  --help               显示帮助信息
```

### 示例

```bash
# 转换单个文件
python transcribe.py interview.mp3

# 转换目录下所有音频
python transcribe.py ./recordings/

# 指定语种为英文
python transcribe.py english_lecture.mp3 --language en

# 自动检测语种
python transcribe.py unknown_language.mp3 --language auto

# 使用自定义 API Key
python transcribe.py audio.mp3 --api-key tp-your-key

# 指定分割时长为 3 分钟
python transcribe.py long_audio.mp3 --chunk-duration 180
```

### Claude Code Skill 使用

```
# 转换单个文件
/transcribe audio.mp3

# 转换目录
/transcribe ./recordings/

# 指定完整路径
/transcribe C:\Users\x\Desktop\audio.mp3
```

## ⚙️ 配置说明

### API 配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `MIMO_API_KEY` | - | MiMo API Key（必须） |
| `BASE_URL` | `https://token-plan-cn.xiaomimimo.com/v1` | API 地址 |
| `MODEL` | `mimo-v2.5-asr` | 模型名称 |
| `LANGUAGE` | `zh` | 语种 |
| `CHUNK_DURATION` | `300` | 分割时长（秒） |

### 音频格式

| 格式 | MIME 类型 | 说明 |
|------|-----------|------|
| MP3 | `audio/mpeg` | 推荐格式 |
| WAV | `audio/wav` | 无损格式 |

### 大小限制

- 单次请求 Base64 大小上限：10MB
- 建议分割阈值：8MB（留余量）
- 大文件自动分割成 5 分钟片段

## 🔧 常见问题

### Q: 报错 401 Invalid API Key

**A:** Token Plan 用户必须使用专属 Base URL：
```
https://token-plan-cn.xiaomimimo.com/v1
```
不是通用地址 `api.xiaomimimo.com`。

### Q: 报错 input_audio.data exceeds maximum size

**A:** 文件过大，脚本会自动分割。如果仍然报错，尝试减小 `--chunk-duration` 参数。

### Q: 识别结果不准确

**A:**
- 明确指定语种（`--language zh` 或 `--language en`）
- 确保音频清晰，避免过多噪音
- 尝试转换为 WAV 格式

### Q: 支持哪些语言？

**A:**
- `zh`：中文（及粤语、吴语、闽南语、四川话等方言）
- `en`：英文
- `auto`：自动检测

## 📊 计费说明

- 按 Token 计费
- Token Plan 用户有专属额度
- 非高峰期（00:00-08:00）消耗系数 0.8x
- TTS 系列模型限时免费

## 📁 项目结构

```
mimo-asr-skill/
├── .claude/
│   └── skills/
│       └── transcribe.md    # Claude Code Skill 定义
├── transcribe.py            # 主程序
├── README.md                # 项目说明
├── LICENSE                  # MIT 许可证
└── .gitignore              # Git 忽略文件
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🔗 相关链接

- [MiMo 官方文档](https://mimo.mi.com/docs/zh-CN/quick-start/usage-guide/audio/Speech-Recognition)
- [MiMo Token Plan](https://token-plan-cn.xiaomimimo.com)
- [ffmpeg 下载](https://www.gyan.dev/ffmpeg/builds/)

## 🙏 致谢

- [小米 MiMo](https://mimo.mi.com) 提供 ASR 服务
- [ffmpeg](https://ffmpeg.org) 提供音频处理能力
