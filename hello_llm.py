import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("LLM_API_KEY")
model = os.getenv("LLM_MODEL")
baseurl = os.getenv("LLM_BASE_URL")

if not api_key or not model:
    raise RuntimeError(
        "请先在 .env 中配置 LLM_API_KEY 和 LLM_MODEL"
    )

client = OpenAI(
    base_url=baseurl,
    api_key=api_key,
    timeout=30.0,
    max_retries=2,
)

response = client.chat.completions.create(
    model=model,
    messages=[
        {
            "role": "system",
            "content": "你是一个简洁、耐心的中文学习助手。",
        },
        {
            "role": "user",
            "content": "用三句话解释什么是 AI Agent。",
        },
    ],
)

print(response.choices[0].message.content)