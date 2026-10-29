import json
import logging
import os

from dotenv import load_dotenv
from openai import OpenAI

from tools import calculate

load_dotenv()

MODEL = os.environ["LLM_MODEL"]
MAX_MODEL_ROUNDS = 5

client = OpenAI(
    api_key=os.environ["LLM_API_KEY"],
    base_url=os.environ["LLM_BASE_URL"],
    timeout=30.0,
    max_retries=2,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": (
                "对两个数字进行加、减、乘、除。"
                "用户要求进行数值计算时使用此工具。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "add",
                            "subtract",
                            "multiply",
                            "divide",
                        ],
                    },
                    "a": {
                        "type": "number",
                        "description": "第一个数字",
                    },
                    "b": {
                        "type": "number",
                        "description": "第二个数字",
                    },
                },
                "required": ["operation", "a", "b"],
                "additionalProperties": False,
            },
        },
    }
]

SYSTEM_MESSAGE = {
    "role": "system",
    "content": (
        "你是一个中文计算助手。"
        "普通聊天直接回答；数值计算必须调用 calculate 工具。"
        "以实际工具结果为依据，不要编造工具执行结果。"
        "参数不明确时向用户澄清，不要随意猜测。"
        "工具返回错误时，如实解释。"
        "涉及多个计算步骤时，可以逐步调用工具。"
    ),
}


def execute_tool(name: str, raw_arguments: str) -> dict:
    # 白名单：不允许模型任意指定可执行函数。
    if name != "calculate":
        return {
            "ok": False,
            "error": "未知工具",
        }

    try:
        arguments = json.loads(raw_arguments)
    except json.JSONDecodeError:
        return {
            "ok": False,
            "error": "工具参数不是合法 JSON",
        }

    if not isinstance(arguments, dict):
        return {
            "ok": False,
            "error": "工具参数必须是对象",
        }

    expected_keys = {"operation", "a", "b"}

    if set(arguments) != expected_keys:
        return {
            "ok": False,
            "error": "工具参数缺失或包含额外字段",
        }

    if not isinstance(arguments["operation"], str):
        return {
            "ok": False,
            "error": "operation 必须是字符串",
        }

    return calculate(
        operation=arguments["operation"],
        a=arguments["a"],
        b=arguments["b"],
    )


def run_agent(user_input: str, history: list) -> str:
    # 使用临时消息；成功完成后再提交到历史，
    # 避免请求失败时留下不完整的工具调用记录。
    messages = history + [
        {
            "role": "user",
            "content": user_input,
        }
    ]

    for round_number in range(1, MAX_MODEL_ROUNDS + 1):
        logging.info("模型调用轮次：%s", round_number)

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            parallel_tool_calls=False,
        )

        message = response.choices[0].message

        if not message.tool_calls:
            answer = message.content or "没有获得可显示的回答。"

            messages.append({
                "role": "assistant",
                "content": answer,
            })

            history[:] = messages
            return answer

        messages.append({
            "role": "assistant",
            "content": message.content,
            "tool_calls": [
                {
                    "id": call.id,
                    "type": "function",
                    "function": {
                        "name": call.function.name,
                        "arguments": call.function.arguments,
                    },
                }
                for call in message.tool_calls
            ],
        })

        for call in message.tool_calls:
            logging.info(
                "调用工具：%s，参数：%s",
                call.function.name,
                call.function.arguments,
            )

            result = execute_tool(
                call.function.name,
                call.function.arguments,
            )

            logging.info("工具结果：%s", result)

            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": json.dumps(
                    result,
                    ensure_ascii=False,
                ),
            })

    return (
        "已达到最大执行轮次，任务停止。"
        "本次对话未加入历史，请尝试简化问题。"
    )


def main():
    history = [SYSTEM_MESSAGE.copy()]

    print("计算 Agent 已启动。")
    print("输入 exit 退出，输入 reset 清空历史。")

    while True:
        user_input = input("\n你：").strip()

        if user_input.lower() in {"exit", "quit"}:
            break

        if user_input.lower() == "reset":
            history = [SYSTEM_MESSAGE.copy()]
            print("历史已清空。")
            continue

        if not user_input:
            continue

        try:
            answer = run_agent(user_input, history)
            print("助手：", answer)
        except Exception as exc:
            # 入门演示中仅显示异常类型，避免泄露配置或请求内容。
            print(f"执行失败：{type(exc).__name__}")
            print("请检查网络、模型权限和 API 配置。")


if __name__ == "__main__":
    main()

