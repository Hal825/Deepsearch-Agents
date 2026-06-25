"""
RAGFlow 知识库工具模块
"""

import json
import traceback
from langchain_core.tools import tool
from ragflow_sdk import RAGFlow

from app.api.context import get_thread_context
from app.api.monitor import monitor
from app.ragflow.rag_config import _load_ragflow_env
from app.utils.logger import logger  # 导入日志

api_key, base_url = _load_ragflow_env()
ragflow_client = RAGFlow(api_key=api_key, base_url=base_url)


@tool
def get_assistant_list() -> str:
    """查询 RAGFlow 中有哪些聊天助手"""
    tool_logger = logger.bind(tool_name="get_assistant_list")
    tool_logger.info("开始查询RAGFlow助手列表")
    monitor.report_tool(tool_name="ragflow聊天助手列表查询工具：get_assistant_list")

    try:
        chat_list = ragflow_client.list_chats()
        if not chat_list:
            tool_logger.info("未找到任何助手")
            return "没有任何可用助手"

        count_chat_info = ""
        for chat in chat_list:
            dataset_names = getattr(chat, "kb_names", []) or []
            count_chat_info += f"助手名称:{chat.name};功能介绍：{chat.description}; 关联的知识库：{'、'.join(dataset_names)} \n"
        tool_logger.info(f"找到 {len(chat_list)} 个助手")
        result = count_chat_info
        logger.info(f"[RAGFlow] get_assistant_list 返回:\n{result}")
        return result
    except Exception as e:
        tool_logger.error(f"查询助手列表失败: {e}\n{traceback.format_exc()}")
        return f"查询助手信息异常，无可用助手,异常信息:{str(e)}"


@tool
def create_ask_delete(chat_name, question) -> str:
    """向某个 RAGFlow 聊天助手创建临时会话并提问"""
    tool_logger = logger.bind(tool_name="create_ask_delete", chat_name=chat_name)
    tool_logger.info(f"开始向RAGFlow助手 '{chat_name}' 提问: {question[:100]}...")
    monitor.report_tool(
        tool_name="ragflow提问助手工具：create_ask_delete",
        args={"chat_name": chat_name, "question": question},
    )

    try:
        chats = ragflow_client.list_chats(name=chat_name)
        if not chats:
            tool_logger.warning(f"未找到名为 '{chat_name}' 的助手")
            return f"提问失败，错误原因：未找到名为 '{chat_name}' 的助手"
        use_chat = chats[0]
        tool_logger.debug(f"选中助手ID: {use_chat.id}")

        session = use_chat.create_session(name="temp_session_ask")
        tool_logger.debug(f"创建临时会话: {session.id}")

        response = ragflow_client.post(
            f"/chats/{use_chat.id}/completions",
            {
                "messages": [{"role": "user", "content": question}],
                "stream": True,
                "session_id": session.id,
            },
            stream=True,
        )
        result = ""
        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue
            line = line.removeprefix("data:").strip()
            if line == "[DONE]":
                break
            data = json.loads(line)
            chunk_data = data.get("data")
            if not isinstance(chunk_data, dict):
                continue
            answer = chunk_data.get("answer")
            if answer:
                if answer.startswith(result):
                    result = answer
                elif not result.startswith(answer):
                    result += answer

        tool_logger.info(f"RAGFlow回答完成，回答长度: {len(result)} 字符")
        use_chat.delete_sessions(ids=[session.id])
        tool_logger.debug("临时会话已删除")
        return result
    except Exception as e:
        tool_logger.error(f"提问失败: {e}\n{traceback.format_exc()}")
        return f"提问失败，错误原因：{str(e)}"


# if __name__ == "__main__": ...