"""Day 1 产出物：多轮对话命令行脚本（不依赖任何框架）。"""
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def require_env(name):
    value = os.getenv(name)
    if not value:
        raise SystemExit(f"缺少环境变量 {name}，请在 .env 中设置")
    return value


client = OpenAI(
    api_key=require_env("LLM_API_KEY"),
    base_url=require_env("LLM_BASE_URL"),
)
MODEL = require_env("LLM_MODEL")


def check_model():
    # 启动时向网关拉取当前令牌可用的模型列表，不支持的模型直接报错退出
    available = sorted(m.id for m in client.models.list())
    if MODEL not in available:
        raise SystemExit(
            f"模型 {MODEL} 不可用，请修改 .env 中的 LLM_MODEL。\n"
            f"可用模型: {', '.join(available)}"
        )


def main():
    check_model()
    # messages 列表就是模型的"记忆"：每一轮都要把完整历史传过去
    messages = [{"role": "system", "content": "你是一个简洁的助手。"}]
    print("多轮对话（输入 exit 退出）\n")
    while True:
        user = input("你: ").strip()
        if not user or user.lower() in ("exit", "quit"):
            break
        messages.append({"role": "user", "content": user})

        resp = client.chat.completions.create(model=MODEL, messages=messages)
        reply = resp.choices[0].message.content
        messages.append({"role": "assistant", "content": reply})

        print(f"助手: {reply}")
        # 观察 token 用量：上下文越长，prompt_tokens 越大 —— 这就是为什么要做记忆压缩
        print(
            f"[tokens] prompt={resp.usage.prompt_tokens} "
            f"completion={resp.usage.completion_tokens}\n"
        )


if __name__ == "__main__":
    main()
