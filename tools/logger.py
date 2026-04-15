import logging
import os
from typing import Literal

# 定义日志模块
class TagFormatter(logging.Formatter):
    def format(self, record):
        if not hasattr(record, 'tag'):
            record.tag = 'GENERAL'  # 设置默认tag
        return f"[{record.tag}] {super().format(record)}"

logger = logging.getLogger("myLogger")
logger.setLevel(logging.INFO)

# 确保日志目录存在
log_dir = "log"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

file_handler = logging.FileHandler("log/running_log.log", encoding='utf-8')
formatter = TagFormatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# 添加控制台输出
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# 日志保存简易函数
def log_with_tag(message, tag='GENERAL', level: Literal['debug', 'info', 'warning', 'error', 'critical'] = 'info'):
    if level == 'info':
        logger.info(message, extra={'tag': tag})
    elif level == 'warning':
        logger.warning(message, extra={'tag': tag})
    elif level == 'error':
        logger.error(message, extra={'tag': tag})
    elif level == 'debug':
        logger.debug(message, extra={'tag': tag})
    elif level == 'critical':
        logger.critical(message, extra={'tag': tag})
