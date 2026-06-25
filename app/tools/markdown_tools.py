"""
Markdown 文件生成工具
"""

import traceback
from pathlib import Path
try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated
from langchain_core.tools import tool

from app.api.context import get_session_context
from app.api.monitor import monitor
from app.utils.path_utils import resolve_path
from app.utils.logger import logger  # 导入日志


@tool
def generate_markdown(
    content: Annotated[str, "要写入Markdown文档的文本内容"],
    filename: Annotated[str, "Markdown文档的文件名（不包含扩展名或包含.md）"],
    path: Annotated[str, "文件保存的绝对路径"] = "",
):
    """根据提供的文本内容生成 Markdown 文件"""
    tool_logger = logger.bind(tool_name="generate_markdown", filename=filename, path=path)
    tool_logger.info("开始生成Markdown文件")
    monitor.report_tool("Markdown文档生成工具", {"写入的文本内容": content})

    if not filename.endswith(".md"):
        filename += ".md"

    session_dir = get_session_context()
    tool_logger.debug(f"当前会话目录: {session_dir}")

    if path and path != ".":
        full_input_path = str(Path(path) / filename)
    else:
        full_input_path = filename

    full_path_str = resolve_path(full_input_path, session_dir)
    file_path = Path(full_path_str)
    parent_dir = file_path.parent

    try:
        if not parent_dir.exists():
            parent_dir.mkdir(parents=True, exist_ok=True)
            tool_logger.debug(f"创建目录: {parent_dir}")

        file_path.write_text(content, encoding="utf-8")
        tool_logger.info(f"Markdown文件生成成功: {file_path}")
        return f"Markdown文件 '{file_path}' 已成功生成并保存。"
    except Exception as e:
        tool_logger.error(f"生成Markdown失败: {e}\n{traceback.format_exc()}")
        return f"生成Markdown文件失败: {str(e)}"


if __name__ == "__main__":
    # 本地调试不变
    def get_session_context():
        return "./examples/test_docs"
    # ...（略）