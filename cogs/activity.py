import discord
from discord.ext import commands, tasks
from datetime import datetime
from database.db import add_messages, add_voice_minutes, reset_status
 
#Минимальное количество людей в войсе чтобы считались очки
MIN_USERS_IN_VOICE = 2
 
class Activity(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_join_time = {}
 
    @commands.Cog.listener()
    async def on_ready(self):
        print('Activity cog ready')
        self.monthly_reset.start()
        self.voice_check.start()
 
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        add_messages(message.author.id, message.author.display_name)
 
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return
 
        #Зашёл в войс
        if before.channel is None and after.channel is not None:
            real_users = self._count_real_users(after.channel)
            # Начинаем считать только если в канале уже 2+ человека
            if real_users >= MIN_USERS_IN_VOICE:
                self.voice_join_time[member.id] = datetime.now()
 
        #Вышел из войса
        elif before.channel is not None and after.channel is None:
            self._save_voice_time(member)
 
            #Если в канале остался 1 человек убираем его из отслеживания
            remaining = self._count_real_users(before.channel)
            if remaining < MIN_USERS_IN_VOICE:
                for m in before.channel.members:
                    if not m.bot and m.id in self.voice_join_time:
                        self._save_voice_time(m)
 
        # Перешёл между каналами
        elif before.channel != after.channel:
            self._save_voice_time(member)
 
            real_users = self._count_real_users(after.channel)
            if real_users >= MIN_USERS_IN_VOICE:
                self.voice_join_time[member.id] = datetime.now()
 
            # Если в старом канале стало меньше 2 людей останавливаем им счётчик
            remaining = self._count_real_users(before.channel)
            if remaining < MIN_USERS_IN_VOICE:
                for m in before.channel.members:
                    if not m.bot and m.id in self.voice_join_time:
                        self._save_voice_time(m)
 
    def _count_real_users(self, channel) -> int:
        """Считает людей в канале без ботов и без замьюченных/заглушённых"""
        count = 0
        for m in channel.members:
            if m.bot:
                continue
            #Не считаем если сервер замьютил(server deaf/mute)
            if m.voice and (m.voice.deaf or m.voice.self_deaf):
                continue
            count += 1
        return count
 
    def _save_voice_time(self, member):
        if member.id not in self.voice_join_time:
            return
        joined_at = self.voice_join_time.pop(member.id)
        minutes = int((datetime.now() - joined_at).total_seconds() / 60)
        if minutes > 0:
            add_voice_minutes(member.id, member.display_name, minutes)
 
    #Проверка каждые 10 минут убираем одиночек из отслеживания
    @tasks.loop(minutes=10)
    async def voice_check(self):
        for guild in self.bot.guilds:
            for channel in guild.voice_channels:
                real_users = self._count_real_users(channel)
                if real_users < MIN_USERS_IN_VOICE:
                    for m in channel.members:
                        if not m.bot and m.id in self.voice_join_time:
                            self._save_voice_time(m)
 
    #сброс счетчика каждый месяц
    @tasks.loop(hours=720)
    async def monthly_reset(self):
        reset_status()
        print(f"[{datetime.now().strftime('%d.%m.%Y %H:%M')}] Активность сброшена за месяц")
 
        import config
        for guild in self.bot.guilds:
            channel = guild.get_channel(config.TEST_CHANNEL_ID)
            if channel:
                await channel.send("📊 Месяц закончился! Статистика активности обнулена.")
 
async def setup(bot):
    await bot.add_cog(Activity(bot))
 