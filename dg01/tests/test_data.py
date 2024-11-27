import pytest
import pprint
import asyncio
import random

from dg01.data_manager import DataManager


class TestData:
    @pytest.fixture
    def user_id(self):
        return 111
    
    @pytest.fixture
    def channel_id(self):
        return random.randint(0, 1000)

    @pytest.fixture
    def data_manager(self):
        return DataManager()
    
    def test_create_table_sql(self, data_manager):
        print(f"""=== \n{data_manager.create_table_sql}\n===""")

    def test_default_user_data(self, data_manager):
        print(f"""=== \n{data_manager.default_user_data}\n===""")

    @pytest.mark.asyncio
    async def test_get_user_data(self, data_manager, user_id):
        user_data = await data_manager.get_user_data(user_id)
        pp = pprint.PrettyPrinter(indent=2, width=40)
        pp.pprint(user_data)

    @pytest.mark.asyncio
    async def test_update_user_data(self, data_manager, user_id, channel_id):
        # data = await data_manager.get_user_data(user_id)
        # data['channel_id'] = channel_id

        data = {'user_id': 328501834203398146, 'channel_id': 0, 'stage_idx': 1, 'count': 1, 'data_absorbed': 0, 'battles_won': 0, 'battles_lost': 0, 'last_cheer': None, 'is_copying': 1, 'evolution_started': -1, 'last_played': ''}
        assert await data_manager.update_user_data(328501834203398146, data)
    