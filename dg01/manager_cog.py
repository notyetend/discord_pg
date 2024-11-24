from discord.ext import commands

from dg01.games import GameType, MAPPING__GAME_TYPE__COG_CLASS
from dg01.errors import GameError


class CogManager:
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def add_cog(self, game_type: GameType):
        CogClass = MAPPING__GAME_TYPE__COG_CLASS.get(game_type)
        if CogClass:
            await self.bot.add_cog(CogClass(self.bot))
            return True
        else:
            raise GameError(f"Unknown game type for cog: {game_type}")

    async def remove_cog(self, game_type: GameType):
        CogClass = MAPPING__GAME_TYPE__COG_CLASS.get(game_type)
        if CogClass:
            await self.bot.remove_cog(CogClass(self.bot).qualified_name)
            return True
        else:
            raise GameError(f"Unknown game type for cog: {game_type}")