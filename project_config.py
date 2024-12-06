""" Data Input/Output dir/file configuration 

# example_usagage (from modules)

from config import (
...
)

"""

from pathlib import Path
import os
import logging
import logging_config

logger = logging.getLogger(__name__)

BASE_DIR = Path(r"C:\github\app_project_analyzer")  # base/root directory
# logging.info(f"BASE_DIR set to {BASE_DIR}")

# *LLM Models
# Anthropic (Claude) models
CLAUDE_OPUS = "claude-3-opus-20240229"
CLAUDE_SONNET = "claude-3-5-sonnet-20241022"
CLAUDE_HAIKU = "claude-3-haiku-20240307"

# OpenAI models
GPT_35_TURBO = "gpt-3.5-turbo"
GPT_35_TURBO_16K = "gpt-3.5-turbo-16k"
GPT_4 = "gpt-4"
GPT_4_TURBO = "gpt-4-turbo"
GPT_4_TURBO_32K = "gpt-4-turbo-32k"
GPT_4O = "gpt-4o"
