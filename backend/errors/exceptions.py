#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2025/9/22 10:54
# @Author : Ray
# @File : exceptions.py
# @Software: PyCharm
"""
异常管理
"""
class FulingException(Exception):
    """应用的基础异常类"""
    status_code = 500
    message = "服务器内部发生未知错误。"

    def __init__(self, message=None, status_code=None):
        super().__init__(message)
        if message is not None:
            self.message = message
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self):
        return {"error": self.message}

class CharacterNotFound(FulingException):
    """当找不到角色文件时引发"""
    status_code = 404
    message = "指定的角色不存在。"

class InvalidAPIRequest(FulingException):
    """当API请求无效或缺少参数时引发"""
    status_code = 400
    message = "请求无效或缺少必要参数。"

class KimiServiceError(FulingException):
    """当调用Kimi API失败时引发"""
    status_code = 503
    message = "与AI服务的通信时发生错误。"

class ApiResponseParseError(FulingException):
    """当解析Kimi返回的JSON失败时引发"""
    status_code = 500
    message = "解析AI服务响应时发生错误。"
