# -*- coding: utf-8 -*-
"""生成示例 PDF（knowledge/demo.pdf），供 ch2_1.py 使用。
嵌入本机中文字体，避免 STSong-Light 的西文按半角排版、
预览却按全角画出，导致英文和标识符挤成一团。
只在学习环境使用，跑一次即可：python scripts/make_demo_pdf.py
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph

FONT_NAME = "CJK"
# 优先用可嵌入的系统字体；STSong-Light 是 CID 字体，不嵌入字形，
# macOS 预览会把拉丁字母画成全角，和排版宽度对不上。
FONT_CANDIDATES = [
    ("/System/Library/Fonts/Supplemental/Songti.ttc", 0),
    ("/System/Library/Fonts/STHeiti Light.ttc", 0),
    ("/Library/Fonts/Arial Unicode.ttf", None),
    ("C:/Windows/Fonts/msyh.ttc", 0),
    ("C:/Windows/Fonts/simsun.ttc", 0),
    ("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 0),
]


def register_cjk_font():
    for path, subfont_index in FONT_CANDIDATES:
        if not os.path.exists(path):
            continue
        kwargs = {"subfontIndex": subfont_index} if subfont_index is not None else {}
        pdfmetrics.registerFont(TTFont(FONT_NAME, path, **kwargs))
        return path
    raise FileNotFoundError(
        "找不到可嵌入的中文字体。请安装宋体/微软雅黑/Noto Sans CJK 后重试。"
    )

text = (
    "LangChain安装方法：使用pip install langchain langchain-openai即可完成安装。"
    "安装完成后需要配置大模型网关地址和API密钥才能正常调用。"
    "如果在公司内网环境，还需要确认能访问模型网关地址。"

    "文本分割器的作用是把长文档切成小块，以便后续做向量检索。"
    "LangChain推荐使用RecursiveCharacterTextSplitter，它会优先在段落、"
    "句子等自然边界处切分，保持语义完整。中文文档建议把句号和逗号"
    "加入分隔符列表。chunk_size控制每块最大长度，chunk_overlap控制"
    "相邻块之间的重叠部分，避免关键信息正好被切断。"

    "检索增强生成（RAG）的流程是：文档加载、文本分割、向量化入库、"
    "检索相关片段、把片段和问题一起交给大模型生成答案。"
    "这样可以回答模型训练数据里没有的知识，也能减少幻觉。"
    "LangChain中通过检索器和链的组合可以快速搭建RAG应用。"
)


def main():
    font_path = register_cjk_font()
    out = os.path.join(os.path.dirname(__file__), "..", "knowledge", "demo.pdf")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    style = ParagraphStyle("cn", fontName=FONT_NAME, fontSize=12,
                           leading=20, firstLineIndent=24)
    doc = SimpleDocTemplate(out, pagesize=A4,
                            leftMargin=2 * cm, rightMargin=2 * cm,
                            topMargin=2 * cm, bottomMargin=2 * cm)
    doc.build([Paragraph(p, style) for p in text.strip().split("\n\n")])
    print(f"已生成示例PDF：{os.path.abspath(out)}")
    print(f"使用字体：{font_path}")


if __name__ == "__main__":
    main()
