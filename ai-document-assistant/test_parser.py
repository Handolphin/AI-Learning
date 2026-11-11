
from pathlib import Path

# 从 document_parser 模块中导入文件读取函数
from document_parser import extract_text_from_file


# 1. 获取当前 Python 文件所在的目录
project_dir = Path(__file__).parent

# 2. 定位测试文件
test_file = project_dir / "test_files" / "test_meeting.pdf"

# 3. 读取文件的二进制内容
file_bytes = test_file.read_bytes()

# 4. 调用我们编写的文件读取函数
extracted_text = extract_text_from_file(
    file_name=test_file.name,
    file_bytes=file_bytes
)

# 5. 输出提取结果
print("文件读取成功！")
print("-" * 40)
print(extracted_text)
print("-" * 40)
