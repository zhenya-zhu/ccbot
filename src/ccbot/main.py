"""Application entry point — CLI dispatcher and bot bootstrap.

Handles three execution modes:
  1. `ccbot hook` — delegates to hook.hook_main() for Claude Code / Codex hook processing.
  2. `ccbot session-register` — registers tmux window -> Claude Code / Codex session metadata.
  3. Default — applies top-level CLI overrides, configures logging, initializes tmux session, and starts the
     Telegram bot polling loop via bot.create_bot().
"""

import argparse
import logging
import os
import sys

from .runtimes import SUPPORTED_RUNTIMES


def _apply_global_cli_overrides(argv: list[str]) -> list[str]:
    """Apply global CLI overrides and return the remaining argv.

    Supports `ccbot --run claude|codex` so users can switch between
    Claude Code and Codex without editing environment variables.
    """
    parser = argparse.ArgumentParser(
        prog="ccbot",
        add_help=False,
    )
    parser.add_argument(
        "--run",
        "--runtime",
        dest="runtime",
        choices=sorted(SUPPORTED_RUNTIMES),
        help="Runtime (Claude Code or Codex) for this bot process",
    )
    parser.add_argument("-h", "--help", action="store_true")

    args, remaining = parser.parse_known_args(argv[1:])

    if args.runtime:
        os.environ["CCBOT_RUNTIME"] = args.runtime

    if remaining and remaining[0] in {"hook", "session-register"}:
        return [argv[0], *remaining]

    if args.help:
        help_parser = argparse.ArgumentParser(
            prog="ccbot",
            description="Telegram bot for tmux-backed Claude Code or Codex sessions",
        )
        help_parser.add_argument(
            "--run",
            "--runtime",
            dest="runtime",
            choices=sorted(SUPPORTED_RUNTIMES),
            help="Runtime (Claude Code or Codex) for this bot process",
        )
        help_parser.print_help()
        raise SystemExit(0)

    if remaining:
        parser.error(f"unrecognized arguments: {' '.join(remaining)}")

    return [argv[0]]


def main() -> None:
    """Main entry point."""
    argv = _apply_global_cli_overrides(sys.argv)
    sys.argv = argv

    if len(argv) > 1 and argv[1] == "hook":
        from .hook import hook_main

        hook_main()
        return
    if len(argv) > 1 and argv[1] == "session-register":
        from .session_register import session_register_main

        session_register_main()
        return

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.WARNING,
    )

    # Import config before enabling DEBUG — avoid leaking debug logs on config errors
    try:
        from .config import config
    except ValueError as e:
        from .utils import ccbot_dir

        config_dir = ccbot_dir()
        env_path = config_dir / ".env"
        print(f"Error: {e}\n")
        print(f"Create {env_path} with the following content:\n")
        print("  TELEGRAM_BOT_TOKEN=your_bot_token_here")
        print("  ALLOWED_USERS=your_telegram_user_id")
        print()
        print("Get your bot token from @BotFather on Telegram.")
        print("Get your user ID from @userinfobot on Telegram.")
        sys.exit(1)

    logging.getLogger("ccbot").setLevel(logging.DEBUG)
    # AIORateLimiter (max_retries=5) handles retries itself; keep INFO for visibility
    logging.getLogger("telegram.ext.AIORateLimiter").setLevel(logging.INFO)
    logger = logging.getLogger(__name__)

    from .tmux_manager import tmux_manager

    logger.info("Allowed users: %s", config.allowed_users)
    logger.info("Runtime (Claude Code or Codex): %s", config.runtime)
    logger.info("Claude projects path: %s", config.claude_projects_path)
    logger.info("Codex home: %s", config.codex_home)

    # Ensure tmux session exists
    session = tmux_manager.get_or_create_session()
    logger.info("Tmux session '%s' ready", session.session_name)

    logger.info("Starting Telegram bot...")
    from .bot import create_bot

    application = create_bot()
    application.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
