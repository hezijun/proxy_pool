# helper/scheduler.py (已实现智能检查逻辑)

# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     proxyScheduler
   Description :
   Author :        JHao
   date：          2019/8/5
-------------------------------------------------
   Change Activity:
                   2019/08/05: proxyScheduler
                   2021/02/23: runProxyCheck时,剩余代理少于POOL_SIZE_MIN时执行抓取
                   2024/08/07: 实现代理检查冷却时间逻辑
-------------------------------------------------
"""
__author__ = 'JHao'

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ProcessPoolExecutor
from datetime import datetime, timedelta  # 导入时间模块

from util.six import Queue
from helper.fetch import Fetcher
from helper.check import Checker
from handler.logHandler import LogHandler
from handler.proxyHandler import ProxyHandler
from handler.configHandler import ConfigHandler


def __runProxyFetch():
    proxy_queue = Queue()
    proxy_fetcher = Fetcher()

    for proxy in proxy_fetcher.run():
        proxy_queue.put(proxy)

    Checker("raw", proxy_queue)


# ==================== ★★★ 核心修改逻辑 ★★★ ====================
def __runProxyCheck():
    """
    智能检查代理池中的代理。
    - 只检查超过冷却时间的代理。
    - 池中代理过少时，自动触发抓取新代理。
    """
    proxy_handler = ProxyHandler()
    log = LogHandler("scheduler")

    # 如果代理池数量低于阈值，立即触发一次抓取
    if proxy_handler.getCount().get('total', 0) < proxy_handler.conf.poolSizeMin:
        log.info("ProxyPool size is too low, trigger fetch task.")
        __runProxyFetch()
        return  # 本次检查结束，等待下一次调度

    # 从配置中获取冷却时间
    cool_down_seconds = proxy_handler.conf.checkCoolDown

    proxies_to_check = []
    all_proxies = proxy_handler.getAll()

    for proxy in all_proxies:
        # proxy.last_time 是一个字符串，格式如: "2024-08-07 12:00:00"
        # 如果代理没有上次检查时间（例如手动添加的），则立即检查
        if not proxy.last_time:
            proxies_to_check.append(proxy)
            continue

        # 计算时间差
        last_check_time = datetime.strptime(proxy.last_time, "%Y-%m-%d %H:%M:%S")
        if datetime.now() - last_check_time > timedelta(seconds=cool_down_seconds):
            proxies_to_check.append(proxy)

    log.info(f"Routine check: {len(all_proxies)} proxies in total, "
             f"{len(proxies_to_check)} proxies need to be checked (cool down: {cool_down_seconds}s).")

    # 如果没有需要检查的代理，则直接结束
    if not proxies_to_check:
        return

    # 将需要检查的代理放入队列
    proxy_queue = Queue()
    for proxy in proxies_to_check:
        proxy_queue.put(proxy)

    Checker("use", proxy_queue)


# ==============================================================


def runScheduler():
    # 首次启动时，为了快速填满代理池，可以运行一次全量抓取和检查
    __runProxyFetch()

    timezone = ConfigHandler().timezone
    scheduler_log = LogHandler("scheduler")
    scheduler = BlockingScheduler(logger=scheduler_log, timezone=timezone)

    # 抓取新代理的任务频率可以保持不变
    scheduler.add_job(__runProxyFetch, 'interval', minutes=4, id="proxy_fetch", name="proxy采集")
    # 检查任务的频率也可以保持不变（例如2分钟），因为它现在是一个轻量级的扫描操作
    scheduler.add_job(__runProxyCheck, 'interval', minutes=2, id="proxy_check", name="proxy检查")

    executors = {
        'default': {'type': 'threadpool', 'max_workers': 50},
        'processpool': ProcessPoolExecutor(max_workers=5)
    }
    job_defaults = {
        'coalesce': False,
        'max_instances': 10
    }

    scheduler.configure(executors=executors, job_defaults=job_defaults, timezone=timezone)

    scheduler.start()


if __name__ == '__main__':
    runScheduler()