import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import io
import config

class Banner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print('Banner cog ready')
    
    @commands.command(name='топ')
    async def top_command(self, ctx):
        if ctx.author.id != config.ALLOWED_USER_ID:
            await ctx.reply("У тебя нет прав")
            return
        await self._send_top(ctx.channel)

    async def _send_top(self, channel):
        from database.db import get_top_users
        top = get_top_users(config.TOP_LIMIT)

        if not top:
            await channel.send("Пока нет данных об активности!")
            return

        banner = self._generate_top_banner(top)
        await channel.send(file=discord.File(banner, filename="top.png"))

    def _generate_top_banner(self, top_users):
        width, height = 900, 450
        img = Image.new('RGB', (width, height), color=(30, 30, 40))
        draw = ImageDraw.Draw(img)

        try:
            font_title = ImageFont.truetype("arial.ttf", 40)
            font_name  = ImageFont.truetype("arial.ttf", 28)
            font_small = ImageFont.truetype("arial.ttf", 20)
        except:
            font_title = font_name = font_small = ImageFont.load_default()

        draw.text((width//2, 40), "🏆 Топ активных", font=font_title,
                fill=(255, 215, 0), anchor="mm")
        draw.text((width//2, 85), f"Неделя до {datetime.now().strftime('%d.%m.%Y')}",
                font=font_small, fill=(150, 150, 150), anchor="mm")
        draw.line([(50, 105), (850, 105)], fill=(70, 70, 90), width=2)

        draw.text((80,  115), "Игрок",      font=font_small, fill=(180, 180, 180))
        draw.text((480, 115), "Сообщений",  font=font_small, fill=(180, 180, 180))
        draw.text((650, 115), "Голос",      font=font_small, fill=(180, 180, 180))
        draw.text((800, 115), "Очки",       font=font_small, fill=(180, 180, 180))
        draw.line([(50, 140), (850, 140)], fill=(70, 70, 90), width=1)

        medals = ["🥇", "🥈", "🥉", "4.", "5."]
        colors = [(255,215,0),(192,192,192),(205,127,50),(255,255,255),(255,255,255)]

        for i, row in enumerate(top_users):
            username, messages, voice_minutes, score = row
            y = 160 + i * 52
            if i == 0:
                draw.rectangle([(50, y-5), (850, y+38)], fill=(50, 45, 20))

            draw.text((80,  y), f"{medals[i]}  {username}", font=font_name, fill=colors[i])
            draw.text((490, y), str(messages), font=font_name, fill=(150, 200, 255))

            h, m = divmod(voice_minutes, 60)
            voice_str = f"{h}ч {m}м" if h > 0 else f"{m}м"
            draw.text((655, y), voice_str,  font=font_name, fill=(150, 255, 200))
            draw.text((805, y), str(score), font=font_name, fill=colors[i])

        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        return buf

    @commands.command(name='баннер')
    async def banner_command(self, ctx):
        if ctx.author.id != config.ALLOWED_USER_ID:
            await ctx.reply('No permission')
            return
        await self._send_banner(ctx.channel)
    
    async def _send_banner(self, channel):
        guild = channel.guild

        total = guild.member_count
        bots = sum(1 for m in guild.members if m.bot)
        humans = total -  bots

        online = sum(1 for m in guild.members
                    if m.status != discord.Status.offline and not m.bot)
        
        banner = self._generate_banner(guild.name, humans, online)
        await channel.send(file=discord.File(banner, filename="banner.png"))

    def _generate_banner(self, server_name: str, total: int, online: int):
        width, height = 900, 400
        img = Image.new('RGB', (width, height), color=(30, 30, 40))
        draw = ImageDraw.Draw(img)

        try:
            font_big    = ImageFont.truetype("arial.ttf", 56)
            font_title  = ImageFont.truetype("arial.ttf", 36)
            font_medium = ImageFont.truetype("arial.ttf", 28)
            font_small  = ImageFont.truetype("arial.ttf", 20)
        except:
            font_big = font_title = font_medium = font_small = ImageFont.load_default()

        # Фоновые декоративные круги
        draw.ellipse([(-60, -60), (160, 160)],   fill=(40, 40, 60))
        draw.ellipse([(760, 260), (980, 480)],   fill=(40, 40, 60))

        # Название сервера
        draw.text((width // 2, 60), server_name, font=font_title,
                fill=(255, 215, 0), anchor="mm")

        # Разделитель
        draw.line([(100, 100), (800, 100)], fill=(70, 70, 90), width=2)

        # Блок — всего участников
        draw.rectangle([(80, 130), (420, 290)], fill=(40, 40, 55), outline=(70, 70, 90))
        draw.text((250, 175), str(total), font=font_big,
                fill=(255, 255, 255), anchor="mm")
        draw.text((250, 240), "👥 Всего участников", font=font_medium,
                fill=(180, 180, 200), anchor="mm")

        # Блок — онлайн
        draw.rectangle([(480, 130), (820, 290)], fill=(40, 55, 40), outline=(70, 90, 70))
        draw.text((650, 175), str(online), font=font_big,
                fill=(100, 255, 100), anchor="mm")
        draw.text((650, 240), "🟢 Сейчас онлайн", font=font_medium,
                fill=(150, 220, 150), anchor="mm")

        # Дата обновления
        date_str = datetime.now().strftime("%d.%m.%Y %H:%M")
        draw.text((width // 2, 340), f"Обновлено: {date_str}", font=font_small,
                fill=(100, 100, 120), anchor="mm")

        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        return buf

async def setup(bot):
    await bot.add_cog(Banner(bot))