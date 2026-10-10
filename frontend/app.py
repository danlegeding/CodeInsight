
import html
import os
from pathlib import Path

import psycopg
import requests
import streamlit as st
from dotenv import load_dotenv

# =========================
# 1. 页面配置
# =========================

st.set_page_config(
    page_title="CodeInsight | AI Code Intelligence",
    page_icon="⌘",
    layout="wide",
    initial_sidebar_state="expanded",
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env", override=False)

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
      'https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Outfit:wght@400;500;600;700;800&display=swap'
    );

    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(1100px 520px at 6% -8%,
            rgba(139, 92, 246, 0.38), transparent 52%),
            radial-gradient(900px 460px at 100% 0%,
            rgba(34, 211, 238, 0.18), transparent 48%),
            radial-gradient(780px 380px at 80% 110%,
            rgba(244, 63, 94, 0.16), transparent 50%),
            linear-gradient(180deg, #06070d 0%, #0a1022 100%);
        color: #eef1ff;
    }

    .stApp::before {
        content: "";
        position: fixed;
        inset: 0;
        pointer-events: none;
        background-image:
            linear-gradient(rgba(167, 139, 250, 0.05) 1px, transparent 1px),
            linear-gradient(90deg, rgba(167, 139, 250, 0.05) 1px, transparent 1px);
        background-size: 42px 42px;
        mask-image: radial-gradient(ellipse at center, black 20%, transparent 78%);
        z-index: 0;
        animation: grid-shift 18s linear infinite;
    }

    @keyframes grid-shift {
        from { background-position: 0 0, 0 0; }
        to { background-position: 42px 42px, 42px 42px; }
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    .block-container {
        padding-top: 1.4rem;
        max-width: 1180px;
        position: relative;
        z-index: 1;
    }

    [data-testid="stSidebar"] {
        background:
            linear-gradient(180deg, rgba(18, 12, 40, 0.96), rgba(8, 10, 18, 0.98));
        border-right: 1px solid rgba(167, 139, 250, 0.18);
    }

    [data-testid="stSidebar"]::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 140px;
        background: radial-gradient(circle at 20% 0%,
            rgba(99, 102, 241, 0.35), transparent 70%);
        pointer-events: none;
    }

    .brand-mark {
        width: 46px;
        height: 46px;
        border-radius: 14px;
        display: grid;
        place-items: center;
        font-size: 22px;
        color: white;
        background: linear-gradient(135deg, #7c3aed, #22d3ee);
        box-shadow: 0 0 28px rgba(124, 58, 237, 0.55);
    }

    .hero {
        position: relative;
        overflow: hidden;
        padding: 28px 28px 26px;
        margin-bottom: 22px;
        border-radius: 24px;
        border: 1px solid rgba(196, 181, 253, 0.22);
        background:
            linear-gradient(180deg, rgba(24, 20, 48, 0.72), rgba(12, 14, 28, 0.82));
        box-shadow:
            0 20px 60px rgba(0, 0, 0, 0.35),
            inset 0 1px 0 rgba(255, 255, 255, 0.08);
    }

    .hero::after {
        content: "";
        position: absolute;
        width: 280px;
        height: 280px;
        right: -40px;
        top: -80px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(56, 189, 248, 0.28), transparent 68%);
        animation: glow-pulse 4.8s ease-in-out infinite;
    }

    @keyframes glow-pulse {
        0%, 100% { transform: scale(1); opacity: 0.7; }
        50% { transform: scale(1.12); opacity: 1; }
    }

    .eyebrow {
        color: #67e8f9;
        font-family: 'DM Mono', monospace;
        font-size: 12px;
        letter-spacing: 2.4px;
        text-transform: uppercase;
    }

    .hero h1 {
        font-size: clamp(32px, 5vw, 52px);
        font-weight: 800;
        letter-spacing: -2px;
        line-height: 1.05;
        margin: 12px 0 10px;
        background: linear-gradient(120deg, #ffffff 10%, #c4b5fd 48%, #67e8f9 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .hero p {
        color: #b7bed4;
        font-size: 15px;
        line-height: 1.8;
        max-width: 680px;
        margin-bottom: 16px;
    }

    .panel {
        position: relative;
        background: linear-gradient(180deg, rgba(22, 24, 42, 0.86), rgba(14, 16, 30, 0.9));
        border: 1px solid rgba(148, 163, 255, 0.16);
        border-radius: 18px;
        padding: 22px;
        margin-bottom: 16px;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.22);
        backdrop-filter: blur(16px);
    }

    .panel-title {
        color: #f8f7ff;
        font-size: 18px;
        font-weight: 700;
        margin-bottom: 6px;
    }

    .muted {
        color: #9aa3bf;
        font-size: 12px;
        line-height: 1.7;
    }

    .tag {
        display: inline-block;
        color: #e0e7ff;
        background: linear-gradient(180deg, rgba(99, 102, 241, 0.28), rgba(14, 18, 40, 0.7));
        border: 1px solid rgba(165, 180, 252, 0.35);
        padding: 5px 10px;
        border-radius: 999px;
        font-size: 11px;
        font-family: 'DM Mono', monospace;
        margin-right: 6px;
        box-shadow: 0 0 16px rgba(99, 102, 241, 0.18);
    }

    .stat-row {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 10px;
        margin-top: 8px;
    }

    .stat-card {
        padding: 12px 14px;
        border-radius: 14px;
        background: rgba(8, 10, 22, 0.55);
        border: 1px solid rgba(125, 211, 252, 0.16);
    }

    .stat-label {
        color: #8b95b7;
        font-size: 11px;
        letter-spacing: 1px;
        font-family: 'DM Mono', monospace;
    }

    .stat-value {
        color: #f4f6ff;
        font-size: 20px;
        font-weight: 700;
        margin-top: 4px;
        word-break: break-word;
    }

    .code-scroll {
        width: 100%;
        max-width: 100%;
        max-height: 464px;
        overflow-y: auto;
        overflow-x: auto;
        margin: 8px 0 18px;
        border-radius: 16px;
        border: 1px solid rgba(167, 139, 250, 0.22);
        background: rgba(10, 12, 24, 0.72);
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
    }

    .code-scroll table {
        width: 100%;
        min-width: 880px;
        border-collapse: collapse;
        table-layout: fixed;
    }

    .code-scroll thead th {
        position: sticky;
        top: 0;
        z-index: 1;
        background: #16182c;
        color: #c7d2fe;
        font-size: 12px;
        font-family: 'DM Mono', monospace;
        letter-spacing: 0.4px;
        text-align: left;
        padding: 12px 14px;
        height: 44px;
        border-bottom: 1px solid rgba(167, 139, 250, 0.22);
    }

    .code-scroll tbody td {
        color: #e8edff;
        font-size: 13px;
        padding: 0 14px;
        height: 42px;
        border-bottom: 1px solid rgba(148, 163, 255, 0.08);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        vertical-align: middle;
    }

    .code-scroll tbody tr:nth-child(even) td {
        background: rgba(124, 58, 237, 0.06);
    }

    .code-scroll .col-id { width: 110px; color: #c4b5fd; font-family: 'DM Mono', monospace; }
    .code-scroll .col-path { width: auto; }
    .code-scroll .col-lang { width: 110px; color: #67e8f9; font-family: 'DM Mono', monospace; }
    .code-scroll .col-line { width: 120px; color: #f472b6; font-family: 'DM Mono', monospace; }
    .code-scroll .col-chunk { width: 120px; font-family: 'DM Mono', monospace; }

    .id-chip {
        display: inline-block;
        margin: 0 6px 8px 0;
        padding: 4px 10px;
        border-radius: 999px;
        font-family: 'DM Mono', monospace;
        font-size: 12px;
        color: #e0f2fe;
        background: rgba(14, 165, 233, 0.16);
        border: 1px solid rgba(125, 211, 252, 0.28);
    }

    .result-card {
        border-radius: 16px;
        padding: 14px 16px;
        margin-bottom: 10px;
        border: 1px solid rgba(255,255,255,0.08);
    }

    .issue-high { background: rgba(244, 63, 94, 0.12); border-color: rgba(244, 63, 94, 0.35); }
    .issue-mid { background: rgba(245, 158, 11, 0.12); border-color: rgba(245, 158, 11, 0.35); }
    .issue-low { background: rgba(56, 189, 248, 0.12); border-color: rgba(56, 189, 248, 0.28); }
    .result-good { background: rgba(16, 185, 129, 0.12); border-color: rgba(52, 211, 153, 0.28); }
    .result-opt { background: rgba(139, 92, 246, 0.12); border-color: rgba(167, 139, 250, 0.3); }

    .stButton > button {
        border-radius: 12px;
        border: 1px solid rgba(196, 181, 253, 0.28);
        min-height: 44px;
        font-weight: 650;
        color: #eef2ff;
        background: rgba(24, 24, 48, 0.8);
        transition: all 0.2s ease;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #7c3aed, #2563eb 55%, #06b6d4);
        color: white;
        border: none;
        box-shadow: 0 8px 24px rgba(99, 102, 241, 0.35);
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        border-color: #67e8f9;
        color: white;
    }

    .stTextInput input,
    .stTextArea textarea,
    .stSelectbox [data-baseweb="select"] > div {
        background: #101422 !important;
        border-color: #303a5a !important;
        border-radius: 12px !important;
        color: #eef2ff !important;
    }

    [data-testid="stChatMessage"] {
        background: linear-gradient(180deg, rgba(24, 26, 48, 0.9), rgba(16, 18, 32, 0.92));
        border: 1px solid rgba(148, 163, 255, 0.16);
        border-radius: 16px;
        padding: 12px;
        margin-bottom: 12px;
    }

    [data-testid="stFileUploader"] {
        background: rgba(12, 16, 32, 0.7);
        border: 1px dashed rgba(103, 232, 249, 0.35);
        border-radius: 16px;
        padding: 14px;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(10, 12, 24, 0.72);
        border: 1px solid rgba(167, 139, 250, 0.16);
        border-radius: 16px;
        padding: 6px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        color: #b7bed4;
        font-weight: 650;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, rgba(124, 58, 237, 0.8), rgba(6, 182, 212, 0.7));
        color: white !important;
    }

    [data-testid="stDataFrame"] {
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid rgba(148, 163, 255, 0.14);
    }

    hr {
        border-color: rgba(148, 163, 255, 0.14);
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

if "projects_loaded" not in st.session_state:
    st.session_state.projects_loaded = False

if "projects_load_error" not in st.session_state:
    st.session_state.projects_load_error = None

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None


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


def to_psycopg_url(database_url):
    """把 Tortoise / asyncpg 连接串转成 psycopg 可用的 postgresql://。"""
    converted_url = database_url
    replacements = (
        ("postgresql+asyncpg://", "postgresql://"),
        ("postgres+asyncpg://", "postgresql://"),
        ("asyncpg://", "postgresql://"),
        ("postgres://", "postgresql://"),
    )
    for old_prefix, new_prefix in replacements:
        if converted_url.startswith(old_prefix):
            converted_url = new_prefix + converted_url[len(old_prefix):]
            break
    return converted_url


def fetch_database_projects():
    """只读查询数据库 project 表，展示已有项目的 name。"""
    database_url = os.getenv("DB_URL")
    if not database_url:
        raise RuntimeError("未找到 DB_URL，无法读取数据库中的项目名称。")

    connection_url = to_psycopg_url(database_url)
    query_candidates = (
        "SELECT id, name FROM project ORDER BY id DESC",
        'SELECT id, name FROM "project" ORDER BY id DESC',
    )

    last_error = None
    with psycopg.connect(connection_url) as connection:
        with connection.cursor() as cursor:
            for sql in query_candidates:
                try:
                    cursor.execute(sql)
                    rows = cursor.fetchall()
                    return {
                        str(project_id): {"name": project_name}
                        for project_id, project_name in rows
                    }
                except psycopg.Error as exc:
                    last_error = exc
                    connection.rollback()

    raise RuntimeError(
        "读取项目表失败，请确认数据库中存在 project 表。"
    ) from last_error


def fetch_project_files_with_lines(project_id):
    """只读查询当前 project_id 下的 file_id，以及每个代码块的起止行。"""
    database_url = os.getenv("DB_URL")
    if not database_url:
        raise RuntimeError("未找到 DB_URL，无法读取该项目下的文件。")

    connection_url = to_psycopg_url(database_url)
    query_candidates = (
        """
        SELECT
            f.id,
            f.path,
            f.language,
            c.chunk_index,
            c.start_line,
            c.end_line
        FROM codefile AS f
        LEFT JOIN codechunk AS c ON c.file_id = f.id
        WHERE f.project_id = %s
        ORDER BY f.id, c.chunk_index
        """,
        """
        SELECT
            f.id,
            f.path,
            f.language,
            c.chunk_index,
            c.start_line,
            c.end_line
        FROM "codefile" AS f
        LEFT JOIN "codechunk" AS c ON c.file_id = f.id
        WHERE f.project_id = %s
        ORDER BY f.id, c.chunk_index
        """,
    )

    last_error = None
    with psycopg.connect(connection_url) as connection:
        with connection.cursor() as cursor:
            for sql in query_candidates:
                try:
                    cursor.execute(sql, (int(project_id),))
                    rows = cursor.fetchall()
                    files_by_id = {}
                    chunk_rows = []

                    for (
                        file_id,
                        file_path,
                        language,
                        chunk_index,
                        start_line,
                        end_line,
                    ) in rows:
                        file_key = str(file_id)
                        if file_key not in files_by_id:
                            files_by_id[file_key] = {
                                "file_id": int(file_id),
                                "path": file_path,
                                "language": language or "",
                                "start_line": start_line,
                                "end_line": end_line,
                            }

                        current_file = files_by_id[file_key]
                        if start_line is not None:
                            if current_file["start_line"] is None:
                                current_file["start_line"] = start_line
                            else:
                                current_file["start_line"] = min(
                                    current_file["start_line"],
                                    start_line,
                                )
                        if end_line is not None:
                            if current_file["end_line"] is None:
                                current_file["end_line"] = end_line
                            else:
                                current_file["end_line"] = max(
                                    current_file["end_line"],
                                    end_line,
                                )

                        chunk_rows.append(
                            {
                                "file_id": int(file_id),
                                "path": file_path,
                                "language": language or "",
                                "chunk_index": chunk_index,
                                "start_line": start_line,
                                "end_line": end_line,
                            }
                        )

                    return list(files_by_id.values()), chunk_rows
                except psycopg.Error as exc:
                    last_error = exc
                    connection.rollback()

    raise RuntimeError(
        "读取项目文件失败，请确认数据库中存在 codefile 和 codechunk 表。"
    ) from last_error


def extract_project_info(data, fallback_name):
    """
    兼容上传接口返回：
    {"project_id": 1, "filename": "..."}
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
        "filename",
        project_data.get(
            "name",
            project_data.get("project_name", fallback_name),
        ),
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


def analyze_code_file(file_id):
    """调用已有的代码分析接口 POST /analysis/。"""
    url = f"{API_BASE_URL}/analysis/"

    try:
        response = requests.post(
            url,
            json={"file_id": int(file_id)},
            timeout=(10, 180),
        )

        if not response.ok:
            raise RuntimeError(
                f"代码分析失败（HTTP {response.status_code}）："
                f"{api_error_message(response)}"
            )

        data = response.json()
        if not isinstance(data, dict):
            raise RuntimeError("代码分析接口没有返回有效的结果对象。")

        return data

    except requests.Timeout as exc:
        raise RuntimeError(
            "代码分析等待超时，请检查后端模型服务及日志。"
        ) from exc

    except requests.ConnectionError as exc:
        raise RuntimeError(
            f"无法连接后端：{API_BASE_URL}。"
            "请确认 FastAPI 已启动。"
        ) from exc


def load_projects_from_database(force_reload=False):
    """把数据库里的项目名称同步到侧边栏。"""
    if st.session_state.projects_loaded and not force_reload:
        return

    try:
        database_projects = fetch_database_projects()
        st.session_state.projects = database_projects
        st.session_state.projects_load_error = None
        st.session_state.projects_loaded = True

        if database_projects:
            if st.session_state.active_project_id not in database_projects:
                st.session_state.active_project_id = next(
                    iter(database_projects)
                )
        else:
            st.session_state.active_project_id = None

    except (RuntimeError, psycopg.Error, OSError) as exc:
        st.session_state.projects_load_error = str(exc)
        st.session_state.projects_loaded = True


load_projects_from_database()


def render_scroll_table(headers, rows):
    header_cells = "".join(
        f'<th class="{css_class}">{html.escape(title)}</th>'
        for title, css_class in headers
    )
    body_rows = []
    for row in rows:
        cells = []
        for value, css_class in row:
            display_value = "—" if value is None else str(value)
            escaped_value = html.escape(display_value)
            cells.append(
                f'<td class="{css_class}" title="{escaped_value}">'
                f"{escaped_value}</td>"
            )
        body_rows.append(f"<tr>{''.join(cells)}</tr>")

    return f"""
    <div class="code-scroll">
        <table>
            <thead><tr>{header_cells}</tr></thead>
            <tbody>{"".join(body_rows)}</tbody>
        </table>
    </div>
    """


def issue_level_class(level):
    level_text = str(level).lower()
    if level_text in {"error", "high", "critical", "严重"}:
        return "issue-high"
    if level_text in {"warning", "medium", "warn", "中等"}:
        return "issue-mid"
    return "issue-low"


# =========================
# 5. 侧边栏
# =========================

with st.sidebar:
    st.markdown(
        """
        <div style="padding:8px 0 18px 0;display:flex;gap:12px;align-items:center;">
            <div class="brand-mark">⌘</div>
            <div>
                <div style="font-size:26px;font-weight:800;letter-spacing:-1px;color:#f8f7ff;">
                    CodeInsight
                </div>
                <div class="muted">AI CODE INTELLIGENCE</div>
            </div>
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

    if st.button("刷新数据库项目", use_container_width=True):
        load_projects_from_database(force_reload=True)
        st.rerun()

    if st.session_state.projects_load_error:
        st.warning(st.session_state.projects_load_error)

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
                <div class="stat-row" style="grid-template-columns:1fr;">
                    <div class="stat-card">
                        <div class="stat-label">PROJECT ID</div>
                        <div class="stat-value" style="color:#c4b5fd;">#{selected_id}</div>
                    </div>
                    <div class="stat-card" style="margin-top:10px;">
                        <div class="stat-label">PROJECT NAME</div>
                        <div class="stat-value" style="font-size:16px;">
                            {html.escape(str(current_project["name"]))}
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.info("数据库中还没有项目，请先上传 ZIP 压缩包。")

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
            上传代码项目，探索结构、理解核心逻辑，
            用自然语言与整个代码库对话，并对指定文件做深度分析。
        </p>
        <span class="tag">AI CODE ANALYSIS</span>
        <span class="tag">PROJECT Q&A</span>
        <span class="tag">RAG</span>
        <span class="tag">LINE-AWARE</span>
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
                选择 ZIP 压缩包。后端会解析源码、切分代码块并完成向量化。
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

                st.session_state.messages.setdefault(project_id, [])
                st.session_state.active_project_id = project_id
                st.session_state.show_uploader = False
                load_projects_from_database(force_reload=True)
                st.session_state.projects[project_id] = {
                    "name": project_name,
                }

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
        <div class="panel" style="text-align:center;padding:58px 20px;">
            <div class="brand-mark" style="margin:0 auto 16px;width:64px;height:64px;font-size:30px;">⌘</div>
            <div class="panel-title" style="font-size:24px;">
                代码工作空间已就绪
            </div>
            <div class="muted">
                上传第一个项目，开始探索结构、问答与文件分析。
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

else:
    project_id = st.session_state.active_project_id
    project = st.session_state.projects[project_id]
    project_name = project["name"]

    chat_tab, analysis_tab = st.tabs(["✦  项目问答", "◈  代码分析"])

    with chat_tab:
        st.markdown(
            f"""
            <div class="panel">
                <div class="panel-title">02 / 项目对话</div>
                <div class="muted">
                    当前项目：{html.escape(str(project_name))} · ID #{project_id}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

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

        for message in messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

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

    with analysis_tab:
        st.markdown(
            f"""
            <div class="panel">
                <div class="panel-title">03 / 代码分析</div>
                <div class="muted">
                    当前项目：{html.escape(str(project_name))} · ID #{project_id}
                    <br>
                    卡片中的 file_id 均属于该 project_id，并标出 start_line / end_line。
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        try:
            project_files, chunk_rows = fetch_project_files_with_lines(
                project_id
            )
        except (RuntimeError, psycopg.Error, OSError, ValueError) as exc:
            project_files, chunk_rows = [], []
            st.error(str(exc))

        if not project_files:
            st.info("当前项目下没有可分析的代码文件。")
        else:
            file_chips = "".join(
                f'<span class="id-chip">file_id #{item["file_id"]}</span>'
                for item in project_files
            )
            st.markdown(
                f'<div style="margin:4px 0 12px;">{file_chips}</div>',
                unsafe_allow_html=True,
            )
            st.markdown("##### 项目文件")
            st.markdown(
                render_scroll_table(
                    [
                        ("file_id", "col-id"),
                        ("path", "col-path"),
                        ("language", "col-lang"),
                        ("start_line", "col-line"),
                        ("end_line", "col-line"),
                    ],
                    [
                        [
                            (item["file_id"], "col-id"),
                            (item["path"], "col-path"),
                            (item["language"], "col-lang"),
                            (item["start_line"], "col-line"),
                            (item["end_line"], "col-line"),
                        ]
                        for item in project_files
                    ],
                ),
                unsafe_allow_html=True,
            )

            st.markdown("##### 代码块起止行")
            st.markdown(
                render_scroll_table(
                    [
                        ("file_id", "col-id"),
                        ("path", "col-path"),
                        ("chunk_index", "col-chunk"),
                        ("start_line", "col-line"),
                        ("end_line", "col-line"),
                    ],
                    [
                        [
                            (item["file_id"], "col-id"),
                            (item["path"], "col-path"),
                            (item["chunk_index"], "col-chunk"),
                            (item["start_line"], "col-line"),
                            (item["end_line"], "col-line"),
                        ]
                        for item in chunk_rows
                    ],
                ),
                unsafe_allow_html=True,
            )

            file_ids = [item["file_id"] for item in project_files]
            path_by_file_id = {
                item["file_id"]: item["path"] for item in project_files
            }

            selected_file_id = st.selectbox(
                "选择要分析的 file_id",
                options=file_ids,
                format_func=lambda file_id: (
                    f"#{file_id}  ·  {path_by_file_id[file_id]}"
                ),
            )

            if st.button(
                "开始分析文件 →",
                type="primary",
                use_container_width=True,
                key="run_code_analysis",
            ):
                try:
                    with st.spinner("正在分析代码，请稍候……"):
                        st.session_state.analysis_result = analyze_code_file(
                            selected_file_id
                        )
                except (RuntimeError, ValueError) as exc:
                    st.session_state.analysis_result = None
                    st.error(str(exc))

        analysis_result = st.session_state.analysis_result
        if isinstance(analysis_result, dict):
            st.markdown("##### 分析摘要")
            st.markdown(
                f"""
                <div class="result-card result-opt">
                    {html.escape(str(analysis_result.get("summary", "没有返回摘要。")))}
                </div>
                """,
                unsafe_allow_html=True,
            )

            issues = analysis_result.get("issues") or []
            if issues:
                st.markdown("##### 问题")
                for issue in issues:
                    if not isinstance(issue, dict):
                        st.write(str(issue))
                        continue
                    level = issue.get("level", "info")
                    description = issue.get("description", "")
                    suggestion = issue.get("suggestion", "")
                    suggestion_html = (
                        f'<div class="muted" style="margin-top:6px;">建议：'
                        f"{html.escape(str(suggestion))}</div>"
                        if suggestion
                        else ""
                    )
                    st.markdown(
                        f"""
                        <div class="result-card {issue_level_class(level)}">
                            <strong>{html.escape(str(level))}</strong>
                            <div style="margin-top:6px;">
                                {html.escape(str(description))}
                            </div>
                            {suggestion_html}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            strengths = analysis_result.get("strengths") or []
            if strengths:
                st.markdown("##### 优点")
                for strength in strengths:
                    st.markdown(
                        f'<div class="result-card result-good">{html.escape(str(strength))}</div>',
                        unsafe_allow_html=True,
                    )

            optimizations = analysis_result.get("optimization") or []
            if optimizations:
                st.markdown("##### 优化建议")
                for optimization in optimizations:
                    st.markdown(
                        f'<div class="result-card result-opt">{html.escape(str(optimization))}</div>',
                        unsafe_allow_html=True,
                    )
