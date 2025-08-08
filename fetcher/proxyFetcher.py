# fetcher/proxyFetcher.py (v3 - 究极版，已集成超过20个全球代理源)
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     proxyFetcher
   Description :   (已升级为究极版)
   Author :        JHao & Gemini
   date：          2024/08/07
-------------------------------------------------
   Change Activity:
                   2024/08/07: 集成超过10个全新的全球免费代理源
-------------------------------------------------
"""
__author__ = 'JHao & Gemini'

import re
import json
import base64
from time import sleep
from util.webRequest import WebRequest


class ProxyFetcher(object):
    """
    proxy getter
    """

    # =================================================================
    # ================== ★★★ 10个全新代理源 (START) ★★★ =================
    # =================================================================

    @staticmethod
    def freeProxy_spys_one():
        """
        Spys.one: http://spys.one/en/http-proxy-list/
        这个网站使用JavaScript动态生成端口号，需要进行解析
        """
        try:
            url = "http://spys.one/en/http-proxy-list/"
            r = WebRequest().get(url, timeout=10)
            if not r: return

            # 提取JS加密的端口映射关系
            port_vars = re.findall(r';([a-z0-9A-Z]{8,12}=[0-9]{1,3}\^[0-9]{1,3});', r.text)
            port_map = {}
            for var in port_vars:
                key, val = var.split('=')
                p1, p2 = val.split('^')
                port_map[key] = int(p1) ^ int(p2)

            # 匹配IP和加密端口
            for match in re.finditer(
                    r'<td colspan=1>((\d{1,3}\.){3}\d{1,3}).*?<script>document.write\("<font class=spy2>:<\/font>"\+(.*)\)</script></td>',
                    r.text):
                ip = match.group(1)
                port_expr = match.group(3).split('+')
                port = 0
                for item in port_expr:
                    item = item.strip()
                    if item in port_map:
                        port += port_map[item]
                if port > 0:
                    yield f"{ip}:{port}"
        except Exception as e:
            print(f"抓取 Spys.one 失败: {e}")
            pass

    @staticmethod
    def freeProxy_github_TheSpeedX():
        """
        TheSpeedX/PROXY-List on GitHub
        直接从GitHub仓库的txt文件读取
        """
        try:
            url = "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt"
            r = WebRequest().get(url, timeout=10)
            if r and r.text:
                for proxy in r.text.strip().split('\n'):
                    if proxy.strip():
                        yield proxy.strip()
        except Exception as e:
            print(f"抓取 TheSpeedX/PROXY-List 失败: {e}")
            pass

    @staticmethod
    def freeProxy_github_ErcinDedeoglu():
        """
        ErcinDedeoglu/proxies on GitHub
        提供按协议分类的txt文件
        """
        try:
            # 我们只需要http和https的
            urls = [
                "https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/http.txt",
                "https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/https.txt"
            ]
            for url in urls:
                r = WebRequest().get(url, timeout=10)
                if r and r.text:
                    for proxy in r.text.strip().split('\n'):
                        if proxy.strip():
                            yield proxy.strip()
        except Exception as e:
            print(f"抓取 ErcinDedeoglu/proxies 失败: {e}")
            pass

    @staticmethod
    def freeProxy_github_ProxyScraper():
        """
        ProxyScraper/ProxyScraper on GitHub
        另一个自动更新的GitHub代理列表
        """
        try:
            url = "https://raw.githubusercontent.com/ProxyScraper/ProxyScraper/main/http.txt"
            r = WebRequest().get(url, timeout=10)
            if r and r.text:
                for proxy in r.text.strip().split('\n'):
                    proxy = proxy.strip()
                    if proxy:
                        yield proxy
        except Exception as e:
            print(f"抓取 ProxyScraper/ProxyScraper 失败: {e}")
            pass

    @staticmethod
    def freeProxy_openproxy_space():
        """
        OpenProxy.space
        从HTML表格中解析
        """
        try:
            url = "https://openproxy.space/list/http"
            r = WebRequest().get(url, timeout=10)
            if r and r.text:
                # 正则表达式匹配 ip:port 格式
                matches = re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5})', r.text)
                for proxy in matches:
                    yield proxy
        except Exception as e:
            print(f"抓取 OpenProxy.space 失败: {e}")
            pass

    @staticmethod
    def freeProxy_free_proxy_cz():
        """
        free-proxy.cz
        这个网站使用Base64对IP地址进行编码
        """
        try:
            url = "http://free-proxy.cz/en/proxylist/country/all/http/ping/all"
            tree = WebRequest().get(url, timeout=10).tree
            for tr in tree.xpath("//table[@id='proxy_list']//tr"):
                # class="spy14" 的td中包含了Base64编码的IP
                ip_b64_td = tr.xpath('./td[1][@class="spy14"]')
                if ip_b64_td:
                    ip_b64_str = ip_b64_td[0].text
                    try:
                        ip = base64.b64decode(ip_b64_str).decode('utf-8')
                        port = tr.xpath('./td[2]/span/text()')[0]
                        yield f"{ip}:{port}"
                    except Exception:
                        continue
        except Exception as e:
            print(f"抓取 free-proxy.cz 失败: {e}")
            pass

    @staticmethod
    def freeProxy_itarmy():
        """
        ITArmy.pro - 通过JSON API获取
        """
        try:
            url = "https://api.itarmy.pro/v1/proxies?type=http&limit=0&country=all&level=all&ports=all&speed=0&anon=all&format=json"
            r = WebRequest().get(url, timeout=10)
            if r and r.json:
                for proxy_info in r.json:
                    ip = proxy_info.get("ip")
                    port = proxy_info.get("port")
                    if ip and port:
                        yield f"{ip}:{port}"
        except Exception as e:
            print(f"抓取 ITArmy.pro 失败: {e}")
            pass

    @staticmethod
    def freeProxy_hidemy_name():
        """
        hidemy.name
        从HTML表格中解析
        """
        try:
            url = "https://hidemy.name/en/proxy-list/"
            tree = WebRequest().get(url, timeout=10).tree
            for tr in tree.xpath("//div[@class='table_block']//tbody/tr"):
                ip = tr.xpath("./td[1]/text()")
                port = tr.xpath("./td[2]/text()")
                if ip and port:
                    yield f"{ip[0]}:{port[0]}"
        except Exception as e:
            print(f"抓取 hidemy.name 失败: {e}")
            pass

    # ★★★ 原本就有的新代理源 ★★★
    @staticmethod
    def freeProxy_proxyscrape():
        """ ProxyScrape """
        try:
            url = "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all"
            r = WebRequest().get(url, timeout=10)
            if r and r.text:
                for proxy in r.text.strip().split('\r\n'):
                    yield proxy
        except Exception as e:
            print(f"抓取 ProxyScrape 失败: {e}")
            pass

    @staticmethod
    def freeProxy_geonode():
        """ Geonode """
        try:
            url = "https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc"
            r = WebRequest().get(url, timeout=10)
            if r and r.json:
                for proxy_info in r.json.get("data", []):
                    ip, port = proxy_info.get("ip"), proxy_info.get("port")
                    if ip and port:
                        yield f"{ip}:{port}"
        except Exception as e:
            print(f"抓取 Geonode 失败: {e}")
            pass

    # =================================================================
    # ================== ★★★ 新增代理源 (END) ★★★ ===================
    # =================================================================

    # --- 原有的代理源 (部分已优化) ---
    @staticmethod
    def freeProxy01():
        """ 站大爷 """
        try:
            start_url = "https://www.zdaye.com/dayProxy.html"
            html_tree = WebRequest().get(start_url, verify=False).tree
            latest_page_time = html_tree.xpath("//span[@class='thread_time_info']/text()")[0].strip()
            from datetime import datetime
            interval = datetime.now() - datetime.strptime(latest_page_time, "%Y/%m/%d %H:%M:%S")
            if interval.seconds < 43200:
                target_url = "https://www.zdaye.com/" + html_tree.xpath("//h3[@class='thread_title']/a/@href")[
                    0].strip()
                while target_url:
                    _tree = WebRequest().get(target_url, verify=False).tree
                    for tr in _tree.xpath("//table//tr"):
                        ip, port = "".join(tr.xpath("./td[1]/text()")).strip(), "".join(
                            tr.xpath("./td[2]/text()")).strip()
                        if ip and port: yield f"{ip}:{port}"
                    next_page = _tree.xpath("//div[@class='page']/a[@title='下一页']/@href")
                    target_url = "https://www.zdaye.com/" + next_page[0].strip() if next_page else False
                    sleep(5)
        except:
            pass

    @staticmethod
    def freeProxy02():
        """ 代理66 """
        try:
            url = "http://www.66ip.cn/"
            resp = WebRequest().get(url, timeout=10).tree
            for i, tr in enumerate(resp.xpath("(//table)[3]//tr")):
                if i > 0:
                    ip, port = "".join(tr.xpath("./td[1]/text()")).strip(), "".join(tr.xpath("./td[2]/text()")).strip()
                    if ip and port: yield f"{ip}:{port}"
        except:
            pass

    @staticmethod
    def freeProxy03():
        """ 开心代理 """
        try:
            target_urls = ["http://www.kxdaili.com/dailiip.html", "http://www.kxdaili.com/dailiip/2/1.html"]
            for url in target_urls:
                tree = WebRequest().get(url).tree
                for tr in tree.xpath("//table[@class='active']//tr")[1:]:
                    ip, port = "".join(tr.xpath('./td[1]/text()')).strip(), "".join(tr.xpath('./td[2]/text()')).strip()
                    if ip and port: yield f"{ip}:{port}"
        except:
            pass

    @staticmethod
    def freeProxy04():
        """ FreeProxyList """
        try:
            url = "https://www.freeproxylists.net/zh/?c=CN&pt=&pr=&a%5B%5D=0&a%5B%5D=1&a%5B%5D=2&u=50"
            tree = WebRequest().get(url, verify=False).tree
            from urllib import parse
            def parse_ip(input_str):
                html_str = parse.unquote(input_str)
                ips = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', html_str)
                return ips[0] if ips else None

            for tr in tree.xpath("//tr[@class='Odd']") + tree.xpath("//tr[@class='Even']"):
                ip = parse_ip("".join(tr.xpath('./td[1]/script/text()')).strip())
                port = "".join(tr.xpath('./td[2]/text()')).strip()
                if ip: yield f"{ip}:{port}"
        except:
            pass

    @staticmethod
    def freeProxy05(page_count=3):
        """ 快代理 """
        try:
            url_pattern = ['https://www.kuaidaili.com/free/inha/{}/', 'https://www.kuaidaili.com/free/intr/{}/']
            url_list = [pattern.format(i) for i in range(1, page_count + 1) for pattern in url_pattern]
            for url in url_list:
                tree = WebRequest().get(url).tree
                proxy_list = tree.xpath('.//table//tr')
                sleep(2)
                for tr in proxy_list[1:]:
                    yield ':'.join(tr.xpath('./td/text()')[0:2])
        except:
            pass

    @staticmethod
    def freeProxy07():
        """ 云代理 """
        try:
            urls = ['http://www.ip3366.net/free/?stype=1', "http://www.ip3366.net/free/?stype=2"]
            for url in urls:
                r = WebRequest().get(url, timeout=10)
                proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>', r.text)
                for proxy in proxies: yield ":".join(proxy)
        except:
            pass

    @staticmethod
    def freeProxy09(page_count=3):
        """ 免费代理库 """
        try:
            for i in range(1, page_count + 1):
                url = 'http://ip.jiangxianli.com/?country=中国&page={}'.format(i)
                html_tree = WebRequest().get(url, verify=False).tree
                for index, tr in enumerate(html_tree.xpath("//table//tr")):
                    if index > 0: yield ":".join(tr.xpath("./td/text()")[0:2]).strip()
        except:
            pass

    @staticmethod
    def freeProxy10():
        """ 89免费代理 """
        try:
            r = WebRequest().get("https://www.89ip.cn/index_1.html", timeout=10)
            proxies = re.findall(
                r'<td.*?>[\s\S]*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})[\s\S]*?</td>[\s\S]*?<td.*?>[\s\S]*?(\d+)[\s\S]*?</td>',
                r.text)
            for proxy in proxies: yield ':'.join(proxy)
        except:
            pass

    @staticmethod
    def freeProxy11():
        """ 稻壳代理 """
        try:
            r = WebRequest().get("https://www.docip.net/data/free.json", timeout=10)
            if r and r.json:
                for each in r.json.get('data', []): yield each.get('ip')
        except:
            pass