#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2025/9/22 10:48
# @Author : Ray
# @File : app.py
# @Software: PyCharm
"""
flask应用主文件
"""
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

from dotenv import load_dotenv

from backend.errors.exceptions import MissingParameterError, InvalidAPIRequest, FulingException

load_dotenv()

from backend.utils.logger import logger
from backend.services import chat_service, character_manager, tts_service, database_manager
from backend.errors.error_handlers import api_error_handler, register_error_handlers


# 初始化Flask应用
app = Flask(__name__)
CORS(app)
app.register_error_handler(FulingException, api_error_handler)

with app.app_context():
    database_manager.initialize_database()


# --- API 路由 ---
@app.route('/api/characters', methods=['GET'])
@api_error_handler
def get_characters_list():
    """
    获取所有可用角色的列表。
    """
    logger.info("请求获取所有角色列表...")
    characters = character_manager.get_all_characters()
    logger.info(f"成功加载 {len(characters)} 个角色。")
    return jsonify(characters)


@app.route('/api/chat', methods=['POST'])
@api_error_handler
def chat():
    """
    核心聊天接口，处理用户的对话请求。
    """
    try:
        data = request.get_json()
        character_id = data.get("characterId")
        user_message = data.get("message")
        history = data.get("history", [])
        conversation_id = data.get('conversationId')
        if not conversation_id:
            conversation_id = database_manager.create_conversation(character_id)
        logger.info(f"收到来自角色 '{character_id}' 的聊天请求,, 对话ID: {conversation_id}")

        response_data = chat_service.process_chat_interaction(
            character_id, user_message, history
        )
        response_data['conversationId'] = conversation_id
        logger.info(f"成功生成对角色 '{character_id}' 的回复, 对话ID: {conversation_id}")
        return jsonify(response_data)
    except FulingException as e:
        return jsonify({"error": e.message, "code": e.status_code}), e.status_code
    except Exception as e:
        logger.critical(f"Unhandled Exception in /api/chat: {e}", exc_info=True)
        return jsonify({"error": "服务器内部发生未知错误", "code": 500}), 500

@app.route('/api/speech', methods=['POST'])
@api_error_handler
def generate_audio():
    """新的TTS接口，根据文本和音色类型生成语音。"""
    data = request.get_json()
    text = data.get("text")
    voice_type = data.get("voiceType")
    logger.info(data)
    emotion = data.get("emotion", "default")

    if not text or not voice_type:
        raise MissingParameterError("请求缺少 'text' 或 'voiceType' 参数。")

    logger.info(f"收到语音生成请求，音色: {voice_type}")

    # 调用新的TTS服务
    base64_audio = tts_service.generate_speech(text, voice_type, emotion)

    logger.info("成功生成Base64音频数据并返回给前端。")
    return jsonify({"audioData": base64_audio})


@app.route('/api/conversations/<character_id>', methods=['GET'])
@api_error_handler
def get_character_conversations(character_id):
    """获取与特定角色的历史对话列表"""
    conversations = database_manager.get_conversations_by_character(character_id)
    return jsonify(conversations)


@app.route('/api/conversations/<conversation_id>', methods=['DELETE'])
@api_error_handler
def delete_conversation_by_id(conversation_id):
    """删除指定的对话"""
    database_manager.delete_conversation(conversation_id)
    return jsonify({"status": "success", "message": "对话已删除"})


@app.route('/api/conversations/<conversation_id>/summarize', methods=['POST'])
@api_error_handler
def summarize_and_end_conversation(conversation_id):
    """为对话生成并保存摘要"""
    data = request.get_json()
    history = data.get("history", [])

    if not history:
        raise InvalidAPIRequest("请求缺少'history'字段")

    summary = chat_service.summarize_conversation(history)
    first_message = history[0].get('content', '') if history else ''

    database_manager.update_conversation_summary(conversation_id, summary, first_message)
    return jsonify({"status": "success", "summary": summary})




# --- 启动应用 ---
if __name__ == '__main__':
    logger.info("Fuling应用启动...")
    app.run(debug=True, port=5123)
