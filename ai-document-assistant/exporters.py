
from io import BytesIO

from docx import Document
from docx.shared import Pt
from docx.oxml.ns import qn

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment


# ======================================
# 1. 导出 Word
# ======================================

def export_tasks_to_word(result, source_name):

    # 创建一份新的 Word 文档
    doc = Document()

    # 设置中文字体
    normal = doc.styles["Normal"]
    normal.font.name = "Microsoft YaHei"
    normal.font.size = Pt(10)
    normal._element.rPr.rFonts.set(
        qn("w:eastAsia"), "Microsoft YaHei"
    )

    # 添加标题和基本信息
    doc.add_heading("会议待办事项清单", level=0)

    doc.add_paragraph(
        f"会议主题：{result.meeting_topic}"
    )

    doc.add_paragraph(
        f"来源文件：{source_name}"
    )

    doc.add_paragraph(
        f"提取任务数：{len(result.tasks)}"
    )

    # 创建待办事项表格
    if result.tasks:

        table = doc.add_table(rows=1, cols=5)
        table.style = "Table Grid"

        headers = [
            "序号",
            "工作事项",
            "责任单位",
            "完成期限",
            "原文依据"
        ]

        # 填写表头
        for cell, title in zip(table.rows[0].cells, headers):
            cell.text = title

        # 逐条填写待办事项
        for index, task in enumerate(result.tasks, start=1):

            cells = table.add_row().cells

            values = [
                str(index),
                task.description,
                task.responsible_unit,
                task.deadline,
                task.source_excerpt
            ]

            for cell, value in zip(cells, values):
                cell.text = value

    else:
        doc.add_paragraph("未提取到明确的待办事项。")

    doc.add_paragraph(
        "提示：本报告由 AI 辅助生成，请对照原文核实后使用。"
    )

    # 将 Word 文件写入内存
    output = BytesIO()
    doc.save(output)

    # 返回文件的二进制内容
    return output.getvalue()


# ======================================
# 2. 导出 Excel
# ======================================

def export_tasks_to_excel(result, source_name):

    # 创建 Excel 工作簿
    workbook = Workbook()

    # 获取默认工作表
    sheet = workbook.active
    sheet.title = "待办事项"

    # 标题
    sheet.merge_cells("A1:E1")
    sheet["A1"] = "会议待办事项清单"
    sheet["A1"].font = Font(size=16, bold=True)

    # 基本信息
    sheet.merge_cells("A2:E2")
    sheet["A2"] = f"会议主题：{result.meeting_topic}"

    sheet.merge_cells("A3:E3")
    sheet["A3"] = f"来源文件：{source_name}"

    # 表头
    headers = [
        "序号",
        "工作事项",
        "责任单位",
        "完成期限",
        "原文依据"
    ]

    sheet.append(headers)

    # 设置表头样式
    for cell in sheet[4]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(
            fill_type="solid",
            fgColor="2764A5"
        )
        cell.alignment = Alignment(
            horizontal="center",
            vertical="center"
        )

    # 写入待办事项
    for index, task in enumerate(result.tasks, start=1):

        sheet.append([
            index,
            task.description,
            task.responsible_unit,
            task.deadline,
            task.source_excerpt
        ])

        # AI 生成内容必须作为纯文本，而不是 Excel 公式
        for cell in sheet[sheet.max_row][1:]:
            cell.data_type = "s"
            cell.alignment = Alignment(
                vertical="top",
                wrap_text=True
            )

    # 设置列宽
    widths = {
        "A": 9,
        "B": 37,
        "C": 22,
        "D": 20,
        "E": 53
    }

    for col, width in widths.items():
        sheet.column_dimensions[col].width = width

    # 冻结表头并添加筛选
    sheet.freeze_panes = "B5"
    sheet.auto_filter.ref = (
        f"A4:E{max(sheet.max_row, 4)}"
    )

    sheet.row_dimensions[4].height = 24

    # 写入内存
    output = BytesIO()
    workbook.save(output)
    workbook.close()

    return output.getvalue()
