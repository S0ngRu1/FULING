#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2025/9/22 10:56
# @Author : Ray
# @File : error_handlers.py
# @Software: PyCharm
"""

"""
from functools import wraps
from flask import jsonify
from .exceptions import FulingException
from backend.utils.logger import logger

def api_error_handler(f):
    """
    一个装饰器，用于捕获API路由中的FulingException并返回格式化的JSON错误响应。
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except FulingException as e:
            logger.error(f"API Error - {e.__class__.__name__}: {e.message}", exc_info=True)
            return jsonify(e.to_dict()), e.status_code
        except Exception as e:
            logger.critical(f"Unhandled Exception: {str(e)}", exc_info=True)
            error_response = {
                "error": "服务器发生了一个意外的错误。"
            }
            return jsonify(error_response), 500
    return decorated_function

def register_error_handlers(app):
    """
    一个函数，用于在Flask app上注册通用的错误处理器。
    """
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({"error": "请求的资源未找到。"}), 404

    @app.errorhandler(405)
    def method_not_allowed_error(error):
        return jsonify({"error": "该请求方法不允许。"}), 405
