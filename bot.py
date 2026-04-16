import discord
from discord.ext import commands
import os
import config
from database.db import init_db

async def main():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    intents.voice_states = True
    intents.presences = True

    bot = commands.Bot(command_prefix='!', intents=intents)

    @bot.event
    async def on_ready():
        print(f"ботяра запущен: {bot.user}")

    init_db()

    await bot.load_extension('cogs.activity')
    await bot.load_extension('cogs.banner')

    await bot.start(config.TOKEN)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())