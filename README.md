# Activity bot for discord server

Discord bot for tracking server member activity, displaying status via generated images

## Features

- Tracks messages and voice chat time for each member
- Displays a weekly Top 5 most active members as an image
- Shows total server member count and online status as a banner
- Restricted commands (only allowed user can trigger reports)
- Docker support

## Requirements

- python 3.11+
- Discord bot token([Discord Developer Portal](https://discord.com/developers/applications))
- The following Privileged Gateway Intents enabled:
    - Presence Intent
    - Server Member Intent
    - Message Content Intent

## Installation

1. Clone the repository
```bash
   git clone https://github.com/your_username/discord-bot.git
   cd discord-bot
```
2. Install dependencies
```bash
   pip install -r requirements.txt
```

3. Set up environment variables
```bash
   cp .env.example .env
```
   Then fill in your values in `.env`

4. Create the data directory
```bash
   mkdir data
```

5. Run the bot
```bash
   python bot.py
```

## Docker

```bash
# Build and start
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DISCORD_TOKEN` | Your bot token from Discord Developer Portal |
| `TEST_CHANNEL_ID` | Channel ID where the bot sends activity images |
| `ALLOWED_USER_ID` | Discord user ID allowed to trigger bot commands |

## Commands

| Command | Description | Access |
|---------|-------------|--------|
| `!баннер` | Sends a banner with total and online member count | Owner only |
| `!топ` | Sends a Top 5 most active members image | Owner only |

## Activity Scoring

| Action | Points |
|--------|--------|
| 1 message | 1 point |
| 1 minute in voice | 2 points |

Stats reset automatically every week after the top is posted.