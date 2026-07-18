"""
Delta Air Lines HelpDesk Discord Bot — Single-file version
All configuration, embeds, views, and commands in one file.

Usage:
    python main.py

Requires a .env file with:
    DISCORD_TOKEN=your_bot_token_here
"""

from __future__ import annotations

import asyncio
import logging
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════

DELTA_RED       = 0xC8102E
FOOTER_TEXT     = "Delta Air Lines • Keep Climbing"
MAILING_ADDRESS = "P.O. Box 20980, Department 980, Atlanta, GA 30320-2980"

BANNER_URL = (
    "https://cdn.discordapp.com/attachments/1525901449769254922"
    "/1525992386948239582/delta_banner.jpg"
)
DIVIDER_URL = (
    "https://cdn.discordapp.com/attachments/1525901449769254922"
    "/1525992387254685869/skinny_delta_banner.jpg"
)

TICKET_CATEGORY_ID      = 1524489811627475075
STAFF_ROLE_ID           = 1436474227971592325
GENERAL_SUPPORT_ROLE_ID = 1436480867240251493

# Each key maps to a ticket category. Add new rows here to add new categories.
TICKET_CONFIG: dict[str, dict] = {
    "general_inquiries": {
        "label":       "General Inquiries",
        "prefix":      "general-support",
        "role_id":     GENERAL_SUPPORT_ROLE_ID,
        "emoji":       "📋",
        "description": "General questions about Delta Air Lines services.",
    },
    "lead_support": {
        "label":       "Lead Support",
        "prefix":      "lead-support",
        "role_id":     STAFF_ROLE_ID,
        "emoji":       "🏅",
        "description": "Escalated issues requiring a lead team member.",
    },
    "partnership_requests": {
        "label":       "Partnership Requests",
        "prefix":      "partnership",
        "role_id":     STAFF_ROLE_ID,
        "emoji":       "🤝",
        "description": "Inquiries regarding business partnerships.",
    },
    "class_purchases": {
        "label":       "Class Purchases",
        "prefix":      "class-purchase",
        "role_id":     STAFF_ROLE_ID,
        "emoji":       "💺",
        "description": "Purchase or upgrade a cabin class.",
    },
    "application_status": {
        "label":       "Application Status",
        "prefix":      "application",
        "role_id":     STAFF_ROLE_ID,
        "emoji":       "📄",
        "description": "Check the status of a submitted application.",
    },
    "jobs_roles": {
        "label":       "Jobs & Roles",
        "prefix":      "jobs",
        "role_id":     STAFF_ROLE_ID,
        "emoji":       "💼",
        "description": "Inquiries about open positions and roles.",
    },
    "bug_reports": {
        "label":       "Bug Reports",
        "prefix":      "bug-report",
        "role_id":     STAFF_ROLE_ID,
        "emoji":       "🐛",
        "description": "Report a bug or technical issue.",
    },
}

# ══════════════════════════════════════════════════════════════════════════════
# EMBEDS
# ══════════════════════════════════════════════════════════════════════════════

def _base_embed(title: str = "", description: str = "") -> discord.Embed:
    embed = discord.Embed(title=title, description=description, color=DELTA_RED)
    embed.set_footer(text=FOOTER_TEXT)
    return embed


def assistance_panel_banner_embed() -> discord.Embed:
    embed = discord.Embed(color=DELTA_RED)
    embed.set_image(url=BANNER_URL)
    return embed


def assistance_panel_embed() -> discord.Embed:
    embed = _base_embed(
        title="✈️  Delta Air Lines — HelpDesk",
        description=(
            "Welcome to the **Delta Air Lines Support Centre**.\n\n"
            "Our dedicated team is here to assist you with any questions, "
            "concerns, or requests you may have. Please select a category "
            "from the dropdown menu below to open a private support ticket.\n\n"
            "A member of our support team will be with you as soon as possible. "
            "Thank you for choosing Delta Air Lines — *Keep Climbing.*"
        ),
    )
    embed.add_field(name="📬 Mailing Address", value=MAILING_ADDRESS, inline=False)
    embed.set_image(url=DIVIDER_URL)
    return embed


def general_inquiries_welcome(member: discord.Member) -> discord.Embed:
    embed = _base_embed(
        title="📋  General Inquiries — Support Ticket",
        description=(
            f"Welcome, {member.mention}! Thank you for reaching out to "
            "**Delta Air Lines Support**.\n\n"
            "A member of our General Support team has been notified and will "
            "be with you shortly.\n\n"
            "**Please provide as much detail as possible:**\n"
            "• Describe your question or concern clearly.\n"
            "• Attach any relevant screenshots, videos, or documents.\n"
            "• Include booking references, dates, or flight numbers if applicable.\n\n"
            "The more information you share, the faster our team can assist you."
        ),
    )
    embed.add_field(name="📬 Mailing Address", value=MAILING_ADDRESS, inline=False)
    embed.set_image(url=DIVIDER_URL)
    return embed


def generic_ticket_welcome(member: discord.Member, label: str, emoji: str) -> discord.Embed:
    embed = _base_embed(
        title=f"{emoji}  {label} — Support Ticket",
        description=(
            f"Welcome, {member.mention}! Thank you for contacting "
            "**Delta Air Lines Support**.\n\n"
            "A member of our team will be with you shortly. "
            "Please describe your request in as much detail as possible "
            "and attach any supporting files.\n\n"
            "*We appreciate your patience and thank you for flying Delta.*"
        ),
    )
    embed.add_field(name="📬 Mailing Address", value=MAILING_ADDRESS, inline=False)
    embed.set_image(url=DIVIDER_URL)
    return embed


def ticket_closed_dm(ticket_name: str) -> discord.Embed:
    embed = _base_embed(
        title="🔒  Ticket Closed",
        description=(
            f"Your support ticket **#{ticket_name}** has been successfully closed.\n\n"
            "Thank you for contacting **Delta Air Lines Support**. "
            "We hope we were able to assist you today. "
            "If you need further assistance, please don't hesitate to open a new ticket.\n\n"
            "*Delta Air Lines — Keep Climbing.*"
        ),
    )
    embed.add_field(name="📬 Mailing Address", value=MAILING_ADDRESS, inline=False)
    embed.set_image(url=DIVIDER_URL)
    return embed


def ticket_closed_channel() -> discord.Embed:
    embed = _base_embed(
        title="🔒  Ticket Closing",
        description=(
            "This ticket has been marked as **closed** and will be deleted shortly.\n\n"
            "Thank you for contacting Delta Air Lines Support."
        ),
    )
    embed.set_image(url=DIVIDER_URL)
    return embed


def already_open_ticket(channel: discord.TextChannel) -> discord.Embed:
    embed = _base_embed(
        title="⚠️  Active Ticket Found",
        description=(
            f"You already have an open support ticket: {channel.mention}\n\n"
            "Please continue your conversation there. "
            "If you believe this is an error, contact a staff member."
        ),
    )
    return embed


def error_embed(message: str) -> discord.Embed:
    embed = discord.Embed(title="❌  Error", description=message, color=DELTA_RED)
    embed.set_footer(text=FOOTER_TEXT)
    return embed


def success_embed(message: str) -> discord.Embed:
    embed = discord.Embed(title="✅  Success", description=message, color=DELTA_RED)
    embed.set_footer(text=FOOTER_TEXT)
    return embed


# ══════════════════════════════════════════════════════════════════════════════
# UTILITIES
# ══════════════════════════════════════════════════════════════════════════════

def is_staff(member: discord.Member) -> bool:
    return any(role.id == STAFF_ROLE_ID for role in member.roles)


async def find_existing_ticket(
    guild: discord.Guild,
    user: discord.Member,
) -> discord.TextChannel | None:
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
    category = guild.get_channel(TICKET_CATEGORY_ID)
    if category is None:
        raise ValueError(f"Ticket category {TICKET_CATEGORY_ID} not found.")

    support_role = guild.get_role(support_role_id)
    channel_name = f"{prefix}-{member.name}"

    overwrites: dict[discord.abc.Snowflake, discord.PermissionOverwrite] = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        member: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            read_message_history=True,
            attach_files=True,
            embed_links=True,
        ),
        guild.me: discord.PermissionOverwrite(
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


def can_close_ticket(member: discord.Member, channel: discord.TextChannel) -> bool:
    topic = channel.topic or ""
    if str(member.id) in topic:
        return True
    if is_staff(member):
        return True
    if channel.permissions_for(member).manage_channels:
        return True
    return False


# ══════════════════════════════════════════════════════════════════════════════
# INTERNAL CLOSE HELPER
# ══════════════════════════════════════════════════════════════════════════════

async def _close_ticket(
    interaction: discord.Interaction,
    channel: discord.TextChannel,
    closer: discord.Member,
    reason: str = "No reason provided.",
) -> None:
    topic = channel.topic or ""
    owner: discord.Member | None = None
    for part in topic.split():
        if part.isdigit():
            owner = channel.guild.get_member(int(part))
            break

    # Closing embed shown in channel
    embed = _base_embed(
        title="🔒  Ticket Closing",
        description=(
            "This ticket has been marked as **closed** and will be deleted in 5 seconds.\n\n"
            f"**Reason:** {reason}\n\n"
            "Thank you for contacting Delta Air Lines Support."
        ),
    )
    embed.set_image(url=DIVIDER_URL)
    await interaction.response.send_message(embed=embed, ephemeral=False)

    # DM the owner with reason
    if owner is not None:
        dm_embed = _base_embed(
            title="🔒  Ticket Closed",
            description=(
                f"Your support ticket **#{channel.name}** has been successfully closed.\n\n"
                f"**Reason:** {reason}\n\n"
                "Thank you for contacting **Delta Air Lines Support**. "
                "If you need further assistance, please open a new ticket.\n\n"
                "*Delta Air Lines — Keep Climbing.*"
            ),
        )
        dm_embed.add_field(name="📬 Mailing Address", value=MAILING_ADDRESS, inline=False)
        dm_embed.set_image(url=DIVIDER_URL)
        try:
            await owner.send(embed=dm_embed)
        except discord.Forbidden:
            pass

    await asyncio.sleep(5)
    try:
        await channel.delete(reason=f"Ticket closed by {closer} ({closer.id}): {reason}")
    except discord.NotFound:
        pass


# ══════════════════════════════════════════════════════════════════════════════
# MODALS
# ══════════════════════════════════════════════════════════════════════════════

class CloseReasonModal(discord.ui.Modal, title="Close Ticket — Delta Air Lines"):
    reason = discord.ui.TextInput(
        label="Reason for closing",
        placeholder="e.g. Issue resolved, No response from user...",
        style=discord.TextStyle.paragraph,
        max_length=500,
        required=True,
    )

    def __init__(self, channel: discord.TextChannel, closer: discord.Member) -> None:
        super().__init__()
        self._channel = channel
        self._closer  = closer

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await _close_ticket(
            interaction,
            self._channel,
            self._closer,
            reason=self.reason.value,
        )


# ══════════════════════════════════════════════════════════════════════════════
# VIEWS (UI COMPONENTS)
# ══════════════════════════════════════════════════════════════════════════════

class TicketActionView(discord.ui.View):
    """Persistent view with Claim and Close buttons attached to every ticket."""

    def __init__(self) -> None:
        super().__init__(timeout=None)

    # ── Claim ────────────────────────────────────────────────────────────────
    @discord.ui.button(
        label="🙋  Claim Ticket",
        style=discord.ButtonStyle.primary,
        custom_id="delta:claim_ticket",
    )
    async def claim_ticket(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ) -> None:
        member = interaction.user
        if not isinstance(member, discord.Member):
            await interaction.response.send_message(
                embed=error_embed("Unable to verify your permissions."),
                ephemeral=True,
            )
            return

        if not is_staff(member):
            await interaction.response.send_message(
                embed=error_embed("Only staff members can claim tickets."),
                ephemeral=True,
            )
            return

        # Ephemeral confirm for the claimant
        await interaction.response.send_message(
            embed=success_embed("You have claimed this ticket."),
            ephemeral=True,
        )

        # Public claim embed in the channel
        embed = _base_embed(
            title="🙋  Ticket Claimed",
            description=(
                f"This ticket has been claimed by {member.mention}.\n\n"
                "They will be assisting you shortly — "
                "please continue describing your issue."
            ),
        )
        embed.set_image(url=DIVIDER_URL)
        await interaction.channel.send(embed=embed)

    # ── Close ────────────────────────────────────────────────────────────────
    @discord.ui.button(
        label="🔒  Close Ticket",
        style=discord.ButtonStyle.danger,
        custom_id="delta:close_ticket",
    )
    async def close_ticket(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ) -> None:
        channel = interaction.channel
        member  = interaction.user

        if not isinstance(channel, discord.TextChannel):
            await interaction.response.send_message(
                embed=error_embed("This button can only be used inside a ticket channel."),
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

        await interaction.response.send_modal(CloseReasonModal(channel, member))


# Keep old name as alias so existing persistent views still resolve
CloseTicketButton = TicketActionView


class AssistanceSelect(discord.ui.Select):
    def __init__(self) -> None:
        options = [
            discord.SelectOption(
                label=cfg["label"],
                value=key,
                emoji=cfg["emoji"],
                description=cfg["description"],
            )
            for key, cfg in TICKET_CONFIG.items()
        ]
        super().__init__(
            placeholder="✈️  Select an Assistance Category",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="delta:assistance_select",
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)

        member = interaction.user
        guild  = interaction.guild

        if not isinstance(member, discord.Member) or guild is None:
            await interaction.followup.send(
                embed=error_embed("This panel can only be used inside a server."),
                ephemeral=True,
            )
            return

        selected_key = self.values[0]
        cfg = TICKET_CONFIG[selected_key]

        existing = await find_existing_ticket(guild, member)
        if existing is not None:
            await interaction.followup.send(
                embed=already_open_ticket(existing),
                ephemeral=True,
            )
            return

        try:
            channel = await create_ticket_channel(
                guild=guild,
                member=member,
                prefix=cfg["prefix"],
                support_role_id=cfg["role_id"],
            )
        except Exception as exc:
            await interaction.followup.send(
                embed=error_embed(f"Failed to create your ticket: {exc}"),
                ephemeral=True,
            )
            return

        support_role = guild.get_role(cfg["role_id"])
        ping_text = (
            f"{member.mention} {support_role.mention if support_role else ''}"
        ).strip()
        await channel.send(ping_text)

        if selected_key == "general_inquiries":
            embed = general_inquiries_welcome(member)
        else:
            embed = generic_ticket_welcome(member, cfg["label"], cfg["emoji"])

        await channel.send(embed=embed, view=TicketActionView())
        await interaction.followup.send(
            content=f"✅  Your ticket has been created: {channel.mention}",
            ephemeral=True,
        )


class AssistancePanelView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)
        self.add_item(AssistanceSelect())


# ══════════════════════════════════════════════════════════════════════════════
# SLASH COMMANDS
# ══════════════════════════════════════════════════════════════════════════════

def staff_only() -> app_commands.check:
    async def predicate(interaction: discord.Interaction) -> bool:
        member = interaction.user
        if not isinstance(member, discord.Member):
            return False
        return any(role.id == STAFF_ROLE_ID for role in member.roles)
    return app_commands.check(predicate)


def register_commands(tree: app_commands.CommandTree) -> None:

    # /assistance panel
    assistance_group = app_commands.Group(
        name="assistance",
        description="Delta Air Lines Assistance Panel commands (staff only).",
    )

    @assistance_group.command(name="panel", description="Post the Delta HelpDesk Assistance Panel.")
    @staff_only()
    async def assistance_panel(interaction: discord.Interaction) -> None:
        channel = interaction.channel
        if not isinstance(channel, discord.TextChannel):
            await interaction.response.send_message(
                embed=error_embed("This command can only be used in a text channel."),
                ephemeral=True,
            )
            return
        await interaction.response.send_message(
            embed=success_embed("Assistance Panel posted successfully."),
            ephemeral=True,
        )
        await channel.send(embed=assistance_panel_banner_embed())
        await channel.send(embed=assistance_panel_embed(), view=AssistancePanelView())

    tree.add_command(assistance_group)

    # /close
    @tree.command(name="close", description="Close the current support ticket.")
    async def close(interaction: discord.Interaction) -> None:
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
        await interaction.response.send_modal(CloseReasonModal(channel, member))

    # /connected
    @tree.command(name="connected", description="Notify the user that an agent has connected (staff only).")
    @staff_only()
    async def connected(interaction: discord.Interaction) -> None:
        channel = interaction.channel
        if not isinstance(channel, discord.TextChannel):
            await interaction.response.send_message(
                embed=error_embed("This command must be used inside a ticket channel."),
                ephemeral=True,
            )
            return
        await interaction.response.send_message(
            embed=success_embed("Message sent successfully."),
            ephemeral=True,
        )
        embed = discord.Embed(
            title="🛫  Agent Connected",
            description=(
                "A **Delta Air Lines Support Agent** has connected to your ticket "
                "and will be assisting you shortly.\n\n"
                "Please feel free to continue describing your issue."
            ),
            color=DELTA_RED,
        )
        embed.set_footer(text=FOOTER_TEXT)
        await channel.send(embed=embed)

    # /resolved
    @tree.command(name="resolved", description="Mark the ticket as resolved (staff only).")
    @staff_only()
    async def resolved(interaction: discord.Interaction) -> None:
        channel = interaction.channel
        if not isinstance(channel, discord.TextChannel):
            await interaction.response.send_message(
                embed=error_embed("This command must be used inside a ticket channel."),
                ephemeral=True,
            )
            return
        await interaction.response.send_message(
            embed=success_embed("Message sent successfully."),
            ephemeral=True,
        )
        embed = discord.Embed(
            title="✅  Ticket Resolved",
            description=(
                "Your support request has been marked as **resolved** by our team.\n\n"
                "If you have any further questions, please open a new ticket. "
                "Thank you for flying with Delta Air Lines — *Keep Climbing.*"
            ),
            color=DELTA_RED,
        )
        embed.set_footer(text=FOOTER_TEXT)
        await channel.send(embed=embed)

    # Global error handler
    @tree.error
    async def on_app_command_error(
        interaction: discord.Interaction,
        error: app_commands.AppCommandError,
    ) -> None:
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message(
                embed=error_embed(
                    "You do not have permission to use this command.\n"
                    "This command is restricted to **Delta Air Lines Staff** only."
                ),
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                embed=error_embed(f"An unexpected error occurred: {error}"),
                ephemeral=True,
            )


# ══════════════════════════════════════════════════════════════════════════════
# BOT CLASS & ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("delta-helpdesk")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True


class DeltaBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(command_prefix="!", intents=intents, help_command=None)

    async def setup_hook(self) -> None:
        self.add_view(AssistancePanelView())
        self.add_view(TicketActionView())
        register_commands(self.tree)
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


def run_health_server() -> None:
    """Tiny HTTP server so Render's free Web Service sees an open port."""
    port = int(os.getenv("PORT", "8080"))

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Delta Air Lines HelpDesk is online.")

        def log_message(self, *args) -> None:
            pass  # Silence HTTP access logs

    server = HTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()


def main() -> None:
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise RuntimeError(
            "DISCORD_TOKEN is not set. Copy .env.example to .env and fill in your bot token."
        )

    # Start the health-check server in a background thread
    thread = threading.Thread(target=run_health_server, daemon=True)
    thread.start()
    log.info("Health-check server started.")

    bot = DeltaBot()
    bot.run(token, log_handler=None)


if __name__ == "__main__":
    main()
