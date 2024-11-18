import discord
from discord.ext import commands, tasks
import json
import random
from datetime import datetime

# 봇 설정
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# 디지몬 데이터 (레벨별 진화)
DIGIMON_EVOLUTION = {
    'egg': ['코로몬'],
    'baby': ['포요몬', '푸니몬'],
    'rookie': ['아구몬', '가브몬', '피요몬'],
    'champion': ['그레이몬', '가루루몬', '버드라몬']
}

class DigimonGame:
    def __init__(self):
        self.players = {}
        self.load_data()
    
    def load_data(self):
        try:
            with open('digimon_data.json', 'r') as f:
                self.players = json.load(f)
        except FileNotFoundError:
            self.players = {}
    
    def save_data(self):
        with open('digimon_data.json', 'w') as f:
            json.dump(self.players, f)
    
    def create_digimon(self, user_id):
        if str(user_id) not in self.players:
            self.players[str(user_id)] = {
                'digimon': random.choice(DIGIMON_EVOLUTION['egg']),
                'level': 'egg',
                'exp': 0,
                'hunger': 100,
                'happiness': 100,
                'last_feed': str(datetime.now()),
                'last_play': str(datetime.now())
            }
            self.save_data()
            return "디지몬 알이 부화했습니다! 당신의 디지몬은 코로몬입니다!"
        return "이미 디지몬을 키우고 있습니다!"

    def feed_digimon(self, user_id):
        if str(user_id) not in self.players:
            return "먼저 디지몬을 생성해주세요! (!디지몬시작)"
        
        player = self.players[str(user_id)]
        player['hunger'] = min(100, player['hunger'] + 30)
        player['last_feed'] = str(datetime.now())
        self.save_data()
        return f"디지몬에게 먹이를 주었습니다! 현재 포만감: {player['hunger']}%"

    def play_digimon(self, user_id):
        if str(user_id) not in self.players:
            return "먼저 디지몬을 생성해주세요! (!디지몬시작)"
        
        player = self.players[str(user_id)]
        player['happiness'] = min(100, player['happiness'] + 20)
        player['exp'] += 10
        player['last_play'] = str(datetime.now())
        self.save_data()
        return f"디지몬과 놀아주었습니다! 행복도: {player['happiness']}%, EXP: {player['exp']}"

    def check_status(self, user_id):
        if str(user_id) not in self.players:
            return "디지몬을 보유하고 있지 않습니다!"
        
        player = self.players[str(user_id)]
        return f"""디지몬 상태
이름: {player['digimon']}
레벨: {player['level']}
경험치: {player['exp']}
포만감: {player['hunger']}%
행복도: {player['happiness']}%"""

game = DigimonGame()

@bot.event
async def on_ready():
    print(f'{bot.user} 디지몬 게임 봇이 시작되었습니다!')
    decrease_stats.start()

@tasks.loop(minutes=30)  # 30분마다 스탯 감소
async def decrease_stats():
    for user_id in game.players:
        player = game.players[user_id]
        player['hunger'] = max(0, player['hunger'] - 5)
        player['happiness'] = max(0, player['happiness'] - 3)
    game.save_data()

@bot.command(name="디지몬시작")
async def start_game(ctx):
    response = game.create_digimon(ctx.author.id)
    await ctx.send(response)

@bot.command(name="먹이주기")
async def feed(ctx):
    response = game.feed_digimon(ctx.author.id)
    await ctx.send(response)

@bot.command(name="놀아주기")
async def play(ctx):
    response = game.play_digimon(ctx.author.id)
    await ctx.send(response)

@bot.command(name="상태확인")
async def status(ctx):
    response = game.check_status(ctx.author.id)
    await ctx.send(response)

bot.run("token_string")