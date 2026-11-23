
from pydantic import BaseModel, ConfigDict, Field


# 定义单条待办事项的数据结构
class MeetingTask(BaseModel):

    model_config = ConfigDict(extra="forbid")

    description: str = Field(
        min_length=1,
        description="具体工作事项"
    )

    responsible_unit: str = Field(
        min_length=1,
        description="责任单位，未明确时填写'未明确'"
    )

    deadline: str = Field(
        min_length=1,
        description="完成期限，未明确时填写'未明确'"
    )

    source_excerpt: str = Field(
        min_length=1,
        description="支持该事项的原文片段"
    )


# 定义整份文档的提取结果
class TaskExtractionResult(BaseModel):

    model_config = ConfigDict(extra="forbid")

    meeting_topic: str = Field(
        min_length=1,
        description="会议主题，未明确时填写'未明确'"
    )

    tasks: list[MeetingTask] = Field(
        description="提取到的待办事项列表，没有则返回空列表"
    )
