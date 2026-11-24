
import hashlib
import json

from datetime import datetime
from pathlib import Path

import streamlit as st

from document_parser import extract_text_from_file
from ai_analyzer import (
    analyze_document,
    extract_tasks_structured
)
from prompts import TASK_PROMPTS
from schemas import TaskExtractionResult
from exporters import (
    export_tasks_to_word,
    export_tasks_to_excel
)
from history_store import save_history, load_history

# ======================================
# 1. 网页设置
# ======================================

st.set_page_config(
    page_title="AI 智能文档处理助手",
    page_icon="📄",
    layout="wide"
)


# ======================================
# 侧边栏：选择页面
# ======================================

page = st.sidebar.radio(
    "功能导航",
    ["新建分析", "历史记录"]
)


# ======================================
# 历史记录页面
# ======================================

if page == "历史记录":

    st.title("🗂️ 历史分析记录")

    # 从磁盘读取记录
    records, errors = load_history()

    # 如果存在损坏文件，显示提示
    if errors:
        st.warning(
            f"有 {len(errors)} 份历史记录无法读取。"
        )

        with st.expander("查看读取错误"):
            for error in errors:
                st.write(error)

    # 没有历史记录
    if not records:
        st.info("暂时没有可读取的历史记录。")
        st.stop()

    st.write(f"已找到 {len(records)} 份历史记录。")

    # 选择某一份历史记录
    selected_index = st.selectbox(
        "请选择要查看的记录",
        options=range(len(records)),
        format_func=lambda i: (
            f"{records[i]['saved_at'][:19]} | "
            f"{records[i]['source_filename']} | "
            f"{records[i]['task_name']}"
        )
    )

    selected_record = records[selected_index]

    st.write(
        f"**来源文件：** "
        f"{selected_record['source_filename']}"
    )

    st.write(
        f"**分析任务：** "
        f"{selected_record['task_name']}"
    )

    st.write(
        f"**保存时间：** "
        f"{selected_record['saved_at']}"
    )

    st.divider()

    # 结构化结果
    if selected_record["kind"] == "structured":

        result = TaskExtractionResult.model_validate(
            selected_record["data"]
        )

        st.subheader("待办事项分析结果")

        st.write(
            f"**会议主题：** {result.meeting_topic}"
        )

        table_data = []

        for task in result.tasks:
            table_data.append({
                "工作事项": task.description,
                "责任单位": task.responsible_unit,
                "完成期限": task.deadline,
                "原文依据": task.source_excerpt
            })

        if table_data:
            st.dataframe(
                table_data,
                hide_index=True
            )
        else:
            st.info("该记录没有明确的待办事项。")

        # 重新导出 Word 和 Excel
        word_bytes = export_tasks_to_word(
            result,
            selected_record["source_filename"]
        )

        excel_bytes = export_tasks_to_excel(
            result,
            selected_record["source_filename"]
        )

        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                "📄 重新下载 Word",
                data=word_bytes,
                file_name="history_tasks.docx",
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "wordprocessingml.document"
                ),
                on_click="ignore"
            )

        with col2:
            st.download_button(
                "📊 重新下载 Excel",
                data=excel_bytes,
                file_name="history_tasks.xlsx",
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                ),
                on_click="ignore"
            )

        with st.expander("查看原始 JSON"):
            st.json(result.model_dump())

    # 普通文本结果
    else:

        st.subheader("AI 分析结果")

        st.markdown(selected_record["data"])

    # 历史页面执行结束
    st.stop()


st.title("📄 AI 智能文档处理助手")

st.write(
    "上传 PDF 或 Word 文档，"
    "使用 DeepSeek 提取和分析文档信息。"
)


# ======================================
# 2. 初始化会话状态
# ======================================

if "analysis_history" not in st.session_state:
    st.session_state["analysis_history"] = {}


# ======================================
# 3. 上传文件
# ======================================

uploaded_file = st.file_uploader(
    "请选择需要分析的文件",
    type=["pdf", "docx"]
)

if uploaded_file is None:
    st.info("请先上传一份 PDF 或 Word 文档。")
    st.stop()


file_bytes = uploaded_file.getvalue()


# ======================================
# 4. 提取文档文字
# ======================================

try:
    extracted_text = extract_text_from_file(
        file_name=uploaded_file.name,
        file_bytes=file_bytes
    )

except Exception as e:
    st.error(f"文档读取失败：{e}")
    st.stop()


st.success(f"文件读取成功：{uploaded_file.name}")

with st.expander("📑 查看文档原文"):
    st.text_area(
        "提取的文字",
        value=extracted_text,
        height=250,
        disabled=True
    )


# ======================================
# 5. 选择分析任务
# ======================================

task_name = st.selectbox(
    "请选择分析任务",
    options=list(TASK_PROMPTS.keys())
)


# ======================================
# 6. 文件长度检查
# ======================================

if len(extracted_text) > 12000:
    st.warning("文档过长，本阶段请使用不超过12000字符的文档。")
    st.stop()


# ======================================
# 7. 生成结果唯一标识
# ======================================

file_hash = hashlib.sha256(file_bytes).hexdigest()

result_key = f"{file_hash}:{task_name}"


# ======================================
# 8. 调用 AI 模型
# ======================================

if st.button("🚀 开始 AI 分析", type="primary"):

    try:
        with st.spinner("DeepSeek 正在分析文档..."):

            if task_name == "待办事项提取":

                result = extract_tasks_structured(
                    extracted_text
                )

                # 保存成普通 Python 字典
                saved_data = {
                    "kind": "structured",
                    "data": result.model_dump()
                }

            else:

                result = analyze_document(
                    document_text=extracted_text,
                    task_name=task_name
                )

                saved_data = {
                    "kind": "text",
                    "data": result
                }

        # 保存到 Session State
        st.session_state["analysis_history"][result_key] = saved_data

        st.success("AI 分析已完成！")

    except Exception as e:
        st.error(f"AI 分析失败：{e}")


# ======================================
# 9. 读取已保存的分析结果
# ======================================

saved_result = st.session_state["analysis_history"].get(
    result_key
)

if saved_result is None:
    st.info("尚未分析当前文件和任务，请点击开始 AI 分析。")
    st.stop()


st.subheader("✅ AI 分析结果")


# ======================================
# 10. 展示结构化待办事项
# ======================================

if saved_result["kind"] == "structured":

    # 将字典重新转换为 Pydantic 对象
    result = TaskExtractionResult.model_validate(
        saved_result["data"]
    )

    st.write(f"**会议主题：** {result.meeting_topic}")

    if result.tasks:

        table_data = []

        for index, task in enumerate(result.tasks, start=1):

            table_data.append({
                "序号": index,
                "工作事项": task.description,
                "责任单位": task.responsible_unit,
                "完成期限": task.deadline,
                "原文依据": task.source_excerpt
            })

        st.dataframe(
            table_data,
            hide_index=True
        )

    else:
        st.info("文档中没有提取到明确的待办事项。")

    with st.expander("查看 JSON 数据"):
        st.json(result.model_dump())


    # ======================================
    # 11. 生成导出文件
    # ======================================

    word_bytes = export_tasks_to_word(
        result,
        uploaded_file.name
    )

    excel_bytes = export_tasks_to_excel(
        result,
        uploaded_file.name
    )

    json_bytes = result.model_dump_json(
        indent=2
    ).encode("utf-8")


    # ======================================
    # 12. 显示下载按钮
    # ======================================

    st.subheader("📥 导出分析结果")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.download_button(
            label="下载 Word",
            data=word_bytes,
            file_name="meeting_tasks.docx",
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
            on_click="ignore"
        )

    with col2:
        st.download_button(
            label="下载 Excel",
            data=excel_bytes,
            file_name="meeting_tasks.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            on_click="ignore"
        )

    with col3:
        st.download_button(
            label="下载 JSON",
            data=json_bytes,
            file_name="meeting_tasks.json",
            mime="application/json",
            on_click="ignore"
        )


# ======================================
# 14. 展示普通文本分析结果
# ======================================

else:
    st.markdown(saved_result["data"])

    st.info(
        "当前摘要和风险识别仍采用普通文本输出。"
        "Word、Excel 结构化导出暂时只支持待办事项提取。"
    )


# ======================================
# 保存当前分析结果
# ======================================

if st.button("💾 保存当前分析结果到历史记录"):

    try:

        output_path = save_history(
            source_filename=uploaded_file.name,
            task_name=task_name,
            file_hash=file_hash,
            saved_result=saved_result
        )

        st.success(
            f"分析结果已保存：{output_path.name}"
        )

    except Exception as e:

        st.error(
            f"历史记录保存失败：{e}"
        )
