import os
from openai import OpenAI
from dotenv import load_dotenv

# 1. 读取 .env 文件(读取环境变量)
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
#接收用户输入
meeting_content=input("请输入会议纪要：")
# 4. 向 DeepSeek 发送请求
if not meeting_content.strip():
    print("会议纪要不能为空")
else:
    response = client.chat.completions.create(
        model="deepseek-flash",
        messages=[
            {
                "role": "system",
                "content": "你是一个专业的工程项目文档分析助手。"
            },
            {
                "role": "user",
                "content": f"请总结以下会议纪要：{meeting_content}"
            }
        ]
    )

# 5. 获取并打印 AI 的回答
    print("\nAI 生成的会议纪要总结：")
    print(response.choices[0].message.content)