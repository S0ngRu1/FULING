#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2025/9/26 15:25
# @Author : Ray
# @File : database_manager.py
# @Software: PyCharm
"""
数据库管理服务
"""
import os
import sqlite3
import uuid
from datetime import datetime
from backend.utils.logger import logger

_BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_PATH = os.path.join(_BACKEND_DIR, 'fuling_memory.db')


def get_db_connection():
    """建立并返回数据库连接"""
    logger.debug(f"正在连接数据库: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    """初始化数据库，创建必要的表"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 创建对话表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            character_id TEXT NOT NULL,
            user_id TEXT NOT NULL, -- 备用，未来可用于多用户
            summary TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            first_message TEXT
        )
    ''')

    logger.info("数据库表 'conversations' 已确认存在。")
    conn.commit()
    conn.close()


def create_conversation(character_id: str, user_id: str = "default_user") -> str:
    """创建一个新的对话记录，并返回其ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    new_id = str(uuid.uuid4())
    cursor.execute(
        "INSERT INTO conversations (id, character_id, user_id) VALUES (?, ?, ?)",
        (new_id, character_id, user_id)
    )
    conn.commit()
    conn.close()
    logger.info(f"为角色 {character_id} 创建了新的对话，ID: {new_id}")
    return new_id


def get_latest_summary(character_id: str, user_id: str = "default_user") -> str | None:
    """获取指定角色最近一次的对话摘要"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT summary FROM conversations WHERE character_id = ? AND user_id = ? AND summary IS NOT NULL ORDER BY updated_at DESC LIMIT 1",
        (character_id, user_id)
    )
    row = cursor.fetchone()
    conn.close()
    if row and row['summary']:
        logger.info(f"为角色 {character_id} 找到了最近的记忆摘要。")
        return row['summary']
    return None


def update_conversation_summary(conversation_id: str, summary: str, first_message: str):
    """更新对话的摘要和首条消息"""
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.utcnow()
    cursor.execute(
        "UPDATE conversations SET summary = ?, first_message = ?, updated_at = ? WHERE id = ?",
        (summary, first_message, now, conversation_id)
    )
    conn.commit()
    conn.close()
    logger.info(f"更新了对话 {conversation_id} 的摘要。")


def get_conversations_by_character(character_id: str, user_id: str = "default_user") -> list:
    """获取与指定角色的所有历史对话摘要列表"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, summary, first_message, updated_at FROM conversations WHERE character_id = ? AND user_id = ? AND summary IS NOT NULL ORDER BY updated_at DESC",
        (character_id, user_id)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def delete_conversation(conversation_id: str):
    """删除指定的对话记录"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
    conn.commit()
    conn.close()
    logger.info(f"删除了对话 {conversation_id}。")

