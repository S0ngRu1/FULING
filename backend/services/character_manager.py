#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2025/9/22 10:29
# @Author : 19229
# @File : character_manager.py
# @Software: PyCharm
"""
角色管理服务
"""
import os
import json
from backend.utils.logger import logger
from backend.errors.exceptions import CharacterNotFound

_SERVICE_DIR = os.path.dirname(__file__)
CHARACTERS_DIR = os.path.abspath(os.path.join(_SERVICE_DIR, '..', 'characters'))

def get_character_prompt(character_id: str) -> str:
    """
    根据角色ID从JSON文件中加载系统提示。
    如果找不到文件或加载失败，则引发CharacterNotFound异常。
    """
    filepath = os.path.join(CHARACTERS_DIR, f"{character_id}.json")

    if not os.path.exists(filepath):
        logger.warning(f"尝试加载一个不存在的角色文件: {filepath}")
        raise CharacterNotFound(f"角色 '{character_id}' 的配置文件未找到。")

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            character_data = json.load(f)
            prompt = character_data.get("system_prompt")
            if not prompt:
                raise ValueError("JSON文件中缺少 'system_prompt' 键。")
            return prompt
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"加载或解析角色文件 {filepath} 时出错: {e}")
        raise CharacterNotFound(f"角色 '{character_id}' 的配置文件无效或已损坏。")


def get_all_characters() -> list:
    """
    加载并返回所有角色的基本信息列表。
    """
    characters = []
    if not os.path.exists(CHARACTERS_DIR):
        logger.warning(f"角色目录 '{CHARACTERS_DIR}' 不存在。")
        return []

    for filename in os.listdir(CHARACTERS_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(CHARACTERS_DIR, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if all(k in data for k in ["id", "name", "description"]):
                        characters.append({
                            "id": data["id"],
                            "name": data["name"],
                            "description": data["description"]
                        })
                    else:
                        logger.warning(f"角色文件 {filename} 缺少必要字段 (id, name, description)，已跳过。")
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"加载或读取角色文件 {filename} 时出错: {e}，已跳过。")
            except Exception as e:
                logger.critical(f"处理角色文件 {filename} 时发生未知严重错误: {e}，已跳过。", exc_info=True)
    return characters

