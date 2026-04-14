import discord
from discord.ext import commands
from datetime import datetime
from database.db import add_messages, add_voice_minutes

class Activity(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_join_time = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        add_messages(message.author.id, message.author.display_name)
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return

        if before.channel is None and after.channel is not None:
            self.voice_join_time[member.id] = datetime.now()
        
        elif before.channel is not None and after.channel is None:
            self._save_voice_time(member)
        
        elif before.channel != after.channel:
            self._save_voice_time(member)
            self.voice_join_time[member.id] = datetime.now()
    
    def _save_voice_time(self, member):
        if member.id not in self.voice_join_time:
            return
        joined_at = self.voice_join_time.pop(member.id)
        minutes = int((datetime.now() - joined_at).total_seconds() / 60)
        if minutes > 0:
            add_voice_minutes(member.id, member.display_name, minutes)

async def setup(bot):
    await bot.add_cog(Activity(bot))
