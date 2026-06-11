# -*- coding: utf-8 -*-
"""
RAG 文档问答 — Streamlit Web 界面
用法: streamlit run app.py
"""
import streamlit as st
import os
import tempfile
from rag_core import RAGEngine

# ---- 页面配置 ----
st.set_page_config(page_title="RAG 文档问答", page_icon="📄", layout="wide")
st.title("📄 RAG 文档问答系统")
st.caption("上传 .docx 文件，然后对文档内容进行提问")

# ---- 初始化引擎（只初始化一次） ----
if "rag" not in st.session_state:
    st.session_state.rag = RAGEngine()
if "messages" not in st.session_state:
    st.session_state.messages = []

rag = st.session_state.rag

# ============================================================
# 侧边栏：文档管理
# ============================================================
with st.sidebar:
    st.header("📁 文档管理")

    # --- 单文件上传 ---
    uploaded_file = st.file_uploader("上传 .docx 文件", type=["docx"])
    if uploaded_file is not None:
        # 写入临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name

        with st.spinner("正在解析并向量化..."):
            count = rag.add_document(tmp_path)

        os.unlink(tmp_path)

        if count > 0:
            st.success(f"已添加 {count} 个文本块到向量库")
        else:
            st.warning("文档为空或解析失败，请检查文件内容")

    st.divider()

    # --- 批量导入本地文件夹 ---
    st.subheader("批量导入")
    dir_path = st.text_input("本地 .docx 文件夹路径", placeholder="例如 D:\\docs\\")
    if st.button("导入文件夹"):
        if dir_path and os.path.isdir(dir_path):
            total = 0
            for filename in os.listdir(dir_path):
                if filename.endswith(".docx"):
                    count = rag.add_document(os.path.join(dir_path, filename))
                    total += count
            if total > 0:
                st.success(f"共导入 {total} 个文本块")
            else:
                st.warning("该文件夹中没有 .docx 文件")
        else:
            st.error("文件夹路径不存在")

    st.divider()
    st.caption("技术栈: python-docx | ChromaDB | Ollama | Streamlit")

# ============================================================
# 主区域：对话
# ============================================================
st.subheader("💬 文档问答")

# 显示历史消息
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 输入框
if question := st.chat_input("输入你的问题，我会从文档中寻找答案..."):
    # 用户消息
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    # 生成回答
    with st.chat_message("assistant"):
        with st.spinner("正在检索并生成回答..."):
            answer = rag.ask(question)
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
