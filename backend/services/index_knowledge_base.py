#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2025/9/25 14:54
# @Author : Ray
# @File : index_knowledge_base.py
# @Software: PyCharm
"""
知识库索引
"""
import os
import chromadb
from sentence_transformers import SentenceTransformer
from backend.utils.logger import logger

# --- 配置 ---
KNOWLEDGE_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'knowledge_base'))
CHROMA_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'chroma_db'))
EMBEDDING_MODEL_NAME = 'paraphrase-multilingual-MiniLM-L12-v2'  # 一个高效的多语言模型
COLLECTION_NAME = "fuling_rag"


def main():
    """
    读取知识库文件，生成向量，并存入ChromaDB。
    这个脚本只需要在知识库更新后运行一次。
    """
    logger.info("--- 开始索引知识库 ---")

    # 1. 加载嵌入模型
    logger.info(f"正在加载嵌入模型: {EMBEDDING_MODEL_NAME}...")
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    logger.info("模型加载完毕。")

    # 2. 初始化ChromaDB客户端
    # PersistentClient 会将数据库文件保存在指定路径
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

    # 3. 获取或创建集合 (Collection)
    # 集合类似于数据库中的一张表
    collection = client.get_or_create_collection(name=COLLECTION_NAME)
    logger.info(f"已连接到ChromaDB集合: '{COLLECTION_NAME}'")

    # 4. 遍历知识库文件
    for filename in os.listdir(KNOWLEDGE_BASE_DIR):
        if filename.endswith(".txt"):
            character_id = filename.split('.')[0]
            filepath = os.path.join(KNOWLEDGE_BASE_DIR, filename)

            logger.info(f"正在处理文件: {filename}，角色ID: {character_id}")

            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # 将知识库按 '---' 分隔符拆分成段落 (chunks)
            chunks = [chunk.strip() for chunk in content.split('---') if chunk.strip()]
            if not chunks:
                logger.warning(f"文件 {filename} 为空或格式不正确，已跳过。")
                continue

            # 5. 生成向量并准备数据
            logger.info(f"正在为 {len(chunks)} 个段落生成向量...")
            embeddings = model.encode(chunks).tolist()

            # 为每个段落创建唯一的ID和元数据
            ids = [f"{character_id}_{i}" for i in range(len(chunks))]
            metadatas = [{"character_id": character_id} for _ in range(len(chunks))]

            # 6. 将数据存入ChromaDB
            collection.add(
                embeddings=embeddings,
                documents=chunks,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"成功为角色 '{character_id}' 添加了 {len(chunks)} 个向量文档。")

    logger.info("--- 知识库索引完成 ---")


if __name__ == "__main__":
    main()
