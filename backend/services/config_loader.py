#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2025/9/24 11:48
# @Author : Ray
# @File : config_loader.py
# @Software: PyCharm
"""
配置加载
"""
import os
import json
from backend.utils.logger import logger

# 构建到config目录的绝对路径
_SERVICE_DIR = os.path.dirname(__file__)
CONFIG_DIR = os.path.abspath(os.path.join(_SERVICE_DIR, '..', 'config'))


def load_tts_config() -> dict:
    """
    加载并返回TTS情感配置文件。
    """
    filepath = os.path.join(CONFIG_DIR, "tts_config.json")
    logger.info(f"正在从 {filepath} 加载TTS配置...")

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            config = json.load(f)
            # 返回核心的映射字典
            return config.get("emotion_to_speed_map", {})
    except FileNotFoundError:
        logger.error(f"TTS配置文件未找到: {filepath}")
        return {}
    except json.JSONDecodeError:
        logger.error(f"TTS配置文件格式错误: {filepath}")
        return {}
    except Exception as e:
        logger.error(f"加载TTS配置文件时发生未知错误: {e}")
        return {}
