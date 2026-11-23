
from pydantic import ValidationError

from schemas import TaskExtractionResult

# 一份模拟的 AI 返回结果
correct_json = """
{
    "meeting_topic": "道路改造工程协调会",
    "tasks": [
        {
            "description": "提交施工进度计划",
            "responsible_unit": "施工单位",
            "deadline": "本周五前",
            "source_excerpt": "施工单位应在本周五前提交施工进度计划"
        }
    ]
}
"""

# 使用 Pydantic 进行解析和验证
result = TaskExtractionResult.model_validate_json(
    correct_json
)

print("数据校验成功！")

# 获取第一条待办事项
print(result.tasks[0].description)
print(result.tasks[0].responsible_unit)
print(result.tasks[0].deadline)

# 再测试一份错误的数据
wrong_json = """
{
    "meeting_topic": "道路改造工程协调会",
    "tasks": "提交施工进度计划"
}
"""

try:
    TaskExtractionResult.model_validate_json(wrong_json)

except ValidationError as e:
    print("\n成功发现错误的数据结构！")
    print(e)