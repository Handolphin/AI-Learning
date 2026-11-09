import os
from openai import OpenAI
from dotenv import load_dotenv

# 1. 读取 .env 文件
load_dotenv()

# 2. 获取 API Key
api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    raise ValueError("没有找到 DEEPSEEK_API_KEY，请检查 .env 文件")

# 3. 创建 DeepSeek 客户端
client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"
)

# 4. 向 DeepSeek 发送请求
response = client.chat.completions.create(
    model="deepseek-flash",
    messages=[
        {
            "role": "system",
            "content": "你是一个专业的工程项目文档分析助手。"
        },
        {
            "role": "user",
            "content": "请总结以下会议纪要：今天召开道路改造工程协调会，施工单位汇报了当前进度，计划下周完成路面铣刨工作。"
        }
    ]
)

# 5. 获取并打印 AI 的回答
print(response.choices[0].message.content)