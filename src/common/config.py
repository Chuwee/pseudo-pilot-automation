"""
Docstring para src.common.config
"""
import os
from dotenv import load_dotenv

load_dotenv()


WHISPER_API_KEY = os.environ.get("WHISPER_API_KEY")
WHISPER_MODEL= os.environ.get("WHISPER_MODEL")

# Redis Configuration for shared context database
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
REDIS_DB = int(os.environ.get("REDIS_DB", "0"))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", None)
USE_REDIS = os.environ.get("USE_REDIS", "true").lower() == "true"
