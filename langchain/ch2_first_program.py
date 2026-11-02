# -*- coding: utf-8 -*-
"""第2章：第一个 LangChain 程序 —— 验证厂内网关连通性"""
from llm import llm

# 普通调用：返回 AIMessage 对象，.content 才是文本
result = llm.invoke("用一句话解释什么是大语言模型")
print(result.content)

# 流式调用：内网网关不一定支持 stream，跑不通也不影响后续章节
try:
    for chunk in llm.stream("从1数到5"):
        print(chunk.content, end="", flush=True)
    print()
except Exception as e:
    print(f"[提示] 当前网关不支持流式输出，跳过：{e}")