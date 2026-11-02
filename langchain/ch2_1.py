# -*- coding: utf-8 -*-
"""第2章：第一个 LangChain 程序 —— 对应书中 2.4 问答程序示例（读 PDF 文档）

流程：PDF加载 -> 文本分割 -> 向量化入库 -> 检索 -> 问答
这正是全书后面 RAG 的雏形。

运行前置：
  1. 设置环境变量 LLM_BASE_URL / LLM_API_KEY
  2. knowledge/ 下放一个自己的 PDF（首次运行可用 scripts/make_demo_pdf.py 生成示例）
  3. 首次运行会下载 bge 嵌入模型（约100MB），之后走本地缓存
"""
from llm import llm, embeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

# ---------- 1. 加载 PDF ----------
pdf_path = "knowledge/demo.pdf"
loader = PyPDFLoader(pdf_path)
docs = loader.load()          # 按页返回 Document 对象
print(f"PDF 共 {len(docs)} 页")

# ---------- 2. 分割 ----------
chunks = RecursiveCharacterTextSplitter(
    chunk_size=500, chunk_overlap=50,
    separators=["\n\n", "\n", "。", "，", ""],
).split_documents(docs)
print(f"切分后 {len(chunks)} 个片段")

# ---------- 3. 向量化入库 ----------
vectorstore = Chroma.from_documents(chunks, embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# ---------- 4. 组装问答链 ----------
def format_docs(ds):
    return "\n\n".join(d.page_content for d in ds)

prompt = ChatPromptTemplate.from_template(
    "仅根据以下上下文回答问题，上下文没有的就说不知道。\n"
    "上下文：{context}\n问题：{question}"
)

chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt | llm | StrOutputParser()
)

# ---------- 5. 提问 ----------
if __name__ == "__main__":
    question = "这个文档主要讲了什么？"
    print(chain.invoke(question))
