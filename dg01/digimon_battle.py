from dataclasses import dataclass
from typing import Optional
import random
import discord
from discord.ext import commands

from dg01.errors import setup_logger
from dg01.game_events import EventType, EventBattleWin, EventBattleLose, EventBattleItemGet


logger = setup_logger(__name__)


class BattleView:
    """전투 관련 출력을 담당하는 클래스"""
    
    async def send_battle_win(self, channel: discord.TextChannel, user_id: int, battles_won: int, battles_lost: int) -> None:
        """전투 승리 메시지 전송"""
        embed = discord.Embed(
            title="⚔️ 전투 승리!",
            description="전투에서 승리했습니다!",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="📊 전투 기록",
            value=f"총 전적: {battles_won}승 {battles_lost}패",
            inline=False
        )
        
        await channel.send(embed=embed)

    async def send_battle_item_get(self, channel: discord.TextChannel, user_id: int, item_id: int) -> None:
        """전투 아이템 획득 메시지 전송"""
        embed = discord.Embed(
            title="🎁 아이템 획득!",
            description="전투 승리로 특별한 아이템을 획득했습니다!",
            color=discord.Color.gold()
        )
        
        item_descriptions = {
            1: "강화된 방어구",
            2: "공격력 증가 아이템",
            3: "회복 아이템"
        }
        
        item_description = item_descriptions.get(item_id, "알 수 없는 아이템")
        embed.add_field(
            name="획득한 아이템",
            value=item_description,
            inline=False
        )
        
        await channel.send(embed=embed)

    async def send_battle_lose(self, channel: discord.TextChannel, user_id: int, 
                             count_lost: int, battles_won: int, battles_lost: int, 
                             remaining_count: int) -> None:
        """전투 패배 메시지 전송"""
        embed = discord.Embed(
            title="💔 전투 패배",
            description=f"전투에서 패배했습니다... {count_lost:,} 개체를 잃었습니다.\n!치료 해주세요.",
            color=discord.Color.red()
        )

        embed.add_field(
            name="📊 전투 기록",
            value=f"총 전적: {battles_won}승 {battles_lost}패",
            inline=False
        )
        
        embed.add_field(
            name="💪 현재 상태",
            value=f"남은 개체 수: {remaining_count:,}",
            inline=False
        )

        await channel.send(embed=embed)


class BattleHandler:
    """전투 관련 로직을 처리하는 클래스"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.view = BattleView()
    
    async def handle_battle_win(self, event: EventBattleWin, battles_won: int, battles_lost: int) -> None:
        """전투 승리 처리"""
        channel = self.bot.get_channel(event.channel_id)
        if not channel:
            logger.error(f"Channel {event.channel_id} not found for battle win event")
            return

        await self.view.send_battle_win(
            channel=channel,
            user_id=event.user_id,
            battles_won=battles_won,
            battles_lost=battles_lost
        )

    async def handle_battle_item_get(self, event: EventBattleItemGet) -> None:
        """전투 아이템 획득 처리"""
        channel = self.bot.get_channel(event.channel_id)
        if not channel:
            logger.error(f"Channel {event.channel_id} not found for battle item event")
            return

        await self.view.send_battle_item_get(
            channel=channel,
            user_id=event.user_id,
            item_id=event.obtained_item_id
        )

    async def handle_battle_lose(self, event: EventBattleLose, 
                               battles_won: int, battles_lost: int, 
                               remaining_count: int) -> None:
        """전투 패배 처리"""
        channel = self.bot.get_channel(event.channel_id)
        if not channel:
            logger.error(f"Channel {event.channel_id} not found for battle lose event")
            return

        await self.view.send_battle_lose(
            channel=channel,
            user_id=event.user_id,
            count_lost=event.count_lost,
            battles_won=battles_won,
            battles_lost=battles_lost,
            remaining_count=remaining_count
        )