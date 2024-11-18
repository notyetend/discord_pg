import discord
from discord.ext import commands


token = "blabla"

# 봇 생성
intents = discord.Intents.default()
intents.members = True
intents.message_content = True  # 메시지 내용 읽기 권한

bot = commands.Bot(command_prefix='!', intents=intents)


# 봇이 준비되었을 때 실행
@bot.event
async def on_ready():
    print(f'{bot.user} 봇이 실행되었습니다!')

# !hello 명령어
@bot.command()
async def hello(ctx):
    await ctx.send(f'안녕하세요, {ctx.author.name}님!')


@bot.command()
async def add(ctx, left: int, right: int):
    """Adds two numbers together."""
    await ctx.send(left + right)


# !따라해 명령어
@bot.command()
async def 따라해(ctx, *, message):
    await ctx.send(message)

# 봇 실행
bot.run(token)


