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
load_dotenv()

from backend.utils.logger import logger
from backend.services import chat_service, character_manager
from backend.errors.error_handlers import api_error_handler, register_error_handlers
from backend.errors.exceptions import InvalidAPIRequest


# 初始化Flask应用
app = Flask(__name__)
CORS(app)

# 注册通用的HTTP错误处理器
register_error_handlers(app)

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
    data = request.get_json()
    character_id = data.get("characterId")
    user_message = data.get("message")
    history = data.get("history", [])

    logger.info(f"收到来自角色 '{character_id}' 的聊天请求")

    response_data = chat_service.process_chat_interaction(
        character_id, user_message, history
    )

    logger.info(f"成功生成对角色 '{character_id}' 的回复")
    logger.info(response_data)
    return jsonify(response_data)

# --- 启动应用 ---
if __name__ == '__main__':
    logger.info("Fuling应用启动...")
    app.run(debug=True, port=5000)
