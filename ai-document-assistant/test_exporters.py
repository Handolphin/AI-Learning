
from pathlib import Path

from schemas import TaskExtractionResult
from exporters import (
    export_tasks_to_word,
    export_tasks_to_excel
)


# 1. 构造一份模拟的结构化数据
test_data = {
    "meeting_topic": "道路改造工程协调会",
    "tasks": [
        {
            "description": "完成路面铣刨",
            "responsible_unit": "施工单位",
            "deadline": "下周",
            "source_excerpt": "计划于下周完成路面铣刨工作"
        },
        {
            "description": "提交施工进度计划",
            "responsible_unit": "施工单位",
            "deadline": "本周五前",
            "source_excerpt": "施工单位在本周五前提交施工进度计划"
        }
    ]
}


# 2. 转换成 Pydantic 对象
result = TaskExtractionResult.model_validate(test_data)


# 3. 创建输出文件夹
output_dir = Path(__file__).parent / "outputs"
output_dir.mkdir(exist_ok=True)


# 4. 生成 Word
word_bytes = export_tasks_to_word(
    result,
    source_name="test_meeting.docx"
)

word_path = output_dir / "test_tasks.docx"
word_path.write_bytes(word_bytes)


# 5. 生成 Excel
excel_bytes = export_tasks_to_excel(
    result,
    source_name="test_meeting.docx"
)

excel_path = output_dir / "test_tasks.xlsx"
excel_path.write_bytes(excel_bytes)


print("Word 导出成功：", word_path)
print("Excel 导出成功：", excel_path)
