"""
Markdown 转 PDF 工具
"""

import logging
import traceback
from pathlib import Path
try:
    from typing import Annotated, Optional
except ImportError:
    from typing_extensions import Annotated, Optional

from langchain_core.tools import tool

from app.api.context import get_session_context
from app.api.monitor import monitor
from app.utils.path_utils import resolve_path
from app.utils.word_converter import convert_md_to_pdf as convert_md_to_pdf_via_word
from app.utils.logger import logger  # 导入日志


@tool
def convert_md_to_pdf(
    md_filename: Annotated[str, "要转换的Markdown文档路径（包含.md后缀）"],
    pdf_filename: Annotated[
        Optional[str], "输出的PDF文件路径（可选，默认与源文件同名）"
    ] = None,
) -> str:
    """将当前会话目录中的 Markdown 文档转换为 PDF"""
    tool_logger = logger.bind(tool_name="convert_md_to_pdf", md_filename=md_filename, pdf_filename=pdf_filename)
    tool_logger.info("开始转换Markdown到PDF")
    monitor.report_tool("Markdown转PDF工具")

    try:
        session_dir = get_session_context()
        md_path = Path(md_filename).with_suffix(".md")
        md_abs_path = Path(resolve_path(str(md_path), session_dir))
        tool_logger.debug(f"Markdown绝对路径: {md_abs_path}")

        if not md_abs_path.exists():
            tool_logger.warning(f"Markdown文件不存在: {md_abs_path}")
            return f"错误：文件不存在 {md_abs_path}"

        if pdf_filename:
            pdf_path = Path(pdf_filename).with_suffix(".pdf")
            pdf_abs_path = Path(resolve_path(str(pdf_path), session_dir))
        else:
            pdf_abs_path = md_abs_path.with_suffix(".pdf")
        tool_logger.debug(f"PDF输出路径: {pdf_abs_path}")

        result = convert_md_to_pdf_via_word(md_abs_path, pdf_abs_path)
        tool_logger.info(f"转换结果: {result}")
        return result
    except Exception as e:
        tool_logger.error(f"转换失败: {e}\n{traceback.format_exc()}")
        return f"转换失败: {str(e)}"


if __name__ == "__main__":
    # 本地调试不变
    ...