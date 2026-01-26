#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FOFA配置示例文件
复制此文件为 fofa_config.py 并填入你的API信息
"""

# FOFA API配置
FOFA_EMAIL = "your_email@example.com"    # 你的FOFA注册邮箱
FOFA_KEY = "your_fofa_api_key"        # 你的FOFA API密钥

# 默认设置
DEFAULT_QUERY = "camera"               # 默认搜索查询
DEFAULT_MAX_RESULTS = 1000           # 默认最大结果数

# 常用查询模板
QUERIES = {
    "海康威视": 'app="Hikvision-Web"',
    "大华": 'app="Dahua-Web"',
    "宇视": 'app="Uniview-Web"',
    " AXIS": 'app="AXIS-Web"',
    "Vivotek": 'app="Vivotek-Web"',
    "Foscam": 'app="Foscam-Web"',
    "RTSP": 'protocol="rtsp"',
    "HTTP摄像头": 'title="摄像头"',
    "中国摄像头": 'app="Hikvision-Web" && country="CN"',
    "80端口摄像头": 'port=80 && title="摄像头"',
    "554端口": 'port=554',
    "8080端口": 'port=8080',
}

if __name__ == "__main__":
    print("请复制此文件为 fofa_config.py 并填入你的FOFA API信息")
    print("获取API密钥请访问: https://fofa.info/")