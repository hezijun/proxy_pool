# debug_fetcher.py
import requests

# 我们将直接使用requests库，绕开项目中可能复杂的WebRequest封装
# 以确保我们能看到最原始的响应

url = "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

print("--- 开始调试 freeProxy_proxyscrape ---")
print(f"正在请求URL: {url}")

try:
    response = requests.get(url, headers=headers, timeout=20)

    print(f"\n请求完成，HTTP状态码: {response.status_code}")

    # --- 核心调试步骤：打印原始返回内容 ---
    print("\n" + "=" * 20 + " 原始返回内容 (response.text) " + "=" * 20)
    print(response.text)
    print("=" * 60)
    # ---

    # 尝试按行分割并打印前5个结果
    if response.status_code == 200 and response.text:
        proxies = response.text.strip().split('\r\n')
        print(f"\n成功按'\\r\\n'分割，共找到 {len(proxies)} 个代理。")
        print("\n打印前5个代理IP:")
        for i, proxy in enumerate(proxies[:5]):
            print(f"  {i + 1}: {proxy}")
    else:
        print("\n未能获取到有效的代理列表。")

except Exception as e:
    print(f"\n❌ 请求过程中发生严重错误: {e}")

print("\n--- 调试结束 ---")