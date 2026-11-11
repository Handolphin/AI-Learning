
from pathlib import Path
from io import BytesIO

import fitz
from docx import Document


def extract_text_from_file(file_name, file_bytes):
    """
    根据文件类型提取 PDF 或 Word 文档中的文字。

    参数：
        file_name: 文件名称，例如 meeting.pdf
        file_bytes: 文件的二进制内容

    返回：
        提取出来的文本字符串
    """

    # 1. 获取文件扩展名
    file_extension = Path(file_name).suffix.lower()

    # 2. 如果是 PDF 文件
    if file_extension == ".pdf":

        # 使用 PyMuPDF 打开 PDF
        pdf_document = fitz.open(
            stream=file_bytes,
            filetype="pdf"
        )

        # 创建一个列表，保存每一页提取的文字
        text_list = []

        # 遍历 PDF 中的每一页
        for page in pdf_document:
            page_text = page.get_text("text")
            text_list.append(page_text)

        # 关闭 PDF 文件
        pdf_document.close()

        # 将所有页面的文字合并
        full_text = "\n".join(text_list)

    # 3. 如果是 Word 文件
    elif file_extension == ".docx":

        # 将二进制文件转换成可供 python-docx 读取的对象
        word_document = Document(BytesIO(file_bytes))

        text_list = []

        # 提取 Word 中的普通段落
        for paragraph in word_document.paragraphs:
            if paragraph.text.strip():
                text_list.append(paragraph.text)

        # 提取 Word 中的表格内容
        for table in word_document.tables:
            for row in table.rows:
                row_text = [
                    cell.text.strip() for cell in row.cells
                ]
                text_list.append(" | ".join(row_text))

        # 合并所有文字
        full_text = "\n".join(text_list)

    # 4. 如果文件格式不支持
    else:
        raise ValueError("目前只支持 PDF 和 DOCX 文件")

    # 5. 检查是否成功提取文字
    full_text = full_text.strip()

    if not full_text:
        raise ValueError(
            "没有从文件中提取到文字，请检查文件是否为空或是否为扫描版 PDF"
        )

    # 6. 返回提取结果
    return full_text
