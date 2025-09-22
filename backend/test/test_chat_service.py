#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2025/9/22 14:29
# @Author : Ray
# @File : test_chat_service.py
# @Software: PyCharm
"""
测试对话接口
"""
import unittest
import json

from dotenv import load_dotenv

load_dotenv()
from backend.services import chat_service
from backend.services import character_manager
from backend.errors.exceptions import FulingException, KimiServiceError


class TestChatService(unittest.TestCase):

    def setUp(self):
        """在每个测试用例运行前执行的设置"""
        self.character_id = "socrates"
        self.system_prompt = character_manager.get_character_prompt(self.character_id)
        self.user_message = "什么是哲学？"
        self.history = []

    def test_chat_service(self):
        result = chat_service.process_chat_interaction(self.character_id, self.user_message, self.history)
        print(result)


if __name__ == '__main__':
    unittest.main()
