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

import requests
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

# 配置CORS - 根据实际需求调整
CORS(app, resources={
    r"/api/*": {
        "origins": "*",  # 生产环境应限制为具体域名
        "methods": ["GET", "POST", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# 设置请求体大小限制（16MB，适用于文件上传）
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# 注册错误处理器
app.register_error_handler(FulingException, api_error_handler)
register_error_handlers(app)

# 验证必要的环境变量
def validate_environment():
    """验证应用启动所需的环境变量"""
    required_vars = []
    optional_vars = ["API_KEY", "API_BASE", "MODEL"]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.warning(f"缺少以下环境变量: {missing_vars}")
    
    # 检查TTS相关配置（可选）
    if not os.getenv("API_KEY") or not os.getenv("API_BASE"):
        logger.warning("TTS服务配置未完整，/api/voices 端点可能无法正常工作")

# 初始化数据库
with app.app_context():
    database_manager.initialize_database()
    validate_environment()


# --- API 路由 ---
@app.route('/api/characters', methods=['GET'])
@api_error_handler
def get_characters_list():
    """
    获取所有可用角色的列表。
    """
    logger.info("收到获取角色列表请求")
    characters = character_manager.get_all_characters()
    logger.info(f"成功返回 {len(characters)} 个角色")
    return jsonify(characters)


@app.route('/api/characters', methods=['POST'])
@api_error_handler
def create_new_character():
    """处理新角色的创建请求"""
    logger.info("收到创建新角色请求")
    
    # 从 multipart/form-data 中获取数据
    name = request.form.get('name')
    description = request.form.get('description')
    voice_type = request.form.get('voiceType')
    image_file = request.files.get('image')

    if not all([name, description, voice_type, image_file]):
        raise InvalidAPIRequest("创建角色所需的所有字段均为必填项。")

    character_manager.create_character(name, description, voice_type, image_file)
    logger.info(f"成功创建角色: {name}")
    return jsonify({"status": "success", "message": "角色创建成功！"})


@app.route('/api/voices', methods=['GET'])
@api_error_handler
def get_voice_list():
    """从TTS服务获取音色列表"""
    logger.info("收到获取音色列表请求")
    
    qiniu_api_key = os.getenv("API_KEY")
    qiniu_base_url = os.getenv("API_BASE")
    if not qiniu_api_key or not qiniu_base_url:
        raise FulingException("TTS服务未在后端配置。", 500)

    url = f"{qiniu_base_url}/voice/list"
    headers = {"Authorization": f"Bearer {qiniu_api_key}"}

    try:
        # 添加超时设置，避免长时间等待
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # 确保请求成功
        logger.info("成功获取音色列表")
        return jsonify(response.json())
    except requests.exceptions.Timeout:
        logger.error("获取音色列表请求超时")
        raise FulingException("获取音色列表请求超时，请稍后重试。", 504)
    except requests.exceptions.RequestException as e:
        logger.error(f"获取音色列表时发生网络错误: {e}")
        raise FulingException("无法连接到TTS服务。", 503)


@app.route('/api/chat', methods=['POST'])
@api_error_handler
def chat():
    """
    核心聊天接口，处理用户的对话请求。
    """
    data = request.get_json()
    if not data:
        raise InvalidAPIRequest("请求体不能为空")
    
    character_id = data.get("characterId")
    user_message = data.get("message")
    history = data.get("history", [])
    conversation_id = data.get('conversationId')
    
    if not character_id or not user_message:
        raise MissingParameterError("请求缺少 'characterId' 或 'message' 参数")
    
    if not conversation_id:
        conversation_id = database_manager.create_conversation(character_id)
    
    logger.info(f"收到聊天请求 - 角色: {character_id}, 对话ID: {conversation_id}")

    response_data = chat_service.process_chat_interaction(
        character_id, user_message, history
    )
    response_data['conversationId'] = conversation_id
    logger.info(f"成功生成回复 - 角色: {character_id}, 对话ID: {conversation_id}")
    return jsonify(response_data)


@app.route('/api/speech', methods=['POST'])
@api_error_handler
def generate_audio():
    """TTS接口，根据文本和音色类型生成语音。"""
    data = request.get_json()
    if not data:
        raise InvalidAPIRequest("请求体不能为空")
    
    text = data.get("text")
    voice_type = data.get("voiceType")
    emotion = data.get("emotion", "default")

    if not text or not voice_type:
        raise MissingParameterError("请求缺少 'text' 或 'voiceType' 参数。")

    logger.info(f"收到语音生成请求 - 音色: {voice_type}, 情绪: {emotion}")

    # 调用TTS服务
    base64_audio = tts_service.generate_speech(text, voice_type, emotion)

    logger.info("成功生成音频数据")
    return jsonify({"audioData": base64_audio})


@app.route('/api/conversations/<character_id>', methods=['GET'])
@api_error_handler
def get_character_conversations(character_id):
    """获取与特定角色的历史对话列表"""
    logger.info(f"收到获取对话历史请求 - 角色: {character_id}")
    conversations = database_manager.get_conversations_by_character(character_id)
    logger.info(f"成功返回 {len(conversations)} 条对话记录")
    return jsonify(conversations)


@app.route('/api/conversations/<conversation_id>', methods=['DELETE'])
@api_error_handler
def delete_conversation_by_id(conversation_id):
    """删除指定的对话"""
    logger.info(f"收到删除对话请求 - 对话ID: {conversation_id}")
    database_manager.delete_conversation(conversation_id)
    logger.info(f"成功删除对话 - 对话ID: {conversation_id}")
    return jsonify({"status": "success", "message": "对话已删除"})


@app.route('/api/conversations/<conversation_id>/summarize', methods=['POST'])
@api_error_handler
def summarize_and_end_conversation(conversation_id):
    """为对话生成并保存摘要"""
    data = request.get_json()
    if not data:
        raise InvalidAPIRequest("请求体不能为空")
    
    history = data.get("history", [])

    if not history:
        raise InvalidAPIRequest("请求缺少'history'字段")

    logger.info(f"收到生成对话摘要请求 - 对话ID: {conversation_id}")
    summary = chat_service.summarize_conversation(history)
    first_message = history[0].get('content', '') if history else ''

    database_manager.update_conversation_summary(conversation_id, summary, first_message)
    logger.info(f"成功生成并保存对话摘要 - 对话ID: {conversation_id}")
    return jsonify({"status": "success", "summary": summary})


# --- 健康检查端点 ---
@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查端点，用于监控服务状态"""
    return jsonify({
        "status": "healthy",
        "service": "Fuling API"
    })


# --- 启动应用 ---
if __name__ == '__main__':
    logger.info("Fuling应用启动...")
    app.run(debug=False, port=5123, host='0.0.0.0')
