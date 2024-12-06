"""project_analyzer_async"""

import os
import re
import asyncio
import aiofiles
from typing import List, Dict, Optional
import logging

from llm_api_async import (
    call_claude_api_async,
    call_openai_api_async,
    call_llama3_async,
)
from project_config import GPT_4_TURBO, CLAUDE_SONNET  # Default model constants

logger = logging.getLogger(__name__)


class AsyncProjectAnalyzer:
    def __init__(
        self,
        llm_provider: str = "openai",
        model_id: Optional[str] = None,
        max_concurrent_calls: int = 5,
    ):
        """
        Initialize AsyncProjectAnalyzer.

        Args:
            llm_provider (str): LLM provider name ('openai', 'claude', or 'llama3').
            model_id (str): LLM model ID to use. Defaults based on provider.
            max_concurrent_calls (int): Maximum number of concurrent API calls.
        """
        self.llm_provider = llm_provider
        self.model_id = model_id or (
            GPT_4_TURBO if llm_provider == "openai" else CLAUDE_SONNET
        )
        self.semaphore = asyncio.Semaphore(max_concurrent_calls)

    async def read_file(self, file_path: str) -> str:
        """Read a file asynchronously."""
        try:
            async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                return await f.read()
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            return ""

    async def summarize_file(self, file_path: str) -> str:
        """Summarize the content of a file, removing inline comments but preserving docstrings."""
        content = await self.read_file(file_path)
        if content:
            content = re.sub(r'(?<!["\'\\])#.*$', "", content, flags=re.MULTILINE)
            content = re.sub(r"^(\s*#.*\n)+", "", content, flags=re.MULTILINE)
        return content

    async def analyze_files(self, files: List[str]) -> Dict[str, str]:
        """Analyze all files asynchronously."""
        tasks = [self.summarize_file(file) for file in files]
        summaries = await asyncio.gather(*tasks)
        return {file: summary for file, summary in zip(files, summaries) if summary}

    async def generate_summary(
        self, summaries: Dict[str, str], project_name: str
    ) -> str:
        """Generate a project summary using the specified LLM."""
        content = "\n\n".join(
            [f"### {path}\n{summary}" for path, summary in summaries.items()]
        )
        prompt = (
            f"Analyze the Python project '{project_name}' and provide:\n"
            "1. A comprehensive project summary.\n"
            "2. A detailed README.md file.\n"
            "3. Key architectural insights and potential improvements.\n\n" + content
        )

        async with self.semaphore:
            if self.llm_provider == "claude":
                return await call_claude_api_async(prompt, model_id=self.model_id)
            elif self.llm_provider == "openai":
                return await call_openai_api_async(prompt, model_id=self.model_id)
            elif self.llm_provider == "llama3":
                return await call_llama3_async(prompt, model_id=self.model_id)
            else:
                raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")

    async def analyze_project(
        self,
        project_path: Optional[str] = None,
        output_path: str = ".",
        project_name: str = "MyProject",
        file_list: Optional[List[str]] = None,
    ):
        """
        Analyze the project, either by scanning a directory or using a specific list of files.

        Args:
            project_path (str, optional): Path to the root directory of the project.
            output_path (str): Directory to save the output files.
            project_name (str): Name of the project for labeling results.
            file_list (List[str], optional): Specific Python files to analyze.
        """
        if file_list:
            # Use the provided file list
            files = file_list
            logger.info(f"Analyzing specific files: {files}")
        elif project_path:
            # Scan the project directory for Python files
            files = [
                os.path.join(root, file)
                for root, _, files in os.walk(project_path)
                for file in files
                if file.endswith(".py")
            ]
            logger.info(f"Analyzing all Python files in directory: {project_path}")
        else:
            raise ValueError("Either 'project_path' or 'file_list' must be provided.")

        if not files:
            logger.error("No Python files found to analyze.")
            return

        # Analyze files and generate a project summary
        summaries = await self.analyze_files(files)
        project_summary = await self.generate_summary(summaries, project_name)

        # Save results (synchronously for simplicity, or could use aiofiles for async saving)
        output_dir = os.path.join(output_path, f"{project_name}_analysis")
        os.makedirs(output_dir, exist_ok=True)

        # Save summaries
        for file, summary in summaries.items():
            rel_path = os.path.basename(file).replace(os.sep, "_")
            with open(
                os.path.join(output_dir, f"{rel_path}.json"), "w", encoding="utf-8"
            ) as f:
                f.write(summary)

        # Save project summary
        with open(
            os.path.join(output_dir, "project_summary.md"), "w", encoding="utf-8"
        ) as f:
            f.write(project_summary)

        logger.info(f"Analysis complete. Results saved to {output_dir}.")
