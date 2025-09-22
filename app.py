#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2025/9/22 10:48
# @Author : Ray
# @File : app.py
# @Software: PyCharm
"""

"""
from dotenv import load_dotenv
load_dotenv()

from backend.utils.logger import logger
from backend.services import chat_service, character_manager
from backend.errors.error_handlers import api_error_handler, register_error_handlers
from backend.errors.exceptions import InvalidAPIRequest

from flask import Flask, request, jsonify
from flask_cors import CORS

# 初始化Flask应用
app = Flask(__name__)
CORS(app)

# 注册通用的HTTP错误处理器
register_error_handlers(app)

# --- API 路由 ---

@app.route('/api/chat', methods=['POST'])
@api_error_handler
def chat():
    """
    聊天接口路由
    """
    data = request.get_json()
    if not data:
        raise InvalidAPIRequest("请求体不能为空或非JSON格式。")

    character_id = data.get("characterId")
    user_message = data.get("message")

    if not character_id or not user_message:
        raise InvalidAPIRequest("请求中缺少 'characterId' 或 'message'。")

    history = data.get("history", [])

    response_data = chat_service.process_chat_interaction(
        character_id=character_id,
        user_message=user_message,
        history=history
    )

    return jsonify(response_data)


@app.route('/api/characters', methods=['GET'])
@api_error_handler
def get_characters():
    """
    获取所有角色列表的接口。
    """
    all_chars = character_manager.get_all_characters()
    logger.info(f"成功获取到 {len(all_chars)} 个角色列表。")
    return jsonify(all_chars)


# --- 启动应用 ---
if __name__ == '__main__':
    logger.info("Fuling应用启动...")
    app.run(debug=True, port=5000)
