#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2025/9/22 10:50
# @Author : Ray
# @File : logger.py
# @Software: PyCharm
"""
日志配置
"""
import sys
from loguru import logger

# --- Loguru 配置 ---
logger.remove()
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)