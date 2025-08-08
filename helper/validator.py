# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     validator.py
   Description :   定义proxy验证方法 (已修改为豆瓣专用)
   Author :        JHao
   date：          2021/5/25
-------------------------------------------------
   Change Activity:
                   2023/03/10: 支持带用户认证的代理格式 username:password@ip:port
                   2024/08/07: 修改为豆瓣专用校验, 使用GET请求并检查内容
-------------------------------------------------
"""
__author__ = 'JHao'

import re
# 导入完整的requests库以使用GET方法
import requests
from util.six import withMetaclass
from util.singleton import Singleton
from handler.configHandler import ConfigHandler

conf = ConfigHandler()

# 使用更健壮的请求头来模拟真实浏览器
HEADER = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Connection': 'keep-alive'
}

IP_REGEX = re.compile(r"(.*:.*@)?\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}")


class ProxyValidator(withMetaclass(Singleton)):
    pre_validator = []
    http_validator = []
    https_validator = []

    @classmethod
    def addPreValidator(cls, func):
        cls.pre_validator.append(func)
        return func

    @classmethod
    def addHttpValidator(cls, func):
        cls.http_validator.append(func)
        return func

    @classmethod
    def addHttpsValidator(cls, func):
        cls.https_validator.append(func)
        return func


@ProxyValidator.addPreValidator
def formatValidator(proxy):
    """检查代理格式"""
    return True if IP_REGEX.fullmatch(proxy) else False


@ProxyValidator.addHttpValidator
def httpTimeOutValidator(proxy):
    """
    http检测超时
    对于我们的需求，可以保持这个函数不变，或者也改成GET请求。
    保持用HEAD可以稍微加快一点对非HTTPS代理的过滤速度。
    """
    proxies = {"http": "http://{proxy}".format(proxy=proxy), "https": "https://{proxy}".format(proxy=proxy)}

    try:
        r = requests.head(conf.httpUrl, headers=HEADER, proxies=proxies, timeout=conf.verifyTimeout)
        return True if r.status_code == 200 else False
    except Exception as e:
        return False


@ProxyValidator.addHttpsValidator
def httpsTimeOutValidator(proxy):
    """
    更健壮的HTTPS检测，专门针对豆瓣优化。
    1. 使用 GET 请求，更真实地模拟用户访问。
    2. 检查返回内容，确保是真实的豆瓣页面，而不是代理商的错误页。
    3. 支持重定向。
    """
    proxies = {"http": "http://{proxy}".format(proxy=proxy), "https": "https://{proxy}".format(proxy=proxy)}
    try:
        # 使用 requests.get 替代 head
        r = requests.get(conf.httpsUrl, headers=HEADER, proxies=proxies, timeout=conf.verifyTimeout, verify=False,
                         allow_redirects=True)

        # 检查状态码为 200，并且检查返回的文本中是否包含“豆瓣”二字
        # 这样可以有效过滤掉无效或返回错误页面的代理
        if r.status_code == 200 and "豆瓣" in r.text:
            return True
        else:
            return False
    except Exception as e:
        return False


@ProxyValidator.addHttpValidator
def customValidatorExample(proxy):
    """自定义validator函数，校验代理是否可用, 返回True/False"""
    return True