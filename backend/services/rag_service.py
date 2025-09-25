#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2025/9/25 13:07
# @Author : Ray
# @File : rag_service.py
# @Software: PyCharm
"""
RAG服务
"""
import os
import chromadb
from sentence_transformers import SentenceTransformer
from backend.utils.logger import logger
from backend.errors.exceptions import FulingException

# --- 在模块加载时，一次性初始化所有组件 ---
logger.info("正在初始化RAG服务...")

# 配置路径
CHROMA_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'chroma_db'))
EMBEDDING_MODEL_NAME = 'paraphrase-multilingual-MiniLM-L12-v2'
COLLECTION_NAME = "fuling_rag"

# 加载嵌入模型
try:
    EMBEDDING_MODEL = SentenceTransformer(EMBEDDING_MODEL_NAME)
    logger.info("RAG服务的嵌入模型加载成功。")
except Exception as e:
    logger.critical(f"无法加载嵌入模型 '{EMBEDDING_MODEL_NAME}': {e}")
    EMBEDDING_MODEL = None

# 连接到ChromaDB
try:
    CHROMA_CLIENT = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    CHROMA_COLLECTION = CHROMA_CLIENT.get_collection(name=COLLECTION_NAME)
    logger.info("RAG服务成功连接到ChromaDB。")
except Exception as e:
    logger.critical(f"无法连接到ChromaDB集合 '{COLLECTION_NAME}': {e}")
    CHROMA_COLLECTION = None

# 用于判断知识型问题的关键词
QUESTION_WORDS = (
    "who", "what", "where", "when", "how", "why", "tell me", "describe",
    "谁", "什么", "哪里", "何时", "怎样", "为什么", "告诉我", "介绍一下", "关于"
)


def is_knowledge_query(text: str) -> bool:
    """通过关键词判断用户输入是否为一个知识型问题。"""
    text_lower = text.lower().strip()
    for word in QUESTION_WORDS:
        if text_lower.startswith(word):
            return True
    return False


def retrieve_context(character_id: str, query: str) -> str | None:
    """
       从ChromaDB中通过向量相似度检索上下文。
    """
    if not EMBEDDING_MODEL or not CHROMA_COLLECTION:
        logger.error("RAG服务未正确初始化，无法执行检索。")
        return None

    try:
        # 1. 将用户问题转换为查询向量
        query_embedding = EMBEDDING_MODEL.encode(query).tolist()

        # 2. 在ChromaDB中进行查询
        results = CHROMA_COLLECTION.query(
            query_embeddings=[query_embedding],
            n_results=2,  # 返回最相关的2个结果
            # 使用where过滤器，确保只在当前角色的知识中搜索
            where={"character_id": character_id}
        )

        # 3. 提取并组合检索到的文档内容
        retrieved_docs = results.get('documents', [[]])[0]
        if not retrieved_docs:
            logger.warning(f"未能为问题 '{query}' 在角色 '{character_id}' 的知识库中找到相关上下文。")
            return None

        context = "\n\n---\n\n".join(retrieved_docs)
        logger.info(f"为问题 '{query}' 成功检索到上下文。")
        return context

    except Exception as e:
        logger.error(f"在向量数据库中检索时发生错误: {e}")
        raise FulingException("检索知识时发生内部错误。")
