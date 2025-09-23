#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2025/9/23 15:20
# @Author : Ray
# @File : test_character_manager.py
# @Software: PyCharm
"""
测试角色列表
"""
import unittest

from backend.services.character_manager import get_all_characters


class TestChatService(unittest.TestCase):

    def testcase1(self):
        characters = get_all_characters()
        print(characters)







if __name__ == '__main__':
    unittest.main()
