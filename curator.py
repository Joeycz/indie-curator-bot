import os
import json
import time
import feedparser
from datetime import datetime, timedelta
from dateutil import parser
from openai import OpenAI
from notion_client import Client
from dotenv import load_dotenv
import httpx
try:
    from volcenginesdkarkruntime import Ark
except ImportError:
    Ark = None

# 加载 .env 文件
load_dotenv()

# --- 配置区域 ---

# 运行频率配置
TWITTER_FETCH_DAY = 0 # 0 = Monday, 6 = Sunday. 设置为 None 则每次都运行
FORCE_TWITTER = os.environ.get("FORCE_TWITTER", "false").lower() == "true"

# 在本地运行时，可以直接填入，但在 GitHub Actions 中会从环境变量读取

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
NOTION_API_KEY = os.environ.get("NOTION_API_KEY")
NOTION_DATABASE_ID = os.environ.get("NOTION_DATABASE_ID")

# Volcano Ark Config
ARK_API_KEY = os.environ.get("ARK_API_KEY")
ARK_MODEL_ID = os.environ.get("ARK_MODEL_ID")



def load_json_file(filename, default_value):
    """通用 JSON 文件加载函数"""
    try:
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"无法加载 {filename}: {e}")
    return default_value

CONFIG = load_json_file("config.json", {})

# 优先级: config.json > auto
LLM_PROVIDER = CONFIG.get("llm_provider", "auto").lower()

# 信源列表 (从 config 读取)
RSS_FEEDS = load_json_file("feeds.json", [])

# --- 初始化 ---

client = None
MODEL_NAME = "deepseek-chat" # Default



if LLM_PROVIDER == "volc" or (LLM_PROVIDER == "auto" and ARK_API_KEY and ARK_MODEL_ID):
    print("使用 Volcano Ark API")
    if not Ark:
         print("错误: 未安装 volcengine-python-sdk[ark]。")
    if not ARK_API_KEY or not ARK_MODEL_ID:
        print("警告: 选择了 Volcano Ark 但缺少 ARK_API_KEY 或 ARK_MODEL_ID")
    
    # 使用官方 Ark SDK
    client = Ark(api_key=ARK_API_KEY, base_url="https://ark.cn-beijing.volces.com/api/v3")
    MODEL_NAME = ARK_MODEL_ID
    
elif LLM_PROVIDER == "deepseek" or (LLM_PROVIDER == "auto" and DEEPSEEK_API_KEY):
    print("使用 DeepSeek API")
    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
    MODEL_NAME = "deepseek-chat"

if NOTION_API_KEY:
    notion = Client(auth=NOTION_API_KEY)

# --- 核心函数 ---

def is_recent(published_parsed):
    """检查文章是否在过去 24 小时内发布"""
    if not published_parsed:
        return True # 如果没有时间，默认处理
    published_dt = datetime.fromtimestamp(time.mktime(published_parsed))
    yesterday = datetime.now() - timedelta(hours=24)
    return published_dt > yesterday

def analyze_content(title, summary, link):
    """调用 DeepSeek AI 进行评分和分析"""
    if not client:
        print("DeepSeek Client 未初始化 (缺少 API Key)")
        return None

    prompt = f"""
你是一个眼光独到的科技产品猎手，专注于挖掘"独立开发"、"小而美"、"极具创意"的产品。

请分析以下产品信息：
标题: {title}
简介: {summary}
链接: {link}

评分标准 (0-10分):
- 9-10分: 极其独特的独立产品、视觉惊艳、解决了极其细分的痛点。
- 6-8分: 不错的工具，但可能缺乏惊喜。
- 0-5分: 大厂新闻、枯燥教程、加密货币、普通营销文。

请返回纯 JSON 格式 (不要 Markdown):
{{
    "score": number,
    "reason": "一句话中文点评 (30字以内)",
    "tags": ["Tag1", "Tag2"],
    "is_indie": boolean
}}
"""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that outputs JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        print(f"AI 分析失败: {e}")
        return None


def check_if_exists(link):
    """检查链接是否已存在于 Notion (使用 httpx 直接调用以通过绕过 SDK 问题)"""
    try:
        url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
        headers = {
            "Authorization": f"Bearer {NOTION_API_KEY}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
        
        body = {
            "filter": {
                "property": "URL",
                "url": {
                    "equals": link
                }
            }
        }
        
        response = httpx.post(url, headers=headers, json=body, timeout=10)
        if response.status_code != 200:
            print(f"检查重复请求失败: {response.status_code} {response.text}")
            return False
            
        data = response.json()
        return len(data.get('results', [])) > 0
    except Exception as e:
        print(f"检查重复失败: {e}")
        return False


def save_to_notion(item, analysis):
    """写入 Notion 数据库"""
    print(f"正在保存: {item.title} ({analysis['score']}分)")
    try:
        notion.pages.create(
            parent={"database_id": NOTION_DATABASE_ID},
            properties={
                "Name": {"title": [{"text": {"content": item.title}}]},
                "URL": {"url": item.link},
                "Score": {"number": analysis['score']},
                "AI Comment": {"rich_text": [{"text": {"content": analysis['reason']}}]},
                "Tags": {"multi_select": [{"name": tag} for tag in analysis['tags']]},
                "Date": {"date": {"start": datetime.now().isoformat()}}
            }
        )
    except Exception as e:
        print(f"Notion 写入失败: {e}")

# --- 主程序 ---

def main():
    print("开始运行 AI 选品程序 ...")

    for feed_url in RSS_FEEDS:
        print(f"正在抓取: {feed_url}")
        feed = feedparser.parse(feed_url)
        
        for entry in feed.entries:
            # 1. 过滤时间 (只看最近24小时)
            if not is_recent(entry.get('published_parsed')):
                continue
                
            title = entry.title
            link = entry.link
            summary = entry.get('summary', '')[:500] # 截取前500字避免 Token 溢出

            # 1.5 去重检查
            if check_if_exists(link):
                print(f"跳过重复: {title}")
                continue

            # 2. AI 分析
            print(f"正在分析: {title}...")
            analysis = analyze_content(title, summary, link)
            
            if not analysis:
                continue

            # 3. 筛选高分内容 (比如 > 7分)
            if (analysis.get('score') or 0) >= 7:
                save_to_notion(entry, analysis)
            else:
                print(f"低分跳过 ({analysis['score']}分): {title}")
                
            # 避免 API 速率限制
            time.sleep(2)



if __name__ == "__main__":
    main()
