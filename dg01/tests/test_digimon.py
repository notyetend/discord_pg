import pytest

from dg01.data_manager import DataManager
from dg01.digimon_data import DigimonDataFields

@pytest.mark.asyncio
async def test_sth():
    data_manager = DataManager()
    user_data = await data_manager.get_user_data(user_id=12345)
    print(f"=== {user_data=} ===")
    digimon = DigimonDataFields(**user_data)
    print(f"=== {digimon=} ===")
