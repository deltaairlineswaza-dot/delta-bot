"""
main.py — Entry point for the Delta Air Lines HelpDesk Discord bot.

Usage:
    python main.py

Requires a .env file (or environment variables) with:
    DISCORD_TOKEN=your_bot_token_here
"""

from __future__ import annotations

import os
import logging

import discord
from discord.ext import commands
from dotenv import load_dotenv

from commands import register_commands
from views import AssistancePanelView, CloseTicketButton

load_dotenv()

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("delta-helpdesk")

# ── Intents ───────────────────────────────────────────────────────────────────
intents = discord.Intents.default()
intents.members = True       # Needed to fetch members for DMs / permission checks
intents.message_content = True


# ── Bot subclass ──────────────────────────────────────────────────────────────

class DeltaBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix="!",   # Not used, but required by commands.Bot
            intents=intents,
            help_command=None,
        )

    async def setup_hook(self) -> None:
        # Register persistent views so buttons survive bot restarts
        self.add_view(AssistancePanelView())
        self.add_view(CloseTicketButton())

        # Register slash commands
        register_commands(self.tree)

        # Sync the command tree globally.
        # For faster propagation during development you can pass a guild:
        #   await self.tree.sync(guild=discord.Object(id=YOUR_GUILD_ID))
        synced = await self.tree.sync()
        log.info("Synced %d application command(s).", len(synced))

    async def on_ready(self) -> None:
        log.info("Logged in as %s (ID: %s)", self.user, self.user.id if self.user else "unknown")
        log.info("Delta Air Lines HelpDesk is online and ready.")
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="✈️  Delta Air Lines Support",
            )
        )


# ── Run ───────────────────────────────────────────────────────────────────────

def main() -> None:
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise RuntimeError(
            "DISCORD_TOKEN environment variable is not set. "
            "Copy .env.example to .env and fill in your bot token."
        )
    bot = DeltaBot()
    bot.run(token, log_handler=None)   # We configure logging ourselves above


if __name__ == "__main__":
    main()
