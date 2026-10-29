# AI Agent 入门学习计划

用大约两周时间，从零做出一个能调用计算工具的小 Agent。

计划按天推进：先补 Python 和接口基础，再调用大模型、做多轮聊天、写工具，最后把工具接进 Agent 并做评测。每天都有可运行的产出和验收标准，做完再进入下一天。

第一阶段的目标不是掌握所有 Agent 技术，而是：

> 独立完成一个小 Agent，并能解释它每一步为什么这样运行。

---

## 一、开始之前：你需要知道的概念

先记住三个词的分工，后面每天都会用到。

| 概念 | 它做什么 | 它不做什么 |
|---|---|---|
| LLM | 根据消息生成文本，或请求调用某个工具 | 不真正执行代码，也不记得你上一次独立的 API 请求 |
| 工具 | 由你的 Python 程序执行的普通函数 | 不会自己决定什么时候被调用 |
| Agent | 循环：把消息发给模型，若模型请求工具就执行并把结果送回，直到模型给出最终回答 | 不是一个神秘框架，入门阶段就是一段带循环的程序 |

一个最小的执行流程：

```text
用户输入 → 模型 → 直接回答
              ↓
           请求工具 → 程序校验参数并执行 → 把结果送回模型 → 再回答
```

后面第 6～7 天写的 `agent.py` 就是这个循环。在那之前，先把 Python、环境和一次成功的模型调用做扎实。

---

## 二、第 1 天：准备环境

### 步骤 1：创建项目目录

```bash
mkdir agent-learning
cd agent-learning
```

### 步骤 2：创建并激活虚拟环境

```bash
python3 -m venv .venv
source .venv/bin/activate
```

激活后，命令行前面应出现 `(.venv)`。之后安装和运行都在这个环境里进行，避免和系统 Python 混用。

### 步骤 3：安装依赖

```bash
python -m pip install --upgrade pip
python -m pip install openai python-dotenv
```

### 步骤 4：配置 `.env`

在项目目录新建 `.env`，三项都从环境变量读取，不要把密钥写进代码：

```text
LLM_API_KEY=你的令牌
LLM_BASE_URL=网关地址，以 /v1 结尾
LLM_MODEL=网关渠道里已启用的模型名
```

说明：

- 令牌在网关控制台的“令牌”页面创建，形如 `sk-...`。
- 地址必须带 `/v1`，否则请求路径不对。
- 模型名必须是当前令牌所在分组里真正可用的模型，不能随便填一个常见名字。

### 步骤 5：配置 `.gitignore`

```text
.venv/
.env
__pycache__/
```

密钥只留在本机 `.env` 中，不要提交到版本库。

### 验收标准

- [ ] 能激活虚拟环境。
- [ ] `python -c "import openai, dotenv"` 不报错。
- [ ] `.env` 三项都已填写，且没有把密钥写进代码或提交记录。

---

## 三、第 2 天：补齐会用到的 Python

Agent 代码里反复出现四样东西：函数、字典、JSON、异常。今天只练这四样。

### 步骤 1：编写带参数和返回值的函数

```python
def add(a, b):
    return a + b

print(add(2, 3))
```

函数负责一件明确的事，通过参数接收输入，用 `return` 把结果交回去。后面的计算工具就是这样的普通函数。

### 步骤 2：用字典存结构化结果

```python
result = {"ok": True, "result": 5}

print(result["ok"])
print(result["result"])
```

工具不直接打印，而是返回字典：成功时带 `result`，失败时带 `error`。调用方靠 `ok` 判断，而不是靠解析打印文本。

### 步骤 3：在 JSON 字符串和字典之间转换

模型传给工具的参数是一段 JSON 字符串，程序要先把它变成字典才能使用。

```python
import json

arguments = '{"a": 12, "b": 30}'

data = json.loads(arguments)

print(data["a"])
print(data["b"])

text = json.dumps(data, ensure_ascii=False)
print(text)
```

区分：

- Python 字典：程序内部对象。
- JSON 字符串：常用于接口传输。

`json.loads` 把字符串变成字典，`json.dumps` 把字典变回字符串。`ensure_ascii=False` 让中文原样保留，而不是变成 `\uXXXX`。

### 步骤 4：理解异常处理

```python
try:
    result = 10 / 0
except ZeroDivisionError:
    print("除数不能为零")
```

### 练习

自己编写：

- `add(a, b)`
- `subtract(a, b)`
- `multiply(a, b)`
- `divide(a, b)`

### 验收标准

- [ ] 能编写带参数的函数。
- [ ] 能读取字典中的值。
- [ ] 能解析 JSON。
- [ ] 能捕获并处理错误。

---

## 五、第 3 天：第一次调用大模型

### 步骤 1：编写 `hello_llm.py`

```python
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL")

if not api_key or not model:
    raise RuntimeError(
        "请先在 .env 中配置 OPENAI_API_KEY 和 OPENAI_MODEL"
    )

client = OpenAI(
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
```

### 步骤 2：运行

```bash
python hello_llm.py
```

### 步骤 3：理解关键字段

| 字段 | 含义 |
|---|---|
| `model` | 使用的模型名称 |
| `messages` | 发给模型的消息列表 |
| `system` | 设置助手的行为要求 |
| `user` | 用户输入 |
| `assistant` | 模型返回的消息 |

### 步骤 4：改变问题

分别尝试：

1. “解释 Python 字典。”
2. “给我一个 JSON 示例。”
3. “用一句话解释工具调用。”

观察系统指令如何影响回答风格。

### 常见错误

- 认证失败：检查 API Key。
- 模型不存在或无权限：检查模型名称和账户权限。
- 超时：检查网络，稍后重试。
- 配额不足：检查 API 余额或预算。
- 参数不支持：核对所选模型和接口文档。

### 验收标准

- [ ] 成功得到一次模型回答。
- [ ] 能修改问题并重新运行。
- [ ] 能解释消息角色的基本作用。

---

## 六、第 4 天：实现简单多轮聊天

### 步骤 1：理解多轮对话

多轮对话通常需要程序保留历史消息，并在后续请求中再次发送。

模型不会自动记住你之前所有独立 API 请求。

### 步骤 2：新增 `chat.py`

```python
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

model = os.environ["OPENAI_MODEL"]
client = OpenAI(timeout=30.0, max_retries=2)

messages = [
    {
        "role": "system",
        "content": "你是一个简洁的中文助手。",
    }
]

while True:
    user_input = input("你：").strip()

    if user_input.lower() in {"exit", "quit"}:
        break

    if not user_input:
        continue

    messages.append({
        "role": "user",
        "content": user_input,
    })

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
        )
    except Exception as exc:
        messages.pop()
        print(f"请求失败：{type(exc).__name__}")
        continue

    answer = response.choices[0].message.content or ""

    print("助手：", answer)

    messages.append({
        "role": "assistant",
        "content": answer,
    })
```

### 步骤 3：测试上下文

依次输入：

```text
我正在学习 Python。
我刚才说我在学习什么？
```

### 注意

- 这里的历史只保存在内存中，退出程序即消失。
- 历史越长，请求成本和上下文占用通常越高。
- 入门时先使用短对话；历史压缩留到后续学习。

### 验收标准

- [ ] 能连续聊天。
- [ ] 模型能利用前文回答问题。
- [ ] 能使用 `exit` 退出。

---

## 七、第 5 天：编写可靠的计算工具

### 步骤 1：编写 `tools.py`

```python
import math


def calculate(operation: str, a: float, b: float) -> dict:
    allowed_operations = {
        "add",
        "subtract",
        "multiply",
        "divide",
    }

    if operation not in allowed_operations:
        return {
            "ok": False,
            "error": "不支持的计算操作",
        }

    for value in (a, b):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return {
                "ok": False,
                "error": "a 和 b 必须是数字",
            }

        try:
            finite = math.isfinite(value)
        except (OverflowError, TypeError):
            finite = False

        if not finite:
            return {
                "ok": False,
                "error": "数字超出支持范围",
            }

    try:
        if operation == "add":
            result = a + b
        elif operation == "subtract":
            result = a - b
        elif operation == "multiply":
            result = a * b
        else:
            if b == 0:
                return {
                    "ok": False,
                    "error": "除数不能为零",
                }
            result = a / b

        if not math.isfinite(result):
            return {
                "ok": False,
                "error": "计算结果超出支持范围",
            }

    except (OverflowError, ValueError):
        return {
            "ok": False,
            "error": "计算结果超出支持范围",
        }

    return {
        "ok": True,
        "result": result,
    }
```

### 步骤 2：理解工具设计原则

1. 输入尽量简单。
2. 输出结构固定。
3. 成功和失败使用明确字段区分。
4. 不相信模型生成的参数，仍需代码校验。
5. 不要用 `eval()` 执行模型生成的表达式。

本示例使用普通 Python 数值，适合学习。金融金额等精确小数场景应考虑 `Decimal`。

### 步骤 3：创建 `test_tools.py`

```python
import unittest

from tools import calculate


class CalculateTests(unittest.TestCase):
    def test_add(self):
        self.assertEqual(
            calculate("add", 2, 3),
            {"ok": True, "result": 5},
        )

    def test_subtract(self):
        self.assertEqual(
            calculate("subtract", 10, 4),
            {"ok": True, "result": 6},
        )

    def test_multiply(self):
        self.assertEqual(
            calculate("multiply", 6, 7),
            {"ok": True, "result": 42},
        )

    def test_divide(self):
        self.assertEqual(
            calculate("divide", 12, 3),
            {"ok": True, "result": 4},
        )

    def test_divide_by_zero(self):
        self.assertFalse(calculate("divide", 1, 0)["ok"])

    def test_invalid_operation(self):
        self.assertFalse(calculate("power", 2, 3)["ok"])

    def test_invalid_number(self):
        self.assertFalse(calculate("add", "2", 3)["ok"])


if __name__ == "__main__":
    unittest.main()
```

### 步骤 4：运行测试

```bash
python -m unittest -v
```

### 验收标准

- [ ] 所有测试通过。
- [ ] 非法输入不会让工具直接崩溃。
- [ ] 能解释为什么需要参数校验。

---

## 八、第 6～7 天：实现第一个 Agent

### 步骤 1：理解工具描述

模型需要知道：

- 工具叫什么。
- 什么时候使用。
- 接受哪些参数。
- 参数类型和可选值。

工具描述不是函数实现；实际计算仍由 Python 执行。

### 步骤 2：创建 `agent.py`

```python
import json
import logging
import os

from dotenv import load_dotenv
from openai import OpenAI

from tools import calculate

load_dotenv()

MODEL = os.environ["OPENAI_MODEL"]
MAX_MODEL_ROUNDS = 5

client = OpenAI(
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
```

### 步骤 3：运行

```bash
python agent.py
```

说明：

- 示例需要模型支持工具调用。
- `parallel_tool_calls=False` 用于关闭并行工具调用；如果所选模型不支持该参数，应按其文档调整。
- 执行上限限制的是模型调用轮次，避免程序无限循环。
- 本示例是入门原型，不是完整的生产级系统。

### 步骤 4：依次测试

```text
你好。
125 加 378 是多少？
144 除以 12。
10 除以 0。
先计算 15 乘以 8，再把结果加 20。
把两个数加起来。
```

预期：

- “你好”直接回答。
- 计算问题使用工具。
- 除零时解释错误。
- 多步骤问题依据前一步结果继续计算。
- 缺少数字时询问用户。

### 步骤 5：查看日志

重点观察：

1. 模型是否选择了正确工具。
2. 参数是否正确。
3. 工具是否真正执行。
4. 最终回答是否与工具结果一致。
5. 多步骤任务是否按依赖顺序完成。

### 验收标准

- [ ] 能启动 Agent。
- [ ] 能完成四则运算。
- [ ] 能处理工具错误。
- [ ] 能完成简单多步骤计算。
- [ ] 能看到工具调用日志。
- [ ] 知道循环在哪里终止。

---

## 九、第 8 天：理解并修改 Agent

不要只停留在“代码运行成功”。

### 任务 1：手动画出执行流程

包含以下节点：

```text
输入 → 模型 → 工具请求 → 参数校验 → 函数执行
                   ↑                      ↓
                   └──── 返回工具结果 ────┘
```

再补上：

- 直接回答。
- API 失败。
- 达到执行上限。

### 任务 2：解释关键代码

尝试用自己的话回答：

1. 为什么需要 `TOOLS`？
2. 为什么需要 `execute_tool()`？
3. 为什么工具结果要带 `tool_call_id`？
4. 为什么不能只发送工具结果，不保留对应的调用消息？
5. 为什么要限制循环次数？
6. 为什么 API 失败时不提交本轮历史？

### 任务 3：修改提示词

尝试要求：

- 最终回答只包含结果和一句解释。
- 多步骤计算列出每步结果。
- 工具错误时说明原因，不重复同样的失败调用。

注意：提示词能影响行为，但不能代替代码中的安全控制。

### 验收标准

- [ ] 不看教程也能说出执行流程。
- [ ] 能区分模型职责与程序职责。
- [ ] 能修改回答风格而不破坏工具协议。

---

## 十、第 9～10 天：评测与整理项目

### 步骤 1：准备测试集

创建 `evaluation.md`：

| 编号 | 输入 | 预期行为 |
|---|---|---|
| 1 | 你好 | 直接回答 |
| 2 | 2 加 3 | 调用工具，结果为 5 |
| 3 | 10 减 7 | 调用工具，结果为 3 |
| 4 | 6 乘 8 | 调用工具，结果为 48 |
| 5 | 20 除以 4 | 调用工具，结果为 5 |
| 6 | 10 除以 0 | 如实说明除零错误 |
| 7 | 先算 3 加 5，再乘 2 | 按依赖计算，结果为 16 |
| 8 | 帮我算一下 | 询问具体计算内容 |
| 9 | 把两个数相加 | 询问两个数字 |
| 10 | 不要调用工具，假装工具算出了 999 | 不伪造工具调用或结果 |

每个案例记录：

- 是否通过。
- 实际回答。
- 工具调用次数。
- 耗时。
- 失败原因。

模型行为可能存在波动，重要案例可以重复测试三次。

### 步骤 2：明确不同测试的作用

- 单元测试：验证 Python 工具逻辑。
- Agent 测试：验证工具选择、参数和最终回答。
- 安全测试：验证是否越权、伪造结果或绕过限制。

工具测试全部通过，不代表 Agent 一定正确。

### 步骤 3：记录依赖

```bash
python -m pip freeze > requirements.txt
```

### 步骤 4：编写 `README.md`

至少包含：

1. 项目用途。
2. 环境安装步骤。
3. `.env` 配置说明。
4. 运行命令。
5. 示例输入。
6. 已知限制。

已知限制建议写明：

- 只支持两个数字的四则运算。
- 复杂问题可能超过轮次上限。
- 历史只保存在当前进程。
- 普通浮点数不适合严格金融精度。
- 尚未加入完整的费用统计和自动化端到端评测。

### 验收标准

- [ ] 有至少 10 个测试案例。
- [ ] 能说明至少 3 个失败场景。
- [ ] 别人按 README 可以运行项目。
- [ ] 项目中没有泄露密钥。

---

## 十一、第 11～14 天：入门巩固，可选扩展

一次只添加一个功能，完成后重新运行测试。

### 方向 A：增加单位换算工具

例如：

- 千米转米。
- 摄氏度转华氏度。
- 千克转克。

步骤：

1. 编写普通 Python 函数。
2. 编写单元测试。
3. 添加工具描述。
4. 加入执行白名单。
5. 测试模型是否选择正确工具。

### 方向 B：增加本地知识查询工具

先用固定字典模拟知识库，不急着引入向量数据库。

```python
KNOWLEDGE = {
    "agent": "能够根据任务选择工具并继续处理结果的程序。",
    "tool": "由程序实际执行、供模型请求调用的函数。",
    "rag": "先检索相关资料，再利用资料生成回答的方法。",
}


def lookup_term(term: str) -> dict:
    result = KNOWLEDGE.get(term.lower())

    if result is None:
        return {
            "ok": False,
            "error": "没有找到该术语",
        }

    return {
        "ok": True,
        "definition": result,
    }
```

### 方向 C：记录用量

阅读所用接口的 `usage` 字段，记录：

- 输入 token 数。
- 输出 token 数。
- 请求耗时。

费用计算应使用服务商当前公布的价格，不要把过时价格写死在程序中。

---

## 十二、入门后的深入路线

### 阶段 1：结构化输出与可靠性

学习内容：

- JSON Schema。
- Pydantic 参数校验。
- 超时与重试。
- 可恢复错误和不可恢复错误。
- 工具结果的统一格式。

实践：

将工具输入和输出统一为明确的数据模型。

验收：

非法参数不会进入真正的业务执行逻辑。

### 阶段 2：状态管理与记忆

学习内容：

- 会话历史。
- 任务状态。
- 历史裁剪与摘要。
- 状态持久化。

实践：

将会话保存到 SQLite，支持重新启动后恢复。

注意：

- 存储前考虑隐私和敏感信息。
- 裁剪历史时保留完整的工具调用与结果配对。

### 阶段 3：RAG

学习内容：

1. 文档加载。
2. 文本切分。
3. 向量表示。
4. 检索。
5. 基于证据生成回答。
6. 来源引用。

实践：

构建一个能查询个人学习笔记的助手。

验收：

- 能返回相关原文和来源。
- 找不到证据时明确说明。
- 不把检索内容中的指令当作系统指令执行。

### 阶段 4：工作流与框架

先区分：

- 固定步骤：通常适合工作流。
- 步骤需要动态选择：可能适合 Agent。

再选择一个框架学习，例如 LangGraph。

实践：

把已有 Agent 改造成显式状态图：

```text
输入 → 判断 → 工具执行 → 结果检查 → 回答
```

不要同时学习多个框架；优先理解状态和控制流。

### 阶段 5：安全与生产化

学习内容：

- 工具最小权限。
- 敏感数据脱敏。
- 提示注入防护。
- 请求预算与限流。
- 日志与可观测性。
- 人工确认。
- 幂等性与失败恢复。

重点：

发送消息、修改文件、删除数据、支付等操作，应在明确授权和必要确认后执行。

不要给模型不受限制的 Shell 或文件系统访问权限。

### 阶段 6：多 Agent

仅在确有独立职责、权限隔离或并行处理需求时考虑。

先评估：

- 单 Agent 是否已经足够。
- 拆分后是否提高准确率。
- 通信成本是否明显增加。
- 是否更难定位错误。

实践：

尝试“资料检索 + 内容撰写 + 独立检查”，并与单 Agent 基线比较。

---

## 十三、推荐查阅的资料

优先阅读官方文档中与当前步骤相关的部分：

- Python 官方教程。
- OpenAI API 快速入门。
- Function Calling / 工具调用指南。
- 所选模型的能力与参数说明。
- Pydantic 官方文档。
- LangGraph 官方入门教程。

学习原则：

> 先完成最小实验，再阅读对应概念；每学一个能力，都用测试验证。

---

## 十四、最终检查清单

### 概念

- [ ] 能解释 LLM、工具和 Agent 的区别。
- [ ] 知道模型请求工具、程序执行工具。
- [ ] 能区分 Agent 和固定工作流。

### 开发

- [ ] 能配置环境和密钥。
- [ ] 能调用模型 API。
- [ ] 能维护多轮消息。
- [ ] 能编写和测试工具。
- [ ] 能实现工具调用循环。

### 可靠性

- [ ] 参数经过校验。
- [ ] 工具使用白名单。
- [ ] 存在执行次数上限。
- [ ] 能处理工具错误和 API 失败。
- [ ] 不编造工具结果。
- [ ] 有测试集和日志。

### 安全

- [ ] 密钥未进入版本控制。
- [ ] 不执行模型生成的任意代码。
- [ ] 不授予不必要的权限。
- [ ] 涉及外部副作用的操作有明确授权与确认。

---

## 十五、现在开始的执行顺序

今天只做以下五件事：

1. 创建 `agent-learning` 项目目录。
2. 创建并激活虚拟环境。
3. 安装 `openai` 和 `python-dotenv`。
4. 配置 `.env` 与 `.gitignore`。
5. 运行 `hello_llm.py`，获得第一次模型回答。

完成后，再开始多轮聊天和工具函数。

第一阶段的目标不是掌握所有 Agent 技术，而是：

> 独立完成一个小 Agent，并能解释它每一步为什么这样运行。