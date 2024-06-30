import os
import requests
import time
import hmac
import hashlib
import base64
from bs4 import BeautifulSoup
def send_dingtalk_message(content):
    """
    发送消息到钉钉机器人
    """
    access_token = os.getenv("DINGTALK_ACCESS_TOKEN")
    if not access_token:
        print("未设置钉钉机器人的 access_token 环境变量")
        return
    
    secret = os.getenv("DINGTALK_SECRET")
    if not secret:
        print("未设置钉钉机器人的加签密钥环境变量")
        return
    
    # 获取当前时间戳，单位毫秒
    timestamp = int(round(time.time() * 1000))
    
    # 构造加签字符串
    string_to_sign = f"{timestamp}\n{secret}"
    
    # 计算加签值
    sign = hmac.new(secret.encode("utf-8"), string_to_sign.encode("utf-8"), hashlib.sha256).digest()
    sign = base64.b64encode(sign).decode("utf-8")
    
    # 构造请求头部
    headers = {
        "Content-Type": "application/json",
        "Charset": "UTF-8"
    }
    
    # 构造请求体
    message = {
        "msgtype": "text",
        "text": {
            "content": content
        },
        "timestamp": timestamp,
        "sign": sign
    }
    
    # 发送请求到钉钉机器人
    dingtalk_url = f"https://oapi.dingtalk.com/robot/send?access_token={access_token}&timestamp={timestamp}&sign={sign}"
    response = requests.post(dingtalk_url, json=message, headers=headers)
    
    if response.status_code == 200:
        print("钉钉消息发送成功")
    else:
        print(f"钉钉消息发送失败，状态码：{response.status_code}")
def check_blog_titles():
    """
    检查每个朋友的博客标题是否包含朋友的名字
    """
    results = []  # 创建一个空列表来存储检查结果
    
    # 发送请求获取朋友列表
    response = requests.get("https://blog-api.xiao-feishu.top/friends/friends.json")

    if response.status_code == 200:
        data = response.json()
        
        # 遍历每个朋友的信息
        for friend in data["friends"]:
            name, blog_url, favicon_url, rss_feed = friend
            
            # 请求每个博客的首页
            blog_response = requests.get(blog_url + "/index.html")
            
            if blog_response.status_code == 200:
                # 解析HTML
                soup = BeautifulSoup(blog_response.content, "html.parser")
                
                # 获取<title>标签内容
                title = soup.title.string.strip() if soup.title else '未找到标题'
                
                # 检查<title>是否包含Name
                if name in title:
                    results.append(f"包含: {blog_url} 的标题包含名字 '{name}'")
                else:
                    results.append(f"不包含: {blog_url} 的标题是 '{title}'，但不包含 '{name}'")
                    
                    # 不立即发送钉钉消息，将结果存入列表中
                    
            else:
                results.append(f"获取 {blog_url}/index.html 失败，状态码：{blog_response.status_code}")
                
                # 不立即发送钉钉消息，将结果存入列表中
    
    else:
        results.append("请求失败，状态码：" + str(response.status_code))
    
    # 检查是否所有博客标题都正常，如果是则发送一条全部正常的钉钉消息
    all_clear = all("包含" in result for result in results)
    
    if all_clear:
        send_dingtalk_message("所有博客标题检查正常")
    else:
        # 在所有博客检查完毕后，汇总结果并发送一条钉钉消息
        send_dingtalk_message("\n".join(results))

# 调用函数检查博客标题
check_blog_titles()
