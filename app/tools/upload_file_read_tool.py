"""
上传文件读取工具
"""

import traceback
from pathlib import Path
from typing import Annotated
from langchain_core.tools import tool

from app.api.context import get_session_context
from app.api.monitor import monitor
from app.utils.path_utils import resolve_path
from app.utils.logger import logger  # 导入日志

try:
    import docx
except ImportError:
    docx = None

try:
    import pypdf
except ImportError:
    pypdf = None

try:
    import pandas as pd
except ImportError:
    pd = None


@tool
def read_file_content(
    filename: Annotated[
        str, "要读取的文件名或路径（支持 .md, .docx, .pdf, .xlsx, .xls）"
    ],
    instruction: Annotated[
        str, "对提取内容的具体指令（例如：'提取摘要', '统计数据'）"
    ] = "提取全部内容",
) -> str:
    """读取当前会话目录中的指定文件内容"""
    tool_logger = logger.bind(tool_name="read_file_content", filename=filename)
    tool_logger.info(f"开始读取文件: {filename} (指令: {instruction})")
    monitor.report_tool(
        "文件内容读取工具", {"filename": filename, "instruction": instruction}
    )

    session_dir = get_session_context()
    file_path = Path(resolve_path(filename, session_dir))
    tool_logger.debug(f"解析后的绝对路径: {file_path}")

    if not file_path.exists():
        tool_logger.warning(f"文件不存在: {file_path}")
        return f"错误：文件 '{filename}' 不存在 (解析路径: {file_path})。"

    ext = file_path.suffix.lower()
    try:
        if ext in [".md", ".txt"]:
            content = file_path.read_text(encoding="utf-8")
            tool_logger.info(f"文本文件读取成功，长度: {len(content)} 字符")
            return content

        elif ext == ".docx":
            if docx is None:
                tool_logger.error("未安装 python-docx")
                return "错误：未安装 'python-docx' 库，无法读取 Word 文件。"
            doc = docx.Document(str(file_path))
            full_text = [para.text for para in doc.paragraphs]
            content = "\n".join(full_text)
            tool_logger.info(f"Word文件读取成功，段落数: {len(full_text)}")
            return content

        elif ext == ".pdf":
            if pypdf is None:
                tool_logger.error("未安装 pypdf")
                return "错误：未安装 'pypdf' 库，无法读取 PDF 文件。"
            reader = pypdf.PdfReader(str(file_path))
            text = "\n".join([page.extract_text() or "" for page in reader.pages])
            tool_logger.info(f"PDF文件读取成功，页数: {len(reader.pages)}")
            return text

        elif ext in [".xlsx", ".xls"]:
            if pd is None:
                tool_logger.error("未安装 pandas")
                return "错误：未安装 'pandas' 库，无法读取 Excel 文件。"
            try:
                df = pd.read_excel(str(file_path))
            except Exception as e:
                tool_logger.error(f"读取Excel失败: {e}")
                return f"读取 Excel 失败: {str(e)}"
            result = [
                f"文件: {filename}",
                f"行数: {len(df)}, 列数: {len(df.columns)}",
                f"列名: {', '.join(df.columns.astype(str))}",
                "\n[前5行数据预览]:",
                df.head().to_string(index=False),
                "\n[统计描述]:",
                df.describe().to_string(),
            ]
            tool_logger.info(f"Excel读取成功，行数: {len(df)}")
            return "\n".join(result)

        else:
            try:
                content = file_path.read_text(encoding="utf-8")
                tool_logger.info(f"未知格式文件作为文本读取成功，长度: {len(content)}")
                return content
            except UnicodeDecodeError:
                tool_logger.error(f"不支持的文件格式且无法作为文本读取: {ext}")
                return f"错误：不支持的文件格式 '{ext}'，且无法作为文本读取。"
    except Exception as e:
        tool_logger.error(f"读取文件出错: {e}\n{traceback.format_exc()}")
        return f"读取文件出错: {str(e)}"


if __name__ == "__main__":
    # 本地调试不变
    ...