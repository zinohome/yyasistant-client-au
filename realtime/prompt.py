#!/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@author: ibmzhangjun@139.com
@file: prompt.py
@time: 2025/7/15 上午8:53
@desc: 
"""

import os
from threading import Lock

class PromptSingleton:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._prompt = None
                cls._instance._prompt_path = os.path.join(os.path.dirname(__file__), "prompt.txt")
            return cls._instance

    def get_prompt(self):
        """读取并缓存 prompt.txt 的内容"""
        if self._prompt is None:
            self._prompt = self._load_prompt()
        return self._prompt

    def _load_prompt(self):
        try:
            with open(self._prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return ""

    def reload(self):
        """重新加载 prompt.txt 内容到缓存"""
        self._prompt = self._load_prompt()

# 使用方式举例
# from prompt import PromptSingleton
# prompt_content = PromptSingleton().get_prompt()
