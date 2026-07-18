# Delta Air Lines HelpDesk Discord Bot

A professional Delta Air Lines branded Discord support bot built with discord.py 2.x.

## Run & Operate

```bash
cd bot
pip install -r requirements.txt
cp .env.example .env   # then fill in DISCORD_TOKEN
python main.py
```

## Stack

- Python 3.10+, discord.py 2.3.2
- python-dotenv for environment variable loading

## Where Things Live

```
bot/
├── main.py      — Bot entry point, login, persistent view registration
├── config.py    — All IDs, colours, branding constants (edit this to configure)
├── embeds.py    — All Discord embed factory functions
├── views.py     — UI: AssistancePanelView (dropdown), CloseTicketButton
├── tickets.py   — Ticket close orchestration
├── commands.py  — All slash commands (/assistance panel, /close, /connected, /resolved)
└── utils.py     — Shared helpers (permission checks, channel creation, duplicate guard)
```

## Architecture Decisions

- **Persistent views** (`timeout=None` + `add_view` in `setup_hook`) so buttons/dropdowns survive bot restarts.
- **Ticket ownership stored in channel topic** (user ID string) — no database needed.
- **`config.py` as single source of truth** for all IDs; adding a new ticket category only requires a new entry in `TICKET_CONFIG`.
- **Staff-only commands guarded** with `app_commands.check` using `STAFF_ROLE_ID`.
- **Ephemeral staff confirmations** — staff see "Message sent successfully", users see the full branded embed.

## User Preferences

- All IDs and branding live in `config.py` for easy updates.
- New ticket categories: add a row to `TICKET_CONFIG` in `config.py` — no other file changes needed.

## Gotchas

- Run `python main.py` from inside the `bot/` directory.
- The bot needs **Server Members Intent** enabled in the Discord Developer Portal.
- Slash commands can take up to 1 hour to propagate globally after first sync. Use guild-scoped sync during development (see comment in `main.py`).
- `DISCORD_TOKEN` must be set in `.env` (copy `.env.example`).
