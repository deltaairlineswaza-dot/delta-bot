"""
utils.py — Shared helper utilities for the Delta HelpDesk bot.
"""

from __future__ import annotations

import discord
from config import STAFF_ROLE_ID, TICKET_CATEGORY_ID


def is_staff(member: discord.Member) -> bool:
    """Return True if the member has the designated staff role."""
    return any(role.id == STAFF_ROLE_ID for role in member.roles)


async def find_existing_ticket(
    guild: discord.Guild,
    user: discord.Member,
) -> discord.TextChannel | None:
    """
    Search the ticket category for a channel whose topic contains the
    user's ID.  Returns the first match or None.
    """
    category = guild.get_channel(TICKET_CATEGORY_ID)
    if category is None or not isinstance(category, discord.CategoryChannel):
        return None

    for channel in category.channels:
        if isinstance(channel, discord.TextChannel):
            topic = channel.topic or ""
            if str(user.id) in topic:
                return channel

    return None


async def create_ticket_channel(
    guild: discord.Guild,
    member: discord.Member,
    prefix: str,
    support_role_id: int,
) -> discord.TextChannel:
    """
    Create a private ticket channel in the ticket category.
    Permissions: ticket creator + bot + support role can read/send.
    Returns the created TextChannel.
    """
    category = guild.get_channel(TICKET_CATEGORY_ID)
    if category is None:
        raise ValueError(f"Ticket category {TICKET_CATEGORY_ID} not found in guild.")

    bot_member = guild.me
    support_role = guild.get_role(support_role_id)

    # Channel name: prefix-username (Discord usernames are already lowercase)
    channel_name = f"{prefix}-{member.name}"

    # Build permission overwrites
    overwrites: dict[discord.abc.Snowflake, discord.PermissionOverwrite] = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        member: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            read_message_history=True,
            attach_files=True,
            embed_links=True,
        ),
        bot_member: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            manage_channels=True,
            read_message_history=True,
        ),
    }
    if support_role is not None:
        overwrites[support_role] = discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            read_message_history=True,
            manage_channels=True,
        )

    channel = await guild.create_text_channel(
        name=channel_name,
        category=category,  # type: ignore[arg-type]
        overwrites=overwrites,
        topic=f"Ticket owner: {member.id}",
        reason=f"HelpDesk ticket opened by {member} ({member.id})",
    )
    return channel


def can_close_ticket(
    member: discord.Member,
    channel: discord.TextChannel,
) -> bool:
    """
    Return True if the member is allowed to close the ticket:
      - Is the ticket creator (ID stored in channel topic), OR
      - Has the staff role, OR
      - Has Manage Channels permission.
    """
    topic = channel.topic or ""
    if str(member.id) in topic:
        return True
    if is_staff(member):
        return True
    if channel.permissions_for(member).manage_channels:
        return True
    return False
