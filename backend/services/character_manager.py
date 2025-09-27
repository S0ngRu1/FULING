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

from backend.utils.chinese_to_pinyin import chinese_to_pinyin
from backend.utils.logger import logger
from backend.errors.exceptions import CharacterNotFound

_SERVICE_DIR = os.path.dirname(__file__)
CHARACTERS_DIR = os.path.abspath(os.path.join(_SERVICE_DIR, '..', 'characters'))
KNOWLEDGE_BASE_DIR = os.path.abspath(os.path.join(_SERVICE_DIR, '..', 'knowledge_base'))

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

    required_keys = ["id", "name", "description", "imageUrl", "voiceType"]
    for filename in os.listdir(CHARACTERS_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(CHARACTERS_DIR, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                    if all(k in data for k in required_keys):
                        characters.append(data)
                    else:
                        missing_keys = [k for k in required_keys if k not in data]
                        logger.warning(f"角色文件 {filename} 缺少必要字段: {missing_keys}，已跳过。")

            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"加载或读取角色文件 {filename} 时出错: {e}，已跳过。")
            except Exception as e:
                logger.critical(f"处理角色文件 {filename} 时发生未知严重错误: {e}，已跳过。", exc_info=True)

    return characters


def get_character_data(character_id: str) -> dict:
    """根据角色ID加载完整的角色数据字典"""
    filepath = os.path.join(CHARACTERS_DIR, f"{character_id}.json")
    if not os.path.exists(filepath):
        raise CharacterNotFound(f"角色 '{character_id}' 的配置文件未找到。")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"加载角色数据文件 {filepath} 时出错: {e}")
        raise CharacterNotFound(f"角色 '{character_id}' 的配置文件无效或已损坏。")


def create_character(name: str, description: str, voice_type: str, image_file):
    """
    创建并保存一个新的角色配置文件和图片。
    """
    logger.info(f"开始创建新角色: {name}")
    # 1. 生成角色ID
    if any('\u4e00' <= c <= '\u9fff' for c in name):  # 判断是否包含中文
        pinyin_name = chinese_to_pinyin(name)
        character_id = pinyin_name.replace(' ', '_').replace('.', '')
    else:
        character_id = name.lower().replace(' ', '_').replace('.', '')
    # 2. 定义并保存图片
    frontend_public_path = os.path.abspath(os.path.join(_SERVICE_DIR, '..', '..', 'frontend', 'public'))
    image_dir = os.path.join(frontend_public_path, 'assets', 'characters')
    os.makedirs(image_dir, exist_ok=True)

    # 获取文件扩展名，默认为.png
    _, ext = os.path.splitext(image_file.filename)
    if not ext: ext = '.png'
    image_filename = f"{character_id}{ext}"
    image_path = os.path.join(image_dir, image_filename)
    image_file.save(image_path)
    logger.info(f"角色图片已保存至: {image_path}")
    image_url = f"/assets/characters/{image_filename}"

    # 3. 生成默认的 system_prompt
    system_prompt = (
        f"你现在扮演一个名为 {name} 的角色。你的性格和背景如下：{description}。\n\n"
        "**最关键的指令**：你的所有回复都必须是一个格式正确的、单一的JSON对象，绝对不能包含任何JSON以外的额外文本。"
        "此JSON对象必须包含两个键：\n"
        "1. `\"response\"`: 你的对话内容，类型为字符串。\n"
        "2. `\"emotion\"`: 你当前的情绪状态，类型为字符串。情绪可以是 [\"专注\", \"开心\", \"好奇\", \"严肃\", \"鼓励\"] 中的一个。"
    )

    # 4. 构建角色数据字典
    character_data = {
        "id": character_id,
        "name": name,
        "description": description,
        "imageUrl": image_url,
        "voiceType": voice_type,
        "system_prompt": system_prompt
    }

    # 5. 创建并写入 .json 文件
    json_filepath = os.path.join(CHARACTERS_DIR, f"{character_id}.json")
    with open(json_filepath, 'w', encoding='utf-8') as f:
        json.dump(character_data, f, ensure_ascii=False, indent=2)

    logger.info(f"角色配置文件已创建: {json_filepath}")

