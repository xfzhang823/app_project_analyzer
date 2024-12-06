""" main.py """

import argparse
import asyncio
import logging
from async_project_analyzer import AsyncProjectAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Analyze Python projects using an LLM.")
    parser.add_argument(
        "-d", "--directory",
        type=str,
        help="Path to the root directory of the project to analyze."
    )
    parser.add_argument(
        "-f", "--files",
        nargs="+",
        help="List of specific Python files to analyze."
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=".",
        help="Directory where analysis results will be saved. Defaults to the current directory."
    )
    parser.add_argument(
        "-n", "--name",
        type=str,
        default="MyProject",
        help="Name of the project for labeling results. Defaults to 'MyProject'."
    )
    parser.add_argument(
        "-p", "--provider",
        type=str,
        choices=["openai", "claude", "llama3"],
        default="openai",
        help="LLM provider to use (openai, claude, or llama3). Defaults to 'openai'."
    )
    parser.add_argument(
        "-m", "--model",
        type=str,
        help="LLM model ID to use. Defaults to the recommended model for the provider."
    )
    parser.add_argument(
        "-c", "--concurrency",
        type=int,
        default=5,
        help="Maximum number of concurrent API calls. Defaults to 5."
    )

    args = parser.parse_args()

    # Validate input
    if not args.directory and not args.files:
        parser.error("Either --directory or --files must be specified.")

    # Initialize the analyzer
    analyzer = AsyncProjectAnalyzer(
        llm_provider=args.provider,
        model_id=args.model,
        max_concurrent_calls=args.concurrency,
    )

    # Run the analysis
    try:
        await analyzer.analyze_project(
            project_path=args.directory,
            output_path=args.output,
            project_name=args.name,
            file_list=args.files,
        )
    except Exception as e:
        logger.error(f"An error occurred during analysis: {e}")


if __name__ == "__main__":
    asyncio.run(main())
