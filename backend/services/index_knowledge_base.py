#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2025/9/25 14:54
# @Author : Ray
# @File : index_knowledge_base.py
# @Software: PyCharm
"""
知识库索引
- 替换为国内可访问的m3e-small模型（ModelScope）
"""
import os
import chromadb
from sentence_transformers import SentenceTransformer
from modelscope import snapshot_download
from backend.utils.logger import logger

# --- 配置 ---
KNOWLEDGE_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'knowledge_base'))
CHROMA_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'chroma_db'))
MODEL_ID = "AI-ModelScope/m3e-small"  # ModelScope模型ID
COLLECTION_NAME = "fuling_rag"
MODEL_CACHE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'model_cache'))  # 模型本地保存目录


def main():
    """
    读取知识库文件，使用国内模型生成向量，存入ChromaDB
    知识库更新后运行一次即可
    """
    logger.info("--- 开始索引知识库 ---")

    try:
        # 1. 创建模型缓存目录
        os.makedirs(MODEL_CACHE_DIR, exist_ok=True)

        # 2. 先从ModelScope下载模型到本地
        logger.info(f"正在从ModelScope下载模型: {MODEL_ID}...")
        # 下载模型到MODEL_CACHE_DIR，返回本地实际保存路径
        local_model_dir = snapshot_download(
            model_id=MODEL_ID,
            cache_dir=MODEL_CACHE_DIR,  # 保存到指定目录
            revision='master',  # 模型版本
            ignore_file_pattern=["*.bin.index.json"]
        )
        logger.info(f"模型下载完成，本地路径: {local_model_dir}")

        # 3. 加载本地模型
        logger.info("正在初始化本地嵌入模型...")
        model = SentenceTransformer(
            model_name_or_path=local_model_dir,  # 传入本地模型路径
            trust_remote_code=True,  # 国内模型需要此参数
            cache_folder=MODEL_CACHE_DIR  # 缓存目录保持一致
        )
        logger.info("模型加载完毕。")

        # 4. 初始化ChromaDB客户端
        client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        collection = client.get_or_create_collection(name=COLLECTION_NAME)
        logger.info(f"已连接到ChromaDB集合: '{COLLECTION_NAME}'")

        # 5. 遍历处理知识库文件
        for filename in os.listdir(KNOWLEDGE_BASE_DIR):
            if filename.endswith(".txt"):
                character_id = filename.split('.')[0]
                filepath = os.path.join(KNOWLEDGE_BASE_DIR, filename)

                logger.info(f"正在处理文件: {filename}，角色ID: {character_id}")

                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()

                    chunks = [chunk.strip() for chunk in content.split('---') if chunk.strip()]
                    if not chunks:
                        logger.warning(f"文件 {filename} 为空或格式不正确，已跳过。")
                        continue

                    logger.info(f"正在为 {len(chunks)} 个段落生成向量...")
                    embeddings = model.encode(chunks).tolist()

                    ids = [f"{character_id}_{i}" for i in range(len(chunks))]
                    metadatas = [{"character_id": character_id, "filename": filename} for _ in range(len(chunks))]

                    collection.add(
                        embeddings=embeddings,
                        documents=chunks,
                        metadatas=metadatas,
                        ids=ids
                    )
                    logger.info(f"成功为角色 '{character_id}' 添加了 {len(chunks)} 个向量文档。")

                except Exception as e:
                    logger.error(f"处理文件 {filename} 时出错: {str(e)}", exc_info=True)

        logger.info("--- 知识库索引完成 ---")

    except Exception as e:
        logger.critical(f"索引过程发生致命错误: {str(e)}", exc_info=True)


if __name__ == "__main__":
    main()
