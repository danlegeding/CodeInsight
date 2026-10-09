
import os
import requests
import streamlit as st

# =========================
# 1. 页面配置
# =========================

st.set_page_config(
    page_title="CodeInsight | AI Code Intelligence",
    page_icon="⌘",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_BASE_URL = os.getenv(
    "CODEINSIGHT_API_URL",
    "http://127.0.0.1:8000",
).rstrip("/")


# =========================
# 2. 页面样式
# =========================

st.markdown(
    """
    <style>
    @import url(
      'https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Inter:wght@400;500;600;700;800&display=swap'
    );

    .stApp {
        background:
            radial-gradient(ellipse at 10% 0%,
            rgba(79, 70, 229, 0.13), transparent 38%),
            #0b0d12;
        color: #e8eaf0;
        font-family: 'Inter', sans-serif;
    }

    [data-testid="stSidebar"] {
        background: #10131a;
        border-right: 1px solid #242936;
    }

    .hero {
        padding: 24px 0 22px 0;
        border-bottom: 1px solid #242936;
        margin-bottom: 24px;
    }

    .eyebrow {
        color: #8b91ff;
        font-family: 'DM Mono', monospace;
        font-size: 11px;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    .hero h1 {
        color: #f5f6ff;
        font-size: clamp(30px, 4vw, 44px);
        font-weight: 800;
        letter-spacing: -1.8px;
        margin: 10px 0;
    }

    .hero p {
        color: #9299aa;
        font-size: 14px;
        line-height: 1.8;
        max-width: 680px;
    }

    .panel {
        background: rgba(19, 23, 33, 0.88);
        border: 1px solid #282e3c;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 16px;
    }

    .panel-title {
        color: #f0f1f8;
        font-size: 16px;
        font-weight: 700;
        margin-bottom: 6px;
    }

    .muted {
        color: #9299aa;
        font-size: 12px;
        line-height: 1.7;
    }

    .tag {
        display: inline-block;
        color: #a5a8ff;
        background: #20223c;
        border: 1px solid #34365c;
        padding: 4px 9px;
        border-radius: 6px;
        font-size: 11px;
        font-family: 'DM Mono', monospace;
    }

    .stButton > button {
        border-radius: 9px;
        border: 1px solid #383c69;
        min-height: 42px;
        font-weight: 600;
        transition: all 0.2s ease;
    }

    .stButton > button[kind="primary"] {
        background: #6965f5;
        color: white;
        border: 1px solid #7773ff;
    }

    .stButton > button:hover {
        border-color: #8b87ff;
        color: white;
    }

    .stTextInput input,
    .stTextArea textarea {
        background: #11151e;
        border-color: #303646;
        border-radius: 9px;
    }

    [data-testid="stChatMessage"] {
        background: rgba(20, 24, 34, 0.85);
        border: 1px solid #272d3b;
        border-radius: 13px;
        padding: 12px;
        margin-bottom: 12px;
    }

    [data-testid="stFileUploader"] {
        background: #11151e;
        border: 1px dashed #414763;
        border-radius: 12px;
        padding: 12px;
    }

    hr {
        border-color: #282e3c;
    }

    footer {
        visibility: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================
# 3. 会话状态
# =========================

if "projects" not in st.session_state:
    st.session_state.projects = {}

if "messages" not in st.session_state:
    st.session_state.messages = {}

if "active_project_id" not in st.session_state:
    st.session_state.active_project_id = None


# =========================
# 4. API 辅助函数
# =========================

def api_error_message(response):
    """尽量从后端错误响应中提取可读信息。"""
    try:
        data = response.json()
        if isinstance(data, dict):
            return data.get(
                "message",
                data.get("detail", response.text[:500]),
            )
        return str(data)[:500]
    except (ValueError, requests.exceptions.JSONDecodeError):
        return response.text[:500] or "服务器返回了无法解析的响应。"


def extract_project_info(data, fallback_name):
    """
    兼容常见返回格式，例如：
    {"id": 1, "name": "..."}
    {"project_id": 1, "name": "..."}
    {"project": {"id": 1, "name": "..."}}
    """
    if not isinstance(data, dict):
        raise ValueError("上传接口返回的 JSON 格式不符合预期。")

    project_data = data.get("project", data)

    if not isinstance(project_data, dict):
        raise ValueError("没有从上传响应中读取到项目信息。")

    project_id = project_data.get(
        "project_id",
        project_data.get("id"),
    )

    if project_id is None:
        raise ValueError(
            "上传接口没有返回 project_id 或 id。"
            "请检查后端上传接口的返回结构。"
        )

    project_name = project_data.get(
        "name",
        project_data.get("project_name", fallback_name),
    )

    return str(project_id), str(project_name)


def upload_project(uploaded_file):
    """将 ZIP 文件交给现有 FastAPI 后端。"""
    url = f"{API_BASE_URL}/projects/upload"

    files = {
        "file": (
            uploaded_file.name,
            uploaded_file.getvalue(),
            "application/zip",
        )
    }

    try:
        response = requests.post(
            url,
            files=files,
            timeout=(10, 600),
        )

        if not response.ok:
            raise RuntimeError(
                f"上传失败（HTTP {response.status_code}）："
                f"{api_error_message(response)}"
            )

        try:
            data = response.json()
        except ValueError as exc:
            raise RuntimeError(
                "上传接口没有返回有效的 JSON，请检查后端响应。"
            ) from exc

        project_id, project_name = extract_project_info(
            data,
            uploaded_file.name,
        )

        return project_id, project_name

    except requests.Timeout as exc:
        raise RuntimeError(
            "上传等待超时。项目可能仍在处理中，请先检查后端日志，"
            "确认是否已经创建项目，避免重复上传。"
        ) from exc

    except requests.ConnectionError as exc:
        raise RuntimeError(
            f"无法连接后端：{API_BASE_URL}。"
            "请确认 FastAPI 已启动。"
        ) from exc


def ask_code_question(question, project_id):
    """调用已有的 LangGraph 问答接口。"""
    url = f"{API_BASE_URL}/chat/"

    try:
        response = requests.post(
            url,
            json={
                "question": question,
                "project_id": int(project_id),
            },
            timeout=(10, 180),
        )

        if not response.ok:
            raise RuntimeError(
                f"问答失败（HTTP {response.status_code}）："
                f"{api_error_message(response)}"
            )

        data = response.json()
        answer = data.get("answer")

        if not isinstance(answer, str):
            raise RuntimeError("后端响应中没有有效的 answer 字段。")

        return answer

    except requests.Timeout as exc:
        raise RuntimeError(
            "AI 回答等待超时，请检查后端模型服务及日志。"
        ) from exc

    except requests.ConnectionError as exc:
        raise RuntimeError(
            f"无法连接后端：{API_BASE_URL}。"
            "请确认 FastAPI 已启动。"
        ) from exc


# =========================
# 5. 侧边栏
# =========================

with st.sidebar:
    st.markdown(
        """
        <div style="padding:12px 0 20px 0;">
            <div style="font-size:30px;font-weight:800;letter-spacing:-1px;">
                ⌘ CodeInsight
            </div>
            <div class="muted">AI CODE INTELLIGENCE</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("#### 工作空间")

    st.caption("后端 API 地址")
    st.code(API_BASE_URL, language=None)

    if st.button("＋ 上传新项目", use_container_width=True):
        st.session_state.show_uploader = True

    projects = st.session_state.projects

    if projects:
        project_ids = list(projects.keys())

        selected_id = st.selectbox(
            "当前项目",
            options=project_ids,
            index=(
                project_ids.index(st.session_state.active_project_id)
                if st.session_state.active_project_id in project_ids
                else 0
            ),
            format_func=lambda pid: (
                f'{projects[pid]["name"]}  ·  #{pid}'
            ),
        )

        if selected_id != st.session_state.active_project_id:
            st.session_state.active_project_id = selected_id

        if st.button("清空当前对话", use_container_width=True):
            st.session_state.messages[selected_id] = []
            st.rerun()

        st.markdown("---")
        st.markdown("#### 项目信息")

        current_project = projects[selected_id]

        st.markdown(
            f"""
            <div class="panel">
                <div class="muted">PROJECT ID</div>
                <div style="font-family:'DM Mono',monospace;
                            font-size:24px;color:#aaa7ff;margin:6px 0 12px;">
                    #{selected_id}
                </div>
                <div class="muted">PROJECT NAME</div>
                <div style="font-weight:600;word-break:break-word;">
                    {current_project["name"]}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.info("还没有项目，请先上传 ZIP 压缩包。")

    st.markdown("---")
    st.markdown(
        """
        <div class="muted">
            POWERED BY<br>
            FastAPI · LangGraph · PostgreSQL<br><br>
            CodeInsight v0.1.0
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================
# 6. 主页面标题
# =========================

st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">YOUR CODEBASE, UNDERSTOOD</div>
        <h1>Understand code.<br>Think beyond files.</h1>
        <p>
            上传你的代码项目，探索代码结构、理解核心逻辑，
            通过自然语言与整个代码库进行对话。
        </p>
        <span class="tag">AI CODE ANALYSIS</span>
        &nbsp;
        <span class="tag">PROJECT Q&A</span>
        &nbsp;
        <span class="tag">RAG</span>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================
# 7. 项目上传
# =========================

show_uploader = (
    st.session_state.get("show_uploader", False)
    or not st.session_state.projects
)

if show_uploader:
    st.markdown(
        """
        <div class="panel">
            <div class="panel-title">01 / 导入代码项目</div>
            <div class="muted">
                选择 ZIP 压缩包，后端将负责文件解析、代码切分和向量化。
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "选择 ZIP 文件",
        type=["zip"],
        help="请选择包含项目源码的 ZIP 压缩包。",
        key="project_zip_uploader",
    )

    if uploaded_file:
        st.caption(
            f"文件：{uploaded_file.name} · "
            f"{uploaded_file.size / 1024:.1f} KB"
        )

        if st.button(
            "开始分析项目 →",
            type="primary",
            use_container_width=True,
        ):
            try:
                with st.spinner(
                    "正在上传并处理项目，请稍候……"
                ):
                    project_id, project_name = upload_project(
                        uploaded_file
                    )

                st.session_state.projects[project_id] = {
                    "name": project_name,
                }
                st.session_state.messages.setdefault(project_id, [])
                st.session_state.active_project_id = project_id
                st.session_state.show_uploader = False

                st.success(
                    f"项目已接入：{project_name}（ID: {project_id}）"
                )
                st.rerun()

            except (RuntimeError, ValueError) as exc:
                st.error(str(exc))

    st.markdown("---")


# =========================
# 8. 项目问答
# =========================

if not st.session_state.projects:
    st.markdown(
        """
        <div class="panel" style="text-align:center;padding:48px 20px;">
            <div style="font-size:44px;">⌘</div>
            <div class="panel-title" style="font-size:20px;">
                你的代码工作空间已准备就绪
            </div>
            <div class="muted">
                上传第一个项目，开始探索代码。
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

else:
    project_id = st.session_state.active_project_id
    project = st.session_state.projects[project_id]

    st.markdown(
        f"""
        <div class="panel">
            <div class="panel-title">02 / 项目对话</div>
            <div class="muted">
                当前项目：{project["name"]} · ID #{project_id}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 示例问题
    st.markdown("##### 从这些问题开始")

    suggestions = [
        "这个项目的核心功能是什么？",
        "请梳理项目的整体架构。",
        "核心业务流程是怎样的？",
    ]

    cols = st.columns(len(suggestions))

    for index, suggestion in enumerate(suggestions):
        if cols[index].button(
            suggestion,
            key=f"suggestion_{index}",
            use_container_width=True,
        ):
            st.session_state.pending_question = suggestion
            st.rerun()

    messages = st.session_state.messages.setdefault(
        project_id,
        [],
    )

    # 显示历史对话
    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 获取用户问题
    pending_question = st.session_state.pop(
        "pending_question",
        None,
    )

    user_question = st.chat_input(
        "询问关于这个项目的任何问题……"
    )

    question = user_question or pending_question

    if question:
        messages.append(
            {
                "role": "user",
                "content": question,
            }
        )

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            try:
                with st.spinner("正在检索代码并生成回答……"):
                    answer = ask_code_question(
                        question,
                        project_id,
                    )

                st.markdown(answer)

                messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                    }
                )

            except (RuntimeError, ValueError) as exc:
                error_message = str(exc)
                st.error(error_message)

                messages.append(
                    {
                        "role": "assistant",
                        "content": f"请求失败：{error_message}",
                    }
                )
