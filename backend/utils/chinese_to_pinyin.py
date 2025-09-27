#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2025/9/27 12:11
# @Author : Ray
# @File : chinese_to_pinyin.py
# @Software: PyCharm
"""
中文转拼音
"""

from pypinyin import pinyin, Style
import re


def chinese_to_pinyin(cn_name):
    """将中文名称转换为拼音（小写，用下划线连接）"""
    pinyin_list = pinyin(cn_name, style=Style.NORMAL, errors='ignore')
    pinyin_str = '_'.join([item[0] for item in pinyin_list])
    pinyin_str = re.sub(r'[^\w_]', '', pinyin_str).lower()
    return pinyin_str
