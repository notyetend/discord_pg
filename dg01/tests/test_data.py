import pytest
import pprint
import asyncio
import random

from dg01.games import GameType
from dg01.manager_data import DataManager


class TestData:
    @pytest.fixture
    def user_id(self):
        return 111
    
    @pytest.fixture
    def channel_id(self):
        return random.randint(0, 1000)

    @pytest.fixture
    def game_type(self):
        return GameType.DIGIMON

    @pytest.fixture
    def game_data_manager(self):
        return DataManager()
    
    def test_create_table_sql(self, game_data_manager):
        print(f"""=== \n{game_data_manager.create_table_sql}\n===""")

    def test_default_user_data(self, game_data_manager):
        print(f"""=== \n{game_data_manager.default_user_data}\n===""")

    @pytest.mark.asyncio
    async def test_get_user_data(self, game_data_manager, user_id, game_type):
        user_data = await game_data_manager.get_user_data(user_id)
        pp = pprint.PrettyPrinter(indent=2, width=40)
        pp.pprint(user_data)

    @pytest.mark.asyncio
    async def test_update_user_data(self, game_data_manager, user_id, channel_id):
        data = await game_data_manager.get_user_data(user_id)
        data['channel_id'] = channel_id
        assert await game_data_manager.save_user_data(user_id, data)
    