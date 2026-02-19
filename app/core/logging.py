import logging
import json
import os
from .config import settings

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "filename": record.filename,
            "line": record.lineno
        }
        if hasattr(record, "extra_data"):
            log_obj.update(record.extra_data)
        
        return json.dumps(log_obj)

def setup_logging():
    log_level = logging.INFO
    
    os.makedirs(settings.LOGS_DIR, exist_ok=True)

    agent_logger = logging.getLogger("agent")
    agent_logger.setLevel(log_level)
    agent_handler = logging.FileHandler(os.path.join(settings.LOGS_DIR, "agent.log"))
    agent_handler.setFormatter(JSONFormatter())
    agent_logger.addHandler(agent_handler)

    error_logger = logging.getLogger("error")
    error_logger.setLevel(logging.ERROR)
    error_handler = logging.FileHandler(os.path.join(settings.LOGS_DIR, "errors.log"))
    error_handler.setFormatter(JSONFormatter())
    error_logger.addHandler(error_handler)

    build_logger = logging.getLogger("build")
    build_logger.setLevel(log_level)
    build_handler = logging.FileHandler(os.path.join(settings.LOGS_DIR, "build.log"))
    build_handler.setFormatter(JSONFormatter())
    build_logger.addHandler(build_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logging.basicConfig(level=log_level, handlers=[console_handler])

def get_logger(name: str):
    return logging.getLogger(name)
