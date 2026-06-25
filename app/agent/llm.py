"""
大模型初始化模块

负责从 .env 中读取模型配置，并创建项目统一复用的模型对象
后续主智能体和子智能体都从这里导入 model，避免在多个文件里重复加载环境变量
"""

import os
import traceback

from dotenv import find_dotenv, load_dotenv
from langchain.chat_models import init_chat_model

from app.utils.logger import logger  # 导入全局日志对象

# find_dotenv 会从当前目录向上查找 .env，适合脚本和 Web 服务从不同入口启动的场景
load_dotenv(find_dotenv())

# 读取配置
model_name = os.getenv("LLM_QWEN_MAX")
base_url = os.getenv("OPENAI_BASE_URL")  # 用于日志，不含 API Key

logger.info(f"开始初始化模型: model={model_name}, base_url={base_url}")

try:
    # 使用 OpenAI 兼容协议接入模型；具体模型名由 .env 中的 LLM_QWEN_MAX 控制
    model = init_chat_model(
        model=model_name,
        model_provider="openai",
    )
    logger.info("模型初始化成功")
except Exception as e:
    # 记录完整堆栈，便于排查网络/配置问题
    error_detail = traceback.format_exc()
    logger.error(f"模型初始化失败:\n{error_detail}")
    raise  # 仍抛出异常，让上层处理