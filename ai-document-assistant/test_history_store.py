
import tempfile
import unittest

from pathlib import Path

from history_store import save_history, load_history


class HistoryStoreTests(unittest.TestCase):

    def setUp(self):

        # 创建临时测试目录
        self.tmp = tempfile.TemporaryDirectory()
        self.folder = Path(self.tmp.name)

    def tearDown(self):

        # 测试结束后清理临时目录
        self.tmp.cleanup()

    def test_save_and_load(self):

        # 模拟分析结果
        saved_result = {
            "kind": "structured",
            "data": {
                "meeting_topic": "道路改造协调会",
                "tasks": [
                    {
                        "description": "提交计划",
                        "responsible_unit": "施工单位",
                        "deadline": "周五前",
                        "source_excerpt": "施工单位应于周五前提交计划"
                    }
                ]
            }
        }

        # 保存历史记录
        path = save_history(
            source_filename="test.docx",
            task_name="待办事项提取",
            file_hash="abc123",
            saved_result=saved_result,
            output_dir=self.folder
        )

        # 检查文件是否存在
        self.assertTrue(path.exists())

        # 重新加载历史记录
        records, errors = load_history(
            output_dir=self.folder
        )

        # 验证加载结果
        self.assertEqual(errors, [])
        self.assertEqual(len(records), 1)

        deadline = records[0]["data"]["tasks"][0]["deadline"]

        self.assertEqual(deadline, "周五前")

    def test_invalid_json(self):

        # 主动制造一个损坏的 JSON 文件
        broken_file = self.folder / "analysis_broken.json"

        broken_file.write_text(
            "{invalid json",
            encoding="utf-8"
        )

        # 加载历史记录
        records, errors = load_history(
            output_dir=self.folder
        )

        # 不应该返回有效记录
        self.assertEqual(records, [])

        # 应该检测出一个错误文件
        self.assertEqual(len(errors), 1)


if __name__ == "__main__":
    unittest.main()
