"""
tickets.py — Higher-level ticket orchestration helpers.

Thin wrappers used by both slash commands and UI views so the logic
stays in one place.
"""

from __future__ import annotations

import discord

from utils import find_existing_ticket, can_close_ticket
from views import _close_ticket
from embeds import already_open_ticket, error_embed


async def handle_close_from_command(interaction: discord.Interaction) -> None:
    """
    Logic executed when a staff member runs /close inside a ticket channel.
    Mirrors the Close Ticket button but is initiated from a slash command.
    """
    channel = interaction.channel
    member  = interaction.user

    if not isinstance(channel, discord.TextChannel):
        await interaction.response.send_message(
            embed=error_embed("This command can only be used inside a ticket channel."),
            ephemeral=True,
        )
        return

    if not isinstance(member, discord.Member):
        await interaction.response.send_message(
            embed=error_embed("Unable to verify your permissions."),
            ephemeral=True,
        )
        return

    if not can_close_ticket(member, channel):
        await interaction.response.send_message(
            embed=error_embed("You do not have permission to close this ticket."),
            ephemeral=True,
        )
        return

    await _close_ticket(interaction, channel, member)
