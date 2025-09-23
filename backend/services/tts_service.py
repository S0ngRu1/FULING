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

# 加载环境变量
load_dotenv()

# 从配置中获取七牛云的凭证
API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("API_BASE")

# 确保配置存在
if not API_KEY or not BASE_URL:
    raise RuntimeError("请在 .env 文件中配置 API_KEY 和 API_BASE")


def generate_speech(text: str, voice_type: str, speed_ratio: float = 1.0) -> str:
    """
    调用七牛云TTS API生成语音。

    :param text: 需要合成的文本
    :param voice_type: 音色类型
    :param speed_ratio: 语速
    :return: Base64编码的音频数据字符串
    :raises TTSServiceError: 如果API调用失败
    """

    tts_url = f"{BASE_URL}/voice/tts"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    payload = {
        "audio": {
            "voice_type": voice_type,
            "encoding": "mp3",  # 我们请求MP3格式
            "speed_ratio": speed_ratio
        },
        "request": {
            "text": text
        }
    }

    logger.info(f"向七牛云TTS发送请求，音色: {voice_type}")

    try:
        response = requests.post(tts_url, headers=headers, json=payload, timeout=20)
        response.raise_for_status()  # 如果状态码不是2xx，则抛出HTTPError

        response_data = response.json()

        if "data" in response_data and response_data["data"]:
            logger.info("成功从七牛云TTS获取音频数据。")
            return response_data["data"]
        else:
            logger.error(f"七牛云TTS响应格式不正确: {response_data}")
            raise TTSServiceError("TTS服务返回的数据为空或格式不正确。")

    except requests.exceptions.RequestException as e:
        logger.error(f"调用七牛云TTS API时发生网络错误: {e}")
        raise TTSServiceError(f"无法连接到TTS服务: {e}")
    except Exception as e:
        logger.error(f"处理七牛云TTS响应时发生未知错误: {e}")
        raise TTSServiceError(f"处理TTS响应时出错: {e}")
