#!/usr/bin/env python3
"""
Web Research Agent - CLI Entry Point

A production-ready autonomous research agent that searches the web,
synthesizes information, and produces structured research reports.

Usage:
    python main.py "your research query"
    python main.py "your research query" --model gpt-4o --verbose
"""

import argparse
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

# Load environment variables before importing other modules
load_dotenv()


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Web Research Agent - Autonomous research and report generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python main.py "What are the best practices for Python async programming?"
    python main.py "Compare React vs Vue.js for enterprise applications" --model gpt-4o
    python main.py "Latest developments in quantum computing" --verbose
    python main.py "Elon Musk net worth" --output report.txt
        """,
    )

    parser.add_argument(
        "query",
        type=str,
        help="The research query to investigate",
    )

    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="OpenAI model to use (default: gpt-4o-mini)",
    )

    parser.add_argument(
        "--max-iterations",
        type=int,
        default=None,
        help="Maximum agent iterations (default: 25)",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output for debugging",
    )

    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Save report to file instead of stdout",
    )

    return parser.parse_args()


def print_header() -> None:
    """Print report header."""
    print("\n" + "=" * 70)
    print("                       RESEARCH SUMMARY")
    print("=" * 70 + "\n")


def print_footer() -> None:
    """Print report footer."""
    print("\n" + "=" * 70 + "\n")


def main() -> int:
    """
    Main entry point for the research agent.

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    args = parse_arguments()

    # Import after dotenv to ensure environment is loaded
    from src.config import get_settings
    from src.logging_config import setup_logging
    from src.agent import create_agent
    from src.exceptions import ResearchAgentError, ConfigurationError

    # Setup logging
    try:
        settings = get_settings()
        setup_logging(level=settings.log_level, verbose=args.verbose)
    except Exception as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        print(
            "\nPlease ensure OPENAI_API_KEY is set in your environment or .env file.",
            file=sys.stderr,
        )
        return 1

    # Create agent
    try:
        agent = create_agent(
            model=args.model,
            max_iterations=args.max_iterations,
        )
    except ConfigurationError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error creating agent: {e}", file=sys.stderr)
        return 1

    # Execute research
    try:
        result = agent.research(args.query)

        if args.output:
            # Save to file
            output_path = Path(args.output)
            output_path.write_text(result.content)
            print(f"Report saved to: {output_path}")
        else:
            # Print to stdout
            print_header()
            print(result.content)
            print_footer()

        return 0

    except KeyboardInterrupt:
        print("\n\nResearch cancelled by user.", file=sys.stderr)
        return 130

    except ResearchAgentError as e:
        print(f"\nResearch error: {e}", file=sys.stderr)
        return 1

    except Exception as e:
        print(f"\nUnexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
