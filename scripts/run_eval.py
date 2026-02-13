#!/usr/bin/env python3
"""Run evaluation suite on sample reports."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.evaluation.judge import LLMJudge


async def main():
    judge = LLMJudge()
    result = await judge.evaluate(
        report="# Sample Report\n\nThis is a test report for evaluation.",
        query="What is AI?",
    )
    print("Evaluation result:", result)


if __name__ == "__main__":
    asyncio.run(main())
