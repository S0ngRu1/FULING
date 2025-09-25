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
from . import character_manager, rag_service
from backend.utils.logger import logger
from backend.errors.exceptions import KimiServiceError, ApiResponseParseError

# --- 初始化 Kimi API 客户端 ---
client = OpenAI(
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("API_BASE"),
)
llm_model = os.getenv("MODEL")

RAG_PROMPT_TEMPLATE = """
你现在扮演 {character_name}。
严格且仅仅根据下面提供的“背景资料”来回答用户的问题。
绝对禁止使用你的通用知识库进行任何补充或想象。
如果背景资料中没有足够的信息来回答问题，你必须明确地回答：“关于那个案件，我的记忆有些模糊，无法提供确切的细节。”

---
背景资料:
{context}
---
"""


def process_chat_interaction(character_id: str, user_message: str, history: list) -> dict:
    """
    处理聊天交互，会根据角色和问题类型决定是否启用RAG。
    """
    character_data = character_manager.get_character_data(character_id)

    # --- RAG 流程 ---
    if character_data.get("rag_enabled") and rag_service.is_knowledge_query(user_message):
        logger.info(f"检测到知识型问题，为角色 '{character_id}' 启动RAG流程。")
        context = rag_service.retrieve_context(character_id, user_message)

        if context:
            # 如果找到了相关上下文，构建RAG prompt
            system_prompt = RAG_PROMPT_TEMPLATE.format(
                character_name=character_data["name"],
                context=context
            )
            # RAG流程不使用历史记录，以确保回答的精确性
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        else:
            # 没找到上下文，直接返回一个预设的、表示不知道的回答
            return {
                "text": "关于这个问题，我手头的案卷里似乎没有相关记录。",
                "emotion": "沉思"
            }
    else:
        # --- 普通聊天流程 ---
        system_prompt = character_manager.get_character_prompt(character_id)
        messages = [
            {"role": "system", "content": system_prompt},
        ]
        messages.extend(history)
        messages.append({"role": "user", "content": user_message})

    # ---  将API调用和解析逻辑移到if/else外部，成为公共流程 ---
    try:
        logger.info(f"向Kimi API发送请求, 角色: {character_id}, 模型: {llm_model}")
        completion = client.chat.completions.create(
            model=llm_model,
            messages=messages,
            temperature=0.5,
        )
        kimi_response_str = completion.choices[0].message.content
        logger.info("成功从Kimi API收到响应。")

    except APIError as e:
        logger.error(f"调用Kimi API时发生APIError: {e}")
        raise KimiServiceError("AI服务接口返回错误。")
    except Exception as e:
        logger.error(f"调用Kimi API时发生未知错误: {e}")
        raise KimiServiceError("与AI服务通信时发生未知网络或配置错误。")

    # --- 公共的响应解析流程 ---
    try:
        parsed_response = json.loads(kimi_response_str)

        # 即使是RAG，也让模型返回情绪，若没有则提供默认值
        if "response" not in parsed_response:
            raise ValueError("Kimi返回的JSON缺少'response'字段")

        # 确保返回的字典键名统一为 'text' 和 'emotion'
        return {
            "text": parsed_response["response"],
            "emotion": parsed_response.get("emotion", "专注")  # 为RAG提供一个默认情绪
        }

    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"解析Kimi响应时出错: {e}。收到的原始字符串: {kimi_response_str}")
        # **优化**: 如果RAG返回的不是JSON，而是纯文本，我们也进行处理
        if not kimi_response_str.strip().startswith('{'):
            return {"text": kimi_response_str, "emotion": "专注"}
        raise ApiResponseParseError("无法解析AI服务的响应格式。")
