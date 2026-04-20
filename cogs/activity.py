import discord
from discord.ext import commands, tasks
from datetime import datetime
from database.db import add_messages, add_voice_minutes, reset_status
import config
 
# Минимальное количество людей в войсе чтобы считались очки
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
 
        # Зашёл в войс
        if before.channel is None and after.channel is not None:
            if self._is_active(after) and self._count_real_users(after.channel) >= MIN_USERS_IN_VOICE:
                self.voice_join_time[member.id] = datetime.now()
 
        # Вышел из войса
        elif before.channel is not None and after.channel is None:
            self._save_voice_time(member)
 
            # Если в канале остался 1 человек убираем его из отслеживания
            if self._count_real_users(before.channel) < MIN_USERS_IN_VOICE:
                for m in before.channel.members:
                    if not m.bot and m.id in self.voice_join_time:
                        self._save_voice_time(m)
 
        # Перешёл между каналами
        elif before.channel != after.channel:
            self._save_voice_time(member)
 
            if self._is_active(after) and self._count_real_users(after.channel) >= MIN_USERS_IN_VOICE:
                self.voice_join_time[member.id] = datetime.now()
 
            if self._count_real_users(before.channel) < MIN_USERS_IN_VOICE:
                for m in before.channel.members:
                    if not m.bot and m.id in self.voice_join_time:
                        self._save_voice_time(m)
 
        # Изменил статус внутри канала (замьютился/включил наушники и т.д.)
        elif before.channel == after.channel:
            was_active = self._is_active(before)
            now_active = self._is_active(after)
 
            if was_active and not now_active:
                # Замьютился или надел наушники останавливаем счётчик
                self._save_voice_time(member)
 
            elif not was_active and now_active:
                # Размьютился — начинаем считать если в канале 2+ активных
                if self._count_real_users(after.channel) >= MIN_USERS_IN_VOICE:
                    self.voice_join_time[member.id] = datetime.now()
 
    def _is_active(self, voice_state) -> bool:
        """Активен ли пользователь не на мьюте и не в наушниках"""
        if voice_state is None:
            return False
        # self_mute сам замьютил микрофон
        # self_deaf сам надел наушники (заглушил всех)
        # mute/deaf сервер принудительно замьютил
        return not (
            voice_state.self_mute or
            voice_state.self_deaf or
            voice_state.mute or
            voice_state.deaf
        )
 
    def _count_real_users(self, channel) -> int:
        """Считает активных людей в канале (без ботов, без мьюта/деафа)"""
        count = 0
        for m in channel.members:
            if m.bot:
                continue
            if m.voice and self._is_active(m.voice):
                count += 1
        return count
 
    def _save_voice_time(self, member):
        if member.id not in self.voice_join_time:
            return
        joined_at = self.voice_join_time.pop(member.id)
        minutes = int((datetime.now() - joined_at).total_seconds() / 60)
        if minutes > 0:
            add_voice_minutes(member.id, member.display_name, minutes)
 
    # Проверка каждые 10 минут убираем одиночек и замьюченных
    @tasks.loop(minutes=10)
    async def voice_check(self):
        for guild in self.bot.guilds:
            for channel in guild.voice_channels:
                real_users = self._count_real_users(channel)
                for m in channel.members:
                    if m.bot or m.id not in self.voice_join_time:
                        continue
                    # Останавливаем если замьютился или остался один
                    if not self._is_active(m.voice) or real_users < MIN_USERS_IN_VOICE:
                        self._save_voice_time(m)
 
    # Надёжный сброс раз в месяц проверяем дату каждый день
    @tasks.loop(hours=24)
    async def monthly_reset(self):
        if datetime.now().day == 1:  # первое число каждого месяца
            reset_status()
            print(f"[{datetime.now().strftime('%d.%m.%Y %H:%M')}] Активность сброшена за месяц")
 
            for guild in self.bot.guilds:
                channel = guild.get_channel(config.TEST_CHANNEL_ID)
                if channel:
                    await channel.send("📊 Месяц закончился! Статистика активности обнулена.")
 
async def setup(bot):
    await bot.add_cog(Activity(bot))