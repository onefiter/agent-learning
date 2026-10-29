# 计算 Agent

一个入门级 Agent：模型通过工具调用请求加减乘除，由 Python 程序校验参数并执行，结果送回模型后生成最终回答。

## 文件

- `hello_llm.py`：第一次调用模型。
- `chat.py`：多轮对话，启动时检查模型是否可用。
- `tools.py`：`calculate` 工具。
- `test_tools.py`：工具的单元测试。
- `agent.py`：工具调用循环。
- `evaluation.md`：评测用例。

## 环境安装

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## 配置 `.env`

在本目录新建 `.env`（已被 `.gitignore` 忽略，不要提交）：

```text
LLM_API_KEY=网关控制台“令牌”页面创建的令牌，形如 sk-...
LLM_BASE_URL=网关地址，以 /v1 结尾，本地默认为 http://localhost:3000/v1
LLM_MODEL=网关渠道里已启用、且支持工具调用的模型名
```

三个变量都必须设置，缺少时 `chat.py` 和 `agent.py` 会直接报错退出。

## 运行

```bash
python hello_llm.py          # 单次问答
python chat.py               # 多轮对话，exit 退出
python -m unittest -v        # 工具单元测试
python agent.py              # 计算 Agent，exit 退出，reset 清空历史
```

## 示例输入

```text
你好。
125 加 378 是多少？
10 除以 0。
先计算 15 乘以 8，再把结果加 20。
把两个数加起来。
```

## 已知限制

- 只支持两个数字的四则运算。
- 复杂问题可能超过 5 轮的模型调用上限。
- 历史只保存在当前进程，退出即丢失。
- 使用普通浮点数，不适合严格的金融精度。
- 没有费用统计，也没有自动化的端到端评测。
