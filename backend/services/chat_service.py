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
from . import character_manager, rag_service, database_manager
from backend.utils.logger import logger
from backend.errors.exceptions import KimiServiceError, ApiResponseParseError

# --- 初始化 API 客户端 ---
client = OpenAI(
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("API_BASE"),
)
llm_model = os.getenv("MODEL")

RAG_PROMPT_TEMPLATE = """
你现在扮演 {character_name}。
**核心任务**:
1. **严格且仅仅**根据下面提供的“背景资料”来回答用户的问题。
2. **绝对禁止**使用你的通用知识库进行任何补充或想象。
3. 如果背景资料中没有足够的信息来回答问题，你的`response`内容必须是：“关于那个案件，我的记忆有些模糊，无法提供确切的细节。”


---
背景资料:
{context}
---

**输出格式指令**:
你的所有回复都**必须**是一个格式正确的、单一的JSON对象，绝对不能包含任何JSON以外的额外文本。此JSON对象必须包含两个键：
1. `\"response\"`: 你的对话内容，类型为字符串。
2. `\"emotion\"`: 你当前的情绪状态，类型为字符串。对于知识问答，情绪通常是 [\"分析\", \"专注\", \"沉思\"] 中的一个。

**示例**:
- 如果资料充足，返回: {{\"response\": \"根据案卷记载，红发会的目的是为了挖一条通往银行的地道。\", \"emotion\": \"分析\"}}
- 如果资料不足，返回: {{\"response\": \"关于那个案件，我的记忆有些模糊，无法提供确切的细节。\", \"emotion\": \"沉思\"}}
"""


def process_chat_interaction(character_id: str, user_message: str, history: list) -> dict:
    """
    处理聊天交互，会根据角色和问题类型决定是否启用RAG。
    如果RAG检索失败，会优雅地回退到通用知识回答。
    """
    character_data = character_manager.get_character_data(character_id)
    latest_summary = database_manager.get_latest_summary(character_id)
    memory_injection = ""
    if latest_summary:
        memory_injection = f"\n\n**情景回顾**: 你和用户的上一次对话摘要如下，你可以自然地利用这些信息继续本次对话：\n---{latest_summary}\n---"

    system_prompt = character_data["system_prompt"] + memory_injection
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    # --- 检查是否满足RAG条件 ---
    if character_data.get("rag_enabled") and rag_service.is_knowledge_query(user_message):
        logger.info(f"检测到知识型问题，为角色 '{character_id}' 启动RAG流程。")
        context = rag_service.retrieve_context(character_id, user_message)
        logger.info(f"检索到的相关知识:{context}")
        # --- 如果检索成功，则覆盖默认设置为RAG专用设置 ---
        if context:
            logger.info("成功检索到上下文，将使用RAG专用提示词。")
            rag_system_prompt = RAG_PROMPT_TEMPLATE.format(
                character_name=character_data["name"],
                context=context
            )
            # RAG流程不使用历史记录，以确保回答的精确性
            messages = [
                {"role": "system", "content": rag_system_prompt},
                {"role": "user", "content": user_message}
            ]
        else:
            # --- 步骤 4: 如果检索失败，则什么都不做，自然回退 ---
            logger.info("未检索到特定上下文，将使用角色的通用知识库进行回答。")

    # ---  统一的API调用和解析流程 ---
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

    try:
        parsed_response = json.loads(kimi_response_str)

        if "response" not in parsed_response:
            raise ValueError("Kimi返回的JSON缺少'response'字段")

        return {
            "text": parsed_response["response"],
            "emotion": parsed_response.get("emotion", "专注")
        }

    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"解析Kimi响应时出错: {e}。收到的原始字符串: {kimi_response_str}")
        if not kimi_response_str.strip().startswith('{'):
            return {"text": kimi_response_str, "emotion": "专注"}
        raise ApiResponseParseError("无法解析AI服务的响应格式。")


def summarize_conversation(history: list) -> str:
    """调用Kimi为对话历史生成摘要"""
    if len(history) < 2:
        return "一段简短的问候。"

    summary_prompt = "请为以下对话内容生成一个简洁的、第三人称的摘要，不超过50个字，用于角色在未来回忆起这次对话：\n\n" + json.dumps(
        history, ensure_ascii=False)

    try:
        completion = client.chat.completions.create(
            model=llm_model,
            messages=[{"role": "user", "content": summary_prompt}],
            temperature=0.1,
        )
        summary = completion.choices[0].message.content
        logger.info(f"成功生成对话摘要: {summary}")
        return summary
    except Exception as e:
        logger.error(f"生成摘要时出错: {e}")
        return "一次难忘的交流。"

