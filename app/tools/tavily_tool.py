"""
Tavily 网络搜索工具模块
"""

import os
import traceback
from typing import Literal
from dotenv import load_dotenv
from langchain_core.tools import tool
from tavily import TavilyClient

from app.api.monitor import monitor
from app.utils.logger import logger  # 导入日志

load_dotenv()

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


@tool
def internet_search(
    query: str,
    topic: Literal["news", "finance", "general"] = "general",
    max_results: int = 5,
    include_raw_content: bool = False,
):
    """根据用户问题检索互联网公开信息"""
    tool_logger = logger.bind(tool_name="internet_search", query=query, topic=topic)
    tool_logger.info(f"开始网络搜索: {query}")
    monitor.report_tool(
        tool_name="网络搜索工具",
        args={
            "query": query,
            "topic": topic,
            "max_results": max_results,
            "include_raw_content": include_raw_content,
        },
    )

    try:
        result = tavily_client.search(
            query=query,
            topic=topic,
            max_results=max_results,
            include_raw_content=include_raw_content,
        )
        result_count = len(result.get("results", []))
        tool_logger.info(f"搜索完成，返回 {result_count} 条结果")
        return result
    except Exception as e:
        tool_logger.error(f"网络搜索失败: {e}\n{traceback.format_exc()}")
        raise  # 让上层处理


if __name__ == "__main__":
    # 本地调试不变
    ...