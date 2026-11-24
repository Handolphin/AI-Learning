
import json

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from schemas import TaskExtractionResult


# 默认历史记录保存目录
OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"


# ====================================
# 1. 保存分析记录
# ====================================

def save_history(
    source_filename,
    task_name,
    file_hash,
    saved_result,
    output_dir=None
):

    kind = saved_result["kind"]
    data = saved_result["data"]

    # 保存之前，再次校验数据
    if kind == "structured":
        data = TaskExtractionResult.model_validate(
            data
        ).model_dump()

    elif kind == "text":
        if not isinstance(data, str) or not data.strip():
            raise ValueError("文本分析结果无效")

    else:
        raise ValueError("不支持的分析结果类型")

    # 确定保存目录
    target_dir = (
        Path(output_dir)
        if output_dir is not None
        else OUTPUT_DIR
    )

    target_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    # 创建唯一记录编号
    record_id = (
        datetime.now(timezone.utc).strftime(
            "%Y%m%dT%H%M%S%fZ"
        )
        + "_" + uuid4().hex[:8]
    )

    # 组织完整的历史记录
    record = {
        "schema_version": 1,
        "source_filename": Path(source_filename).name,
        "task_name": task_name,
        "file_hash": file_hash,
        "saved_at": datetime.now(timezone.utc).isoformat(),
        "kind": kind,
        "data": data
    }

    # 写入 JSON 文件
    output_path = target_dir / f"analysis_{record_id}.json"

    output_path.write_text(
        json.dumps(
            record,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    return output_path


# ====================================
# 2. 读取历史记录
# ====================================

def load_history(output_dir=None):

    target_dir = (
        Path(output_dir)
        if output_dir is not None
        else OUTPUT_DIR
    )

    if not target_dir.exists():
        return [], []

    records = []
    errors = []

    # 查找历史记录并按照修改时间排序
    paths = sorted(
        target_dir.glob("analysis_*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )

    for path in paths:

        try:
            # 读取 JSON 文件
            record = json.loads(
                path.read_text(encoding="utf-8")
            )

            # 新版存储格式
            if "kind" in record and "data" in record:
                kind = record["kind"]
                data = record["data"]

            # 兼容之前项目保存的 JSON 格式
            else:
                kind = (
                    "structured"
                    if record["task_name"] == "待办事项提取"
                    else "text"
                )

                data = record["result"]

            # 验证历史数据
            if kind == "structured":
                data = TaskExtractionResult.model_validate(
                    data
                ).model_dump()

            elif kind == "text":
                if not isinstance(data, str) or not data.strip():
                    raise ValueError("文本记录内容无效")

            else:
                raise ValueError("记录类型不支持")

            records.append({
                "source_filename": record["source_filename"],
                "task_name": record["task_name"],
                "saved_at": record["saved_at"],
                "kind": kind,
                "data": data
            })

        except (OSError, ValueError, KeyError, TypeError) as e:

            # 单个文件错误，不影响其他历史记录
            errors.append(
                f"{path.name}: {type(e).__name__}"
            )

    return records, errors
