#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2025/9/22 11:12
# @Author : Ray
# @File : chat_service.py
# @Software: PyCharm
"""
聊天核心服务
"""

import os
import json
from openai import OpenAI, APIError
from . import character_manager
from backend.utils.logger import logger
from backend.errors.exceptions import KimiServiceError, ApiResponseParseError

# --- 初始化 Kimi API 客户端 ---
client = OpenAI(
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("API_BASE"),
)
llm_model = os.getenv("MODEL")


def process_chat_interaction(character_id: str, user_message: str, history: list) -> dict:
    """
    处理一次完整的聊天交互。
    在遇到问题时会引发特定异常。
    """
    # 1. 加载角色的系统提示
    system_prompt = character_manager.get_character_prompt(character_id)

    # 2. 构建发送给Kimi的消息列表
    messages = [
        {"role": "system", "content": system_prompt},
    ]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    # 3. 调用Kimi API
    try:
        logger.info(f"向Kimi API发送请求, 角色: {character_id}, 模型: {llm_model}")
        completion = client.chat.completions.create(
            model=llm_model,
            messages=messages,
            temperature=0.3,
        )
        kimi_response_str = completion.choices[0].message.content
        logger.info("成功从Kimi API收到响应。")

    except APIError as e:
        logger.error(f"调用Kimi API时发生APIError: {e}")
        raise KimiServiceError("AI服务接口返回错误。")
    except Exception as e:
        logger.error(f"调用Kimi API时发生未知错误: {e}")
        raise KimiServiceError("与AI服务通信时发生未知网络或配置错误。")

    # 4. 解析Kimi返回的JSON字符串
    try:
        parsed_response = json.loads(kimi_response_str)
        if "response" not in parsed_response or "emotion" not in parsed_response:
            logger.error(f"Kimi返回的JSON缺少必要字段。收到的内容: {kimi_response_str}")
            raise ValueError("Kimi返回的JSON缺少'response'或'emotion'字段")

        return parsed_response

    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"解析Kimi响应时出错: {e}。收到的原始字符串: {kimi_response_str}")
        raise ApiResponseParseError("无法解析AI服务的响应格式。")

