"""
Entry point for whispy.

Run with:
    python -m app.main
    python -m app.main --backend openai   # use OpenAI Whisper API (needs OPENAI_API_KEY)
    python -m app.main --backend local    # use local faster-whisper (default)
"""

import argparse
import sys

from app.core.config import load_config, write_default_config
from app.integrations.logging import setup_logging


def main() -> None:
    parser = argparse.ArgumentParser(description="whispy — speech-to-text TUI")
    parser.add_argument(
        "--backend",
        choices=["local", "openai"],
        default=None,
        help="Transcription backend to use (overrides config file)",
    )
    args = parser.parse_args()

    setup_logging()

    write_default_config()
    config = load_config()

    if args.backend is not None:
        config.transcription.backend = args.backend

    from app.tui.app import WhispyApp
    app = WhispyApp(config=config)
    app.run()


if __name__ == "__main__":
    main()
