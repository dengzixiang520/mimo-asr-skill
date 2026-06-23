#!/usr/bin/env python3
"""
MiMo ASR 语音转文字工具
使用小米 MiMo-V2.5-ASR 模型将音频文件转换为文字
"""

import os
import sys
import base64
import glob
import subprocess
import requests
import json
import shutil
import argparse
from pathlib import Path

# 默认配置
DEFAULT_BASE_URL = "https://token-plan-cn.xiaomimimo.com/v1"
DEFAULT_MODEL = "mimo-v2.5-asr"
DEFAULT_LANGUAGE = "zh"
DEFAULT_CHUNK_DURATION = 300  # 5分钟
MAX_BASE64_SIZE = 8 * 1024 * 1024  # 8MB（留一些余量）

class MiMoASR:
    def __init__(self, api_key, base_url=None):
        self.api_key = api_key
        self.base_url = base_url or DEFAULT_BASE_URL
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    
    def get_audio_duration(self, audio_file):
        """获取音频时长（秒）"""
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", audio_file],
            capture_output=True, text=True
        )
        return float(result.stdout.strip())
    
    def split_audio(self, input_file, chunk_duration=DEFAULT_CHUNK_DURATION):
        """分割音频文件"""
        chunk_dir = f"chunks_{Path(input_file).stem}"
        os.makedirs(chunk_dir, exist_ok=True)
        
        duration = self.get_audio_duration(input_file)
        chunks = []
        start = 0
        index = 0
        
        while start < duration:
            chunk_file = os.path.join(chunk_dir, f"chunk_{index:03d}.mp3")
            subprocess.run([
                "ffmpeg", "-i", input_file, "-ss", str(start),
                "-t", str(chunk_duration), "-c", "copy", chunk_file,
                "-y", "-loglevel", "error"
            ])
            chunks.append(chunk_file)
            start += chunk_duration
            index += 1
        
        return chunks, chunk_dir
    
    def transcribe_chunk(self, audio_file, language=DEFAULT_LANGUAGE):
        """转写单个音频片段"""
        with open(audio_file, "rb") as f:
            audio_bytes = f.read()
        
        # 检查大小
        audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
        if len(audio_base64) > MAX_BASE64_SIZE:
            raise Exception(f"音频片段过大: {len(audio_base64)} bytes")
        
        data = {
            "model": DEFAULT_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_audio",
                            "input_audio": {
                                "data": f"data:audio/mpeg;base64,{audio_base64}"
                            }
                        }
                    ]
                }
            ],
            "asr_options": {
                "language": language
            }
        }
        
        # 重试机制
        for attempt in range(3):
            try:
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=data,
                    timeout=300
                )
                
                if response.status_code == 200:
                    return response.json()["choices"][0]["message"]["content"]
                elif response.status_code == 401:
                    raise Exception("API Key 无效，请检查配置")
                else:
                    raise Exception(f"API 错误: {response.status_code}, {response.text}")
                    
            except requests.exceptions.RequestException as e:
                if attempt < 2:
                    print(f"  ⚠️ 请求失败，重试 {attempt + 1}/3...")
                    continue
                raise
        
        return None
    
    def transcribe_file(self, audio_file, language=DEFAULT_LANGUAGE):
        """转写整个音频文件"""
        print(f"\n{'='*50}")
        print(f"📄 处理文件: {audio_file}")
        print('='*50)
        
        # 检查文件大小
        file_size = os.path.getsize(audio_file)
        print(f"📊 文件大小: {file_size / 1024 / 1024:.1f} MB")
        
        # 如果文件较小，直接转写
        if file_size < MAX_BASE64_SIZE * 0.75:  # 留一些余量
            print("✅ 文件较小，直接转写...")
            return self.transcribe_chunk(audio_file, language)
        
        # 文件较大，需要分割
        print("📦 文件较大，分割处理中...")
        chunks, chunk_dir = self.split_audio(audio_file)
        print(f"✂️ 分割成 {len(chunks)} 个片段")
        
        full_text = []
        for i, chunk in enumerate(chunks):
            print(f"\n🎤 转写片段 {i+1}/{len(chunks)}...")
            text = self.transcribe_chunk(chunk, language)
            full_text.append(text)
            preview = text[:50] + "..." if len(text) > 50 else text
            print(f"   {preview}")
        
        # 清理临时文件
        shutil.rmtree(chunk_dir)
        print("🧹 清理临时文件完成")
        
        return "\n\n".join(full_text)
    
    def transcribe_directory(self, directory, language=DEFAULT_LANGUAGE):
        """批量转写目录中的音频文件"""
        audio_files = []
        for ext in ["*.mp3", "*.wav"]:
            audio_files.extend(glob.glob(os.path.join(directory, ext)))
        
        if not audio_files:
            print("❌ 未找到音频文件")
            return
        
        print(f"📁 找到 {len(audio_files)} 个音频文件")
        
        results = {}
        for audio_file in audio_files:
            try:
                text = self.transcribe_file(audio_file, language)
                results[audio_file] = text
                
                # 保存结果
                output_file = audio_file.rsplit(".", 1)[0] + ".txt"
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(text)
                print(f"💾 已保存到: {output_file}")
                
            except Exception as e:
                print(f"❌ 处理失败: {audio_file}")
                print(f"   错误: {e}")
                results[audio_file] = None
        
        return results


def main():
    parser = argparse.ArgumentParser(description="MiMo ASR 语音转文字工具")
    parser.add_argument("path", help="音频文件或目录路径")
    parser.add_argument("--api-key", help="API Key（或设置 MIMO_API_KEY 环境变量）")
    parser.add_argument("--base-url", help="Base URL（默认使用 Token Plan 专属地址）")
    parser.add_argument("--language", default=DEFAULT_LANGUAGE, help="语种：zh/en/auto（默认：zh）")
    parser.add_argument("--chunk-duration", type=int, default=DEFAULT_CHUNK_DURATION, help="分割时长（秒，默认：300）")
    
    args = parser.parse_args()
    
    # 获取 API Key
    api_key = args.api_key or os.environ.get("MIMO_API_KEY")
    if not api_key:
        print("❌ 请提供 API Key")
        print("   方法1: --api-key YOUR_KEY")
        print("   方法2: 设置环境变量 MIMO_API_KEY")
        sys.exit(1)
    
    # 检查 ffmpeg
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
    except FileNotFoundError:
        print("❌ 未找到 ffmpeg，请先安装")
        print("   下载地址: https://www.gyan.dev/ffmpeg/builds/")
        sys.exit(1)
    
    # 创建 ASR 实例
    asr = MiMoASR(api_key, args.base_url)
    
    # 处理路径
    path = args.path
    if os.path.isdir(path):
        asr.transcribe_directory(path, args.language)
    elif os.path.isfile(path):
        text = asr.transcribe_file(path, args.language)
        output_file = path.rsplit(".", 1)[0] + ".txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"\n💾 已保存到: {output_file}")
    else:
        print(f"❌ 路径不存在: {path}")
        sys.exit(1)
    
    print(f"\n{'='*50}")
    print("✅ 转写完成！")


if __name__ == "__main__":
    main()
