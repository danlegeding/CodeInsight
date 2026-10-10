CodeInsight — AI 代码分析与项目问答助手

CodeInsight 是一个基于大语言模型（LLM）与检索增强生成（RAG）的 AI 代码分析与项目问答应用。

用户可以上传 ZIP 格式的代码项目，通过自然语言提问，检索相关源码片段，并结合大语言模型生成具有代码上下文的回答。

项目采用前后端分离架构，后端负责代码处理、向量化、语义检索与问答流程编排，前端提供可视化交互界面。

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.13-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/LangChain-RAG-1C3C3C" alt="LangChain">
  <img src="https://img.shields.io/badge/PostgreSQL-pgvector-4169E1?logo=postgresql" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Frontend-Streamlit-FF4B4B?logo=streamlit" alt="Streamlit">
</p>---

📑 目录

- "项目功能" (#-项目功能)
- "技术栈" (#-技术栈)
- "系统架构" (#-系统架构)
- "核心流程" (#-核心流程)
- "项目结构" (#-项目结构)
- "环境要求" (#-环境要求)
- "快速开始" (#-快速开始)
- "API 接口" (#-api-接口)
- "技术设计" (#-技术设计)
- "后续计划" (#-后续计划)

---

✨ 项目功能

功能| 说明
📦 代码项目上传| 支持通过 ZIP 压缩包导入代码项目
🔍 代码文件过滤| 根据文件扩展名筛选支持处理的源代码文件
✂️ 代码切分| 使用 "RecursiveCharacterTextSplitter" 将源码拆分为适合检索的文本块
🧠 向量化存储| 使用 Embedding 模型生成代码向量，并存储到 PostgreSQL 的 pgvector 中
🔎 语义检索| 将用户问题转换为向量，检索当前项目中语义相关的代码片段
💬 项目问答| 结合检索结果与大语言模型，根据代码上下文生成回答
🖥️ 可视化交互| 使用 Streamlit 提供项目上传、问题输入和回答展示界面

🛠️ 技术栈

技术| 用途
Python| 主要开发语言
FastAPI| 后端 API 服务
Streamlit| 前端交互界面
LangChain| 文本切分与模型集成
LangGraph| 编排代码问答流程
DeepSeek 兼容接口| 大语言模型调用
OpenAI-compatible Embedding API| 生成文本向量
PostgreSQL| 存储项目、文件及代码块数据
pgvector| 向量存储与相似度检索
Tortoise ORM| 异步数据库操作
Docker| 数据库及开发环境部署

🏗️ 系统架构

flowchart TD
    A[用户] --> B[Streamlit 前端]
    B -->|HTTP 请求| C[FastAPI 后端]

    C --> D[项目上传服务]
    D --> D1[ZIP 解压与文件过滤]
    D1 --> D2[源码切分]
    D2 --> D3[生成 Embedding]
    D3 --> D4[(PostgreSQL + pgvector)]

    C --> E[项目问答服务]
    E --> E1[生成查询向量]
    E1 --> E2[语义检索]
    E2 --> E3[整理代码上下文]
    E3 --> E4[LangGraph 工作流]
    E4 --> E5[大语言模型]
    E5 --> F[返回回答]
    F --> B

🔄 核心流程

1. 代码项目导入

1. 用户上传 ZIP 格式的代码项目。
2. 后端读取压缩包，并筛选支持的源代码文件。
3. 将项目、文件信息及源码保存到数据库。
4. 使用文本切分器将源码拆分为多个代码块。
5. 调用 Embedding 模型，为代码块生成向量。
6. 将代码块及其向量保存到数据库，供后续检索使用。

2. 基于 RAG 的代码问答

1. 用户输入问题，并指定目标项目。
2. Embedding 模型将问题转换为查询向量。
3. 后端通过 pgvector 检索语义相关的代码块。
4. 将检索到的代码片段整理为上下文。
5. LangGraph 组织问答流程，并调用大语言模型生成回答。
6. FastAPI 将回答返回给 Streamlit 前端。

📁 项目结构

📁 项目结构

CodeInsight/                     
├── app/       
│   ├──main.py           
│   ├── models.py            
│   ├── routers/         
│   │   ├── project.py           
│   │   ├── chat.py        
│   │   └── code_analyzer.py       
│   ├── services/        
│   │   ├── chunker.py        
│   │   ├── embedding.py        
│   │   └── deepseek_llm.py              
│   └── graph/         
│       └── code_graph.py        
├── frontend/           
│   └── app.py             
├── tests/           
├── .env.example           
├── .gitignore              
├── README.md            
└── requirements.txt

«注意： 以上目录结构为参考。提交前请根据实际项目核对文件位置，并删除不存在的文件或目录。»

💻 环境要求

- Python 3.13
- PostgreSQL
- 已启用 pgvector 扩展的 PostgreSQL 数据库
- 可访问的大语言模型 API
- 可访问的 Embedding API
- Docker（如果使用 Docker 启动数据库）

🚀 快速开始

1. 获取项目

git clone https://github.com/danlegeding/CodeInsight.git
cd CodeInsight

2. 创建 Python 环境

使用 Conda 创建并激活环境：

conda create -n CodeInsight python=3.13
conda activate CodeInsight

如果已有可用的 Python 环境，也可以直接使用。

3. 安装依赖

python -m pip install -r requirements.txt

4. 配置环境变量

在项目根目录创建 ".env" 文件，并根据实际使用的模型服务和数据库配置填写环境变量。

Embedding 服务使用的环境变量包括：

CLOSEAI_API_KEY=你的Embedding_API密钥
CLOSEAI_BASE_URL=你的Embedding_API地址

此外，还需要根据项目实际配置填写数据库连接信息，以及大语言模型所需的 API 密钥、接口地址和模型名称。

«⚠️ 安全提示： 请勿将包含真实 API Key、数据库密码等敏感信息的 ".env" 文件提交到 GitHub。»

5. 启动数据库

启动项目配置的 PostgreSQL 服务，并确保数据库已启用 pgvector 扩展。

如果项目使用 Docker Compose，在包含 "docker-compose.yml" 的目录下执行：

docker compose up -d

请根据实际 Compose 配置确认数据库服务名称、端口、账号和密码。

6. 启动后端

在项目根目录执行：

python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

后端启动后，可以通过以下地址查看交互式 API 文档：

"http://127.0.0.1:8000/docs" (http://127.0.0.1:8000/docs)

7. 启动前端

打开另一个终端，在项目根目录执行：

python -m streamlit run frontend/app.py

启动成功后，根据终端显示的 Local URL 打开前端页面。

默认情况下，前端请求的后端地址为：

http://127.0.0.1:8000

如果后端地址发生变化，请同步调整前端的 "CODEINSIGHT_API_URL" 配置。

🔌 API 接口

接口列表

请求方法| 接口路径| 功能
"POST"| "/projects/upload"| 上传并处理代码项目
"POST"| "/chat/"| 对指定项目进行自然语言问答
"GET"| "/docs"| 查看交互式 API 文档

项目问答示例

请求路径

POST /chat/

请求体

{
  "question": "这个项目的入口文件在哪里？",
  "project_id": 17
}

响应体

{
  "answer": "这里返回基于检索到的代码上下文生成的回答。"
}

其中，"project_id" 应替换为实际上传项目对应的 ID。

«以上请求和响应格式以当前接口设计为例，实际使用时请以 FastAPI 接口文档和后端代码为准。»

🧩 技术设计

为什么使用 RAG？

直接将整个代码项目交给大语言模型，会受到上下文长度、调用成本和信息相关性等因素限制。

本项目先将源码切分并建立向量索引，再根据用户问题检索相关代码片段，让模型基于更有针对性的上下文生成回答。

为什么使用 LangGraph？

LangGraph 用于组织问答流程中的状态和节点，使检索、上下文处理和回答生成等步骤具有明确的执行关系，同时为后续扩展多步骤代码分析能力提供基础。

为什么使用 PostgreSQL 和 pgvector？

PostgreSQL 可以统一存储项目、文件和代码块等结构化数据，pgvector 则提供向量存储和相似度检索能力。

对于当前项目规模，这种组合能够减少额外引入独立向量数据库带来的部署与维护成本。

🗺️ 后续计划

- [ ] 增加自动化测试，覆盖上传、切分、检索和问答流程。
- [ ] 优化检索结果的相关性，并评估不同检索策略的效果。
- [ ] 支持更多编程语言和代码文件类型。
- [ ] 改进跨文件调用关系分析能力。
- [ ] 在前端展示检索结果对应的文件路径和代码行号。
- [ ] 完善 Docker Compose 部署流程和项目使用文档。

📌 项目说明

CodeInsight 是一个用于学习和实践 AI 应用开发的项目，主要探索大语言模型、Embedding、RAG、向量检索与工作流编排在代码理解场景中的应用。

项目重点是构建从代码导入、索引建立到语义检索与问答的完整应用流程。
