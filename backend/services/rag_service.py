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
from modelscope import snapshot_download
from backend.utils.logger import logger
from backend.errors.exceptions import FulingException

# --- 在模块加载时，一次性初始化所有组件 ---
logger.info("正在初始化RAG服务...")

# 配置路径
CHROMA_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'chroma_db'))
MODEL_ID = "AI-ModelScope/m3e-small"  # 国内模型ID
COLLECTION_NAME = "fuling_rag"
MODEL_CACHE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'model_cache'))  # 模型缓存目录

# 加载嵌入模型
try:
    # 确保缓存目录存在
    os.makedirs(MODEL_CACHE_DIR, exist_ok=True)

    # 从ModelScope下载模型到本地
    logger.info(f"正在从ModelScope下载模型: {MODEL_ID}...")
    local_model_dir = snapshot_download(
        model_id=MODEL_ID,
        cache_dir=MODEL_CACHE_DIR,
        revision='master'
    )

    # 加载本地模型
    EMBEDDING_MODEL = SentenceTransformer(
        model_name_or_path=local_model_dir,
        trust_remote_code=True,
        cache_folder=MODEL_CACHE_DIR
    )
    logger.info("RAG服务的嵌入模型加载成功。")
except Exception as e:
    logger.critical(f"无法加载嵌入模型 '{MODEL_ID}': {e}")
    EMBEDDING_MODEL = None

# 连接到ChromaDB
try:
    CHROMA_CLIENT = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    CHROMA_COLLECTION = CHROMA_CLIENT.get_collection(name=COLLECTION_NAME)
    logger.info("RAG服务成功连接到ChromaDB。")
except Exception as e:
    logger.critical(f"无法连接到ChromaDB集合 '{COLLECTION_NAME}': {e}")
    CHROMA_COLLECTION = None


def is_knowledge_query(text: str) -> bool:
    """通过关键词判断用户输入是否为知识型问题"""
    # 处理文本：去除首尾空格，中文不需要转小写
    text_processed = text.strip().lower()

    # 扩充中文疑问词，覆盖更多表达；区分中英文关键词
    chinese_question_words = {
        "谁", "什么", "哪里", "何时", "怎样", "为什么",
        "何谓", "请问", "解释", "含义", "介绍", "告诉我",
        "是什么", "怎么样", "有什么", "为什么会"
    }
    english_question_words = {
        "who", "what", "where", "when", "how", "why",
        "tell me", "describe"
    }

    # 检查中文关键词：只要文本中包含中文疑问词，即视为知识型问题
    for word in chinese_question_words:
        if word in text_processed:
            return True

    # 检查英文关键词
    for word in english_question_words:
        if text_processed.startswith(word):
            return True

    return False

def retrieve_context(character_id: str, query: str) -> str | None:
    """
    从ChromaDB中通过向量相似度检索上下文，仅返回第一个相关性高于阈值的结果。
    """
    # 相关性阈值
    RELEVANCE_THRESHOLD = 150

    if not EMBEDDING_MODEL or not CHROMA_COLLECTION:
        logger.error("RAG服务未正确初始化，无法执行检索。")
        return None

    try:
        # 1. 将用户问题转换为查询向量
        query_embedding = EMBEDDING_MODEL.encode(query).tolist()

        # 2. 在ChromaDB中查询
        results = CHROMA_COLLECTION.query(
            query_embeddings=[query_embedding],
            n_results=1,  # 只检索最相关的1个结果
            where={"character_id": character_id},  # 过滤当前角色的知识
            include=["documents", "distances"]  # 明确要求返回距离分数
        )

        # 3. 提取结果和相关性分数
        retrieved_docs = results.get('documents', [[]])[0]
        distances = results.get('distances', [[]])[0]

        if not retrieved_docs or not distances:
            logger.warning(f"未找到与问题 '{query}' 相关的知识（角色: {character_id}）。")
            return None

        # 4. 检查第一个结果是否满足相关性阈值
        first_doc = retrieved_docs[0]
        first_distance = distances[0]

        if first_distance <= RELEVANCE_THRESHOLD:
            logger.info(
                f"找到符合阈值的相关知识（距离: {first_distance:.4f}），角色: {character_id}"
            )
            return first_doc
        else:
            logger.warning(
                f"最相关结果距离 {first_distance:.4f} 超过阈值 {RELEVANCE_THRESHOLD}，"
                f"角色: {character_id}，问题: {query}"
            )
            return None

    except Exception as e:
        logger.error(f"在向量数据库中检索时发生错误: {e}")
        raise FulingException("检索知识时发生内部错误。")
