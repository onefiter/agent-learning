# -*- coding: utf-8 -*-
"""
llm.py —— 全项目统一配置模块
从环境变量读取厂内模型配置：
  LLM_BASE_URL : 厂内 OpenAI 兼容网关地址（以 /v1 结尾）
  LLM_API_KEY  : 内部 token（网关不校验时也要设为非空值）
  LLM_MODEL    : 模型名（可选，默认 DeepSeek-V4.1-Flash）

使用前：
  export LLM_BASE_URL="http://llm-gateway.公司内网/v1"
  export LLM_API_KEY="sk-你的内部token"
"""
import os

# huggingface.co 在当前网络下 SSL 握手会被中断（UNEXPECTED_EOF_WHILE_READING）。
# huggingface_hub 在 import 时就读 HF_ENDPOINT，所以必须放在相关 import 之前。
# 已显式设置 HF_ENDPOINT 时不覆盖。
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")

from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings

# ---------- 对话模型（厂内网关，OpenAI 兼容） ----------
llm = ChatOpenAI(
    model=os.environ.get("LLM_MODEL", "DeepSeek-V4.1-Flash"),
    base_url=os.environ["LLM_BASE_URL"],   # 未设置时直接报错提醒，比静默连到外网好
    api_key=os.environ["LLM_API_KEY"],     # OpenAI 客户端要求非空
    temperature=0,
)

# ---------- 嵌入模型（本地 bge，不依赖网络、不花钱） ----------
embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-zh-v1.5")
