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
    """项目自定义异常的基类"""

    def __init__(self, message=None, status_code=None):
        super().__init__(message)
        if message is not None:
            self.message = message
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self):
        return {"error": {"type": self.__class__.__name__, "message": self.message}}


class CharacterNotFound(FulingException):
    """当找不到指定的角色配置文件时引发"""

    def __init__(self, message="指定的角色不存在。"):
        super().__init__(message, status_code=404)


class InvalidAPIRequest(FulingException):
    """当API请求无效或缺少参数时引发"""

    def __init__(self, message="请求无效或缺少必要参数。"):
        super().__init__(message, status_code=400)


class KimiServiceError(FulingException):
    """当调用Kimi API失败时引发"""

    def __init__(self, message="与AI服务的通信时发生错误。"):
        super().__init__(message, status_code=503)  # 503 Service Unavailable


class ApiResponseParseError(FulingException):
    """当解析Kimi返回的JSON失败时引发"""

    def __init__(self, message="解析AI服务响应时发生错误。"):
        super().__init__(message, status_code=500)


class TTSServiceError(FulingException):
    """当调用TTS服务失败时引发"""

    def __init__(self, message="与语音合成服务通信时发生错误。"):
        super().__init__(message, status_code=502)


class MissingParameterError(FulingException):
    """当API请求缺少必要参数时引发"""

    def __init__(self, message="请求缺少必要的参数。"):
        super().__init__(message, status_code=400)
