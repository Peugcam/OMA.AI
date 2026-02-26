"""
Simple example of using OpenClaw programmatically
"""

import asyncio
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from openclaw.openclaw import OpenClaw
import os
from dotenv import load_dotenv

load_dotenv()


async def main():
    """Example usage of OpenClaw"""

    # Initialize
    claw = OpenClaw()

    print("\n" + "="*60)
    print("Example 1: Generate a simple function")
    print("="*60 + "\n")

    # Get coder agent
    coder = claw.registry.get("coder")

    # Task 1: Generate a function
    result = await coder.run(task={
        "description": "Create a function that calculates fibonacci numbers using memoization",
        "language": "python"
    })

    if result.success:
        print("✅ Success!\n")
        print("Explanation:")
        print(result.result["explanation"])
        print("\nGenerated Code:")
        print(result.result["code"])
    else:
        print(f"❌ Failed: {result.error}")

    print("\n" + "="*60)
    print("Example 2: Refactor code")
    print("="*60 + "\n")

    # Task 2: Refactor code
    messy_code = """
def calc(n):
    if n == 0: return 0
    if n == 1: return 1
    return calc(n-1) + calc(n-2)
"""

    result = await coder.refactor(
        code=messy_code,
        goal="add memoization for performance and improve readability"
    )

    if result.success:
        print("✅ Success!\n")
        print("Original:")
        print(result.result["original"])
        print("\nRefactored:")
        print(result.result["refactored"])
        print("\nExplanation:")
        print(result.result["explanation"])

    print("\n" + "="*60)
    print("Agent Statistics")
    print("="*60 + "\n")

    # Show stats
    stats = coder.get_stats()
    print(f"Total executions: {stats['total_executions']}")
    print(f"Successes: {stats['successes']}")
    print(f"Success rate: {stats['success_rate']:.1%}")


if __name__ == "__main__":
    asyncio.run(main())
