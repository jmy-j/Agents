# 📄 RAG 文档问答系统

> 基于 Python + Ollama + Streamlit 的本地私有 RAG（检索增强生成）Demo，支持 .docx 文件索引与自然语言问答。

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Ollama](https://img.shields.io/badge/Ollama-local-orange)](https://ollama.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.58-red)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

## 🎯 项目简介

本系统是一个**完全本地运行**的 RAG Demo，无需 API Key，不上传任何数据到云端。

- 📥 上传 .docx 文档 → 自动解析、分块、向量化存储
- 💬 用自然语言对文档内容提问 → 自动检索相关内容 → LLM 生成精准回答
- 🔍 支持跨文档检索，一个向量库管理多份文档

## 🏗️ 架构

```
用户上传 .docx → python-docx 提取文字 → 文本分块(500字/块)
     ↓
nomic-embed-text 向量化 → ChromaDB 向量库
     ↓
用户提问 → 问题向量化 → 相似度检索(Top-4) → 拼接 Prompt → qwen:0.5b 生成回答
```

| 组件 | 技术 | 用途 |
|------|------|------|
| 文档解析 | `python-docx` | 提取 .docx 文件中的文字 |
| 文本分块 | `langchain-text-splitters` | 按语义切分长文档 |
| 向量化 | Ollama `nomic-embed-text` (274MB) | 把文字转成 768 维向量 |
| 向量存储 | `ChromaDB` | 本地持久化，支持相似度检索 |
| 对话生成 | Ollama `qwen:0.5b` (394MB) | 依据文档内容生成自然语言回答 |
| Web 界面 | `Streamlit` | 聊天式交互，浏览器访问 |

## 🚀 快速开始

### 1. 环境要求

- Python 3.10+
- [Ollama](https://ollama.com/)（安装后需在后台运行）

### 2. 下载模型

```bash
ollama pull nomic-embed-text   # Embedding 模型 (274MB)
ollama pull qwen2.5:7b         # 对话模型 (4.7GB，可选，推荐)
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 启动

```bash
streamlit run app.py
```

浏览器自动打开 `http://localhost:8501`，上传 .docx 文件即可开始提问。

## 📖 使用说明

### 上传文档
- **单文件**：侧边栏点击上传按钮，选择 .docx 文件
- **批量导入**：输入本地文件夹路径，一键导入全部 .docx

### 提问技巧
- 问题越具体，回答越精确
- 支持跨文档检索（上传多份文档后可以跨文件提问）
- 向量库持久化在 `./chroma_db/` 目录，重启不丢失

## ⚙️ 可调参数

编辑 `rag_core.py` 顶部：

```python
CHUNK_SIZE = 500       # 文本块大小（字）
CHUNK_OVERLAP = 50     # 块间重叠（字）
SEARCH_K = 4           # 每次检索返回的块数
CHAT_MODEL = "qwen:0.5b"  # 对话模型（换更大模型提升质量）
```

## 📁 项目结构

```
RAG/
├── app.py              # Streamlit Web 界面
├── rag_core.py         # RAG 核心引擎（解析、向量化、检索、生成）
├── requirements.txt    # Python 依赖
├── 使用手册.md          # 详细使用手册 + 数据流图
├── .vscode/
│   └── settings.json   # 编辑器 UTF-8 编码配置
├── chroma_db/          # 向量库数据（自动生成）
└── README.md
```

## 🔒 隐私说明

所有数据（文档、向量、模型推理）均在本地完成，**不需要网络连接**（模型下载除外）。不会上传任何数据到外部服务。

## 🔜 后续计划

- [ ] 支持 .pdf 文件
- [ ] 支持 .doc (旧版 Word) 格式
- [ ] Reranker 二次精排提升检索精度
- [ ] 对话历史持久化
- [ ] Docker 一键部署

## 📄 License

MIT License
