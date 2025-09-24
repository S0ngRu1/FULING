#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2025/9/23 14:23
# @Author : Ray
# @File : tts_service.py
# @Software: PyCharm
"""
tts服务
"""
import os
import requests
from dotenv import load_dotenv
from backend.utils.logger import logger
from backend.errors.exceptions import TTSServiceError
from backend.services.config_loader import load_tts_config
load_dotenv()

# 从配置中获取七牛云的凭证
API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("API_BASE")

# 确保配置存在
if not API_KEY or not BASE_URL:
    raise RuntimeError("请在 .env 文件中配置 QINIU_API_KEY 和 QINIU_BASE_URL")

# 在模块加载时，从配置文件中读取情感映射
EMOTION_TO_SPEED_MAP = load_tts_config()
if not EMOTION_TO_SPEED_MAP:
    logger.warning("未能加载TTS情感配置，将使用默认语速。")


def generate_speech(text: str, voice_type: str, emotion: str = "default") -> str:
    """
    调用七牛云TTS API生成语音, 现在会根据外部配置文件调整语速。
    """
    tts_url = f"{BASE_URL}/voice/tts"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}
    # 从加载的配置中获取语速
    default_speed = EMOTION_TO_SPEED_MAP.get("default", 1.0)
    speed_ratio = EMOTION_TO_SPEED_MAP.get(emotion, default_speed)
    logger.info(f"情绪: '{emotion}', 映射语速为: {speed_ratio}")

    payload = {
        "audio": {"voice_type": voice_type, "encoding": "mp3", "speed_ratio": speed_ratio},
        "request": {"text": text}
    }

    try:
        response = requests.post(tts_url, headers=headers, json=payload, timeout=20)
        response.raise_for_status()
        response_data = response.json()

        if "data" in response_data and response_data["data"]:
            return response_data["data"]
        else:
            raise TTSServiceError("TTS服务返回的数据为空或格式不正确。")

    except requests.exceptions.RequestException as e:
        raise TTSServiceError(f"无法连接到TTS服务: {e}")

