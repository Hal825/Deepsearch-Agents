import sys
import traceback
from pathlib import Path
from loguru import logger

# 1. 定义项目根目录和日志存储目录
PROJECT_ROOT = Path(__file__).parent.parent.parent  # 指向 deepsearch-agents/
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)  # 确保目录存在

# 2. 移除 loguru 默认的 Handler，避免重复打印
logger.remove()

# 3. 控制台日志格式（开发环境友好，带颜色）
logger.add(
    sys.stdout,
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    ),
    level="DEBUG",  # 开发阶段开 DEBUG，生产可改为 INFO
    colorize=True,
)

# 4. 文件日志格式（持久化存储，包含更多元数据）
logger.add(
    LOG_DIR / "deepsearch_{time:YYYY-MM-DD}.log",
    rotation="00:00",          # 每天午夜轮转
    retention="30 days",       # 保留 30 天
    compression="zip",         # 旧日志自动压缩为 zip，节省空间
    encoding="utf-8",
    format=(
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
        "{level: <8} | "
        "{name}:{function}:{line} | "
        "Process:{process.id} Thread:{thread.id} | "
        "{message}"
    ),
    level="DEBUG",
    backtrace=True,            # 启用异常堆栈回溯
    diagnose=True,             # 开启变量诊断（生产环境建议 False，避免泄露敏感信息）
)

# 5. 专门为异常设计的“错误详情”日志文件（单独存放，方便查错）
logger.add(
    LOG_DIR / "errors_{time:YYYY-MM-DD}.log",
    rotation="00:00",
    retention="90 days",
    compression="zip",
    format=(
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
        "{level} | "
        "{name}:{function}:{line} | "
        "Exception:\n{exception}"
    ),
    level="ERROR",
    backtrace=True,
    diagnose=True,
)

# 6. 导出 logger，并提供便捷的上下文绑定方法
class LoggerContext:
    """用于在异步任务中绑定 session_id 和 thread_id"""
    @staticmethod
    def bind_task(session_id: str, thread_id: str = None):
        """绑定当前任务的上下文，后续所有日志自动带上这些字段"""
        context = {"session_id": session_id}
        if thread_id:
            context["thread_id"] = thread_id
        return logger.bind(**context)

# 导出全局 logger，整个项目统一使用
__all__ = ["logger", "LoggerContext"]

# 启动时打印日志目录位置，方便快速定位
logger.info(f"日志系统初始化完成，日志目录: {LOG_DIR.absolute()}")