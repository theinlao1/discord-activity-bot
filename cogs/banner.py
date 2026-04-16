import discord
from discord.ext import commands, tasks
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import io
import aiohttp
import config

class Banner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Banner cog ready')
        self.auto_update.start()

    # top users 
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

        draw.text((width//2, 40), "Топ активных", font=font_title,
                fill=(255, 215, 0), anchor="mm")
        draw.text((width//2, 85), f"Неделя до {datetime.now().strftime('%d.%m.%Y')}",
                font=font_small, fill=(150, 150, 150), anchor="mm")
        draw.line([(50, 105), (850, 105)], fill=(70, 70, 90), width=2)

        draw.text((80,  115), "Игрок",      font=font_small, fill=(180, 180, 180))
        draw.text((480, 115), "Сообщений",  font=font_small, fill=(180, 180, 180))
        draw.text((650, 115), "Голос",      font=font_small, fill=(180, 180, 180))
        draw.text((800, 115), "Очки",       font=font_small, fill=(180, 180, 180))
        draw.line([(50, 140), (850, 140)], fill=(70, 70, 90), width=1)

        medals = ["1", "2", "3", "4.", "5."]
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


    # banner generator
    @commands.command(name='баннер')
    async def banner_command(self, ctx):
        if ctx.author.id != config.ALLOWED_USER_ID:
            await ctx.reply("У тебя нет прав, сибастьян 🙄")
            return

        if not ctx.message.attachments:
            await ctx.reply("Прикрепи картинку к сообщению! Например: `!баннер` + картинка")
            return

        attachment = ctx.message.attachments[0]
        if not attachment.content_type or not attachment.content_type.startswith("image"):
            await ctx.reply("Прикрепи именно картинку!")
            return

        await ctx.reply("Обновляю баннер сервера... ⏳")

        # Скачиваем картинку
        async with aiohttp.ClientSession() as session:
            async with session.get(attachment.url) as resp:
                img_bytes = await resp.read()

        guild = ctx.guild
        total, online = self._get_stats(guild)

        banner_bytes = self._generate_server_banner(img_bytes, total, online)
        await guild.edit(banner=banner_bytes.read())
        await ctx.reply("✅ Баннер сервера обновлён!")

    @commands.command(name='тестбаннер')
    async def test_banner_command(self, ctx):
        if ctx.author.id != config.ALLOWED_USER_ID:
            await ctx.reply("У тебя нет прав, сибастьян 🙄")
            return

        if not ctx.message.attachments:
            await ctx.reply("Прикрепи картинку к сообщению!")
            return

        attachment = ctx.message.attachments[0]
        if not attachment.content_type or not attachment.content_type.startswith("image"):
            await ctx.reply("Прикрепи именно картинку!")
            return

        async with aiohttp.ClientSession() as session:
            async with session.get(attachment.url) as resp:
                img_bytes = await resp.read()

        guild = ctx.guild
        total, online = self._get_stats(guild)

        banner_bytes = self._generate_server_banner(img_bytes, total, online)
        await ctx.channel.send(
            content="Вот как будет выглядеть баннер:",
            file=discord.File(banner_bytes, filename="test_banner.png")
        )

    # updating data
    @commands.command(name='обновить')
    async def update_command(self, ctx):
        if ctx.author.id != config.ALLOWED_USER_ID:
            await ctx.reply("У тебя нет прав, сибастьян 🙄")
            return
        await self._update_banner(ctx.guild)
        await ctx.reply("✅ Статистика на баннере обновлена!")

    @tasks.loop(hours=1)
    async def auto_update(self):
        for guild in self.bot.guilds:
            await self._update_banner(guild)

    async def _update_banner(self, guild):
        if not guild.banner:
            return

        async with aiohttp.ClientSession() as session:
            async with session.get(guild.banner.url) as resp:
                img_bytes = await resp.read()

        total, online = self._get_stats(guild)
        banner_bytes = self._generate_server_banner(img_bytes, total, online)
        await guild.edit(banner=banner_bytes.read())


    def _get_stats(self, guild):
        total = guild.member_count
        bots = sum(1 for m in guild.members if m.bot)
        humans = total - bots
        online = sum(
            1 for m in guild.members
            if m.status != discord.Status.offline and not m.bot
        )
        return humans, online

    def _generate_server_banner(self, img_bytes: bytes, total: int, online: int):
        W, H = 960, 540

        bg = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        bg = bg.resize((W, H), Image.LANCZOS)

        draw = ImageDraw.Draw(bg)

        try:
            font_big    = ImageFont.truetype("arial.ttf", 64)
            font_medium = ImageFont.truetype("arialbd.ttf", 32)  # жирный
        except:
            font_big = font_medium = ImageFont.load_default()

        padding = 80
        block_w, block_h = 280, 120
        x1, y1 = padding, H - block_h - padding
        x2, y2 = x1 + block_w, y1 + block_h

        draw.rectangle([x1, y1, x2, y2], fill=(20, 20, 30))
        draw.rectangle([x1, y1, x2, y2], outline=(255, 255, 255), width=2)

        # Число участников
        draw.text(
            (x1 + block_w // 2, y1 + 38),
            str(total),
            font=font_big,
            fill=(255, 255, 255),
            anchor="mm"
        )

        # Подпись
        draw.text(
            (x1 + block_w // 2, y1 + 85),
            "УЧАСТНИКОВ",
            font=font_medium,
            fill=(200, 200, 200),
            anchor="mm"
        )

        buf = io.BytesIO()
        bg.save(buf, format="PNG")
        buf.seek(0)
        return buf

async def setup(bot):
    await bot.add_cog(Banner(bot))