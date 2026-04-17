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
        if ctx.author.id not in config.ALLOWED_USER_ID:
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

    def _truncate_name(self, draw, name: str, font, max_width: int) -> str:
        """Обрезает ник если он не влезает, добавляет '...'"""
        if draw.textlength(name, font=font) <= max_width:
            return name
        while len(name) > 0:
            name = name[:-1]
            if draw.textlength(name + "...", font=font) <= max_width:
                return name + "..."
        return "..."

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

        draw.text((width//2, 40), "Топ активных", font=font_title,
                fill=(255, 215, 0), anchor="mm")
        draw.text((width//2, 85), f"Месяц до {datetime.now().strftime('%d.%m.%Y')}",
                font=font_small, fill=(150, 150, 150), anchor="mm")
        draw.line([(50, 105), (850, 105)], fill=(70, 70, 90), width=2)

        draw.text((80,  115), "Игрок",      font=font_small, fill=(180, 180, 180))
        draw.text((480, 115), "Сообщений",  font=font_small, fill=(180, 180, 180))
        draw.text((650, 115), "Голос",      font=font_small, fill=(180, 180, 180))
        draw.text((800, 115), "Очки",       font=font_small, fill=(180, 180, 180))
        draw.line([(50, 140), (850, 140)], fill=(70, 70, 90), width=1)

        medals = ["1", "2", "3", "4.", "5."]
        colors = [(255,215,0),(192,192,192),(205,127,50),(255,255,255),(255,255,255)]

        MAX_NAME_WIDTH = 370

        for i, row in enumerate(top_users):
            username, messages, voice_minutes, score = row
            y = 160 + i * 52
            if i == 0:
                draw.rectangle([(50, y-5), (850, y+38)], fill=(50, 45, 20))

            #обрез для ника
            display_name = self._truncate_name(draw, username, font_name, MAX_NAME_WIDTH)

            draw.text((80,  y), f"{medals[i]}  {display_name}", font=font_name, fill=colors[i])
            draw.text((490, y), str(messages), font=font_name, fill=(150, 200, 255))

            h, m = divmod(voice_minutes, 60)
            voice_str = f"{h}ч {m}м" if h > 0 else f"{m}м"
            draw.text((655, y), voice_str,  font=font_name, fill=(150, 255, 200))
            draw.text((805, y), str(score), font=font_name, fill=colors[i])

        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        return buf

async def setup(bot):
    await bot.add_cog(Banner(bot))