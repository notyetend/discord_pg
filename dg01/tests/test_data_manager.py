import pytest
import os
import aiosqlite
from pathlib import Path
from datetime import datetime, timezone
from dg01.data_manager import DataManager
from dg01.digimon_data import DigimonDataFields

@pytest.fixture
def test_db_path(tmp_path):
    """테스트용 임시 데이터베이스 경로를 생성하는 fixture"""
    db_path = tmp_path / "test_game.db"
    return str(db_path)

@pytest.fixture
def data_manager(test_db_path):
    """테스트용 DataManager 인스턴스를 생성하는 fixture"""
    manager = DataManager(db_path=test_db_path)
    return manager

@pytest.fixture
def sample_user_data():
    """테스트용 샘플 사용자 데이터"""
    return {
        'user_id': 12345,
        'channel_id': 67890,
        'stage_idx': 1,
        'count': 10,
        'battles_won': 5,
        'battles_lost': 2,
        'last_cheer': None,
        'is_copying': True,
        'evolution_started': None,
        'last_played': datetime.now(timezone.utc).isoformat()
    }

@pytest.mark.asyncio
async def test_init_db(data_manager, test_db_path):
    """데이터베이스 초기화 테스트"""
    # DB 파일이 생성되었는지 확인
    assert os.path.exists(test_db_path)
    
    # 테이블이 생성되었는지 확인
    async with aiosqlite.connect(test_db_path) as db:
        async with db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='user_data'"
        ) as cursor:
            table = await cursor.fetchone()
            assert table is not None
            assert table[0] == 'user_data'

@pytest.mark.asyncio
async def test_get_or_create_user_data_new_user(data_manager):
    """새로운 사용자 데이터 생성 테스트"""
    user_id = 99999
    user_data = await data_manager.get_or_create_user_data(user_id)
    print(f"=== {user_data} ===")
    
    # 기본값 확인
    assert user_data['user_id'] == user_id  # default value from DigimonDataFields
    assert user_data['stage_idx'] == 0
    assert user_data['count'] == 0
    assert user_data['battles_won'] == 0
    assert user_data['battles_lost'] == 0

@pytest.mark.asyncio
async def test_get_or_create_user_data_existing_user(data_manager, sample_user_data):
    """기존 사용자 데이터 조회 테스트"""
    
    # 데이터 조회
    _ = await data_manager.get_or_create_user_data(sample_user_data['user_id'])
    await data_manager.update_user_data(sample_user_data['user_id'], sample_user_data)
    user_data = await data_manager.get_or_create_user_data(sample_user_data['user_id'])
    
    # 데이터 확인
    assert user_data['user_id'] == sample_user_data['user_id']
    assert user_data['channel_id'] == sample_user_data['channel_id']
    assert user_data['stage_idx'] == sample_user_data['stage_idx']
    assert user_data['count'] == sample_user_data['count']

@pytest.mark.asyncio
async def test_update_user_data(data_manager, sample_user_data):
    """사용자 데이터 업데이트 테스트"""
    user_id = sample_user_data['user_id']
    
    # 데이터 업데이트
    _ = await data_manager.get_or_create_user_data(user_id)
    success = await data_manager.update_user_data(user_id, sample_user_data)
    assert success is True
    updated_data = await data_manager.get_or_create_user_data(user_id)
    
    # 업데이트된 데이터 확인
    
    assert updated_data['stage_idx'] == sample_user_data['stage_idx']
    assert updated_data['count'] == sample_user_data['count']
    assert updated_data['battles_won'] == sample_user_data['battles_won']
    assert updated_data['battles_lost'] == sample_user_data['battles_lost']

@pytest.mark.asyncio
async def test_update_user_data_invalid_input(data_manager):
    """잘못된 입력으로 사용자 데이터 업데이트 시도 테스트"""
    # 잘못된 데이터 형식으로 업데이트 시도
    success = await data_manager.update_user_data(12345, None)
    assert success is False
    
    success = await data_manager.update_user_data(12345, "invalid_data")
    assert success is False

def test_create_table_sql(data_manager):
    """CREATE TABLE SQL 쿼리 생성 테스트"""
    sql = data_manager.create_table_sql
    
    # 필수 필드들이 SQL에 포함되어 있는지 확인
    assert "CREATE TABLE IF NOT EXISTS user_data" in sql
    assert "user_id INTEGER PRIMARY KEY" in sql
    assert "channel_id INTEGER NOT NULL" in sql
    assert "stage_idx INTEGER NOT NULL" in sql
    assert "count INTEGER" in sql
    assert "battles_won INTEGER" in sql
    assert "battles_lost INTEGER" in sql

def test_default_user_data(data_manager):
    """기본 사용자 데이터 생성 테스트"""
    default_data = data_manager.default_user_data
    
    # 필수 필드들의 기본값 확인
    assert 'user_id' in default_data
    assert 'channel_id' in default_data
    assert 'stage_idx' in default_data
    assert 'count' in default_data
    assert 'battles_won' in default_data
    assert 'battles_lost' in default_data

def test_columns(data_manager):
    """컬럼 목록 테스트"""
    columns = data_manager.columns
    
    # 필수 컬럼들이 포함되어 있는지 확인
    assert 'user_id' in columns
    assert 'channel_id' in columns
    assert 'stage_idx' in columns
    assert 'count' in columns
    assert 'battles_won' in columns
    assert 'battles_lost' in columns
    assert 'last_cheer' in columns
    assert 'is_copying' in columns
    assert 'evolution_started' in columns
    assert 'last_played' in columns

@pytest.mark.asyncio
async def test_get_all_user_data_empty(data_manager):
    """데이터가 없는 경우 전체 유저 데이터 조회 테스트"""
    users = await data_manager.get_all_user_data()
    
    assert isinstance(users, list)
    assert len(users) == 0

@pytest.mark.asyncio
async def test_get_all_user_data_with_users(data_manager):
    """여러 유저 데이터가 있는 경우 전체 유저 데이터 조회 테스트"""
    # 테스트 데이터 생성
    test_users = [
        {
            'user_id': 12345,
            'channel_id': 67890,
            'stage_idx': 1,
            'count': 100,
            'battles_won': 5,
            'battles_lost': 2,
            'is_copying': True,
            'evolution_started': None,
            'last_played': None
        },
        {
            'user_id': 23456,
            'channel_id': 78901,
            'stage_idx': 2,
            'count': 200,
            'battles_won': 10,
            'battles_lost': 3,
            'is_copying': True,
            'evolution_started': None,
            'last_played': None
        }
    ]
    
    # 테스트 데이터 저장
    for user_data in test_users:
        await data_manager.update_user_data(user_data['user_id'], user_data)
    
    # 전체 데이터 조회
    users = await data_manager.get_all_user_data()
    print(f"===== {users=} =====")
    
    # 검증
    assert isinstance(users, list)
    assert len(users) == 2
    
    # 각 사용자 데이터 검증
    for user_data in users:
        original_data = next(u for u in test_users if u['user_id'] == user_data['user_id'])
        assert user_data['channel_id'] == original_data['channel_id']
        assert user_data['stage_idx'] == original_data['stage_idx']
        assert user_data['count'] == original_data['count']
        assert user_data['battles_won'] == original_data['battles_won']
        assert user_data['battles_lost'] == original_data['battles_lost']

@pytest.mark.asyncio
async def test_get_all_user_data_with_null_values(data_manager):
    """NULL 값이 포함된 유저 데이터 조회 테스트"""
    test_user = {
        'user_id': 12345,
        'channel_id': 67890,
        'stage_idx': 1,
        'count': 100,
        'battles_won': 5,
        'battles_lost': 2,
        'is_copying': True,
        'evolution_started': None,  # NULL 값
        'last_played': None        # NULL 값
    }
    
    # 테스트 데이터 저장
    await data_manager.update_user_data(test_user['user_id'], test_user)
    
    # 데이터 조회
    users = await data_manager.get_all_user_data()
    
    # 검증
    assert len(users) == 1
    user_data = users[0]
    assert user_data['evolution_started'] is None
    assert user_data['last_played'] is None

@pytest.mark.asyncio
async def test_get_all_user_data_error_handling(data_manager):
    """데이터베이스 에러 상황 테스트"""
    # 데이터베이스 경로를 잘못된 경로로 변경
    data_manager.db_path = '/invalid/path/to/database.db'
    
    with pytest.raises(Exception):
        await data_manager.get_all_user_data()

@pytest.mark.asyncio
async def test_get_all_user_data_column_types(data_manager):
    """데이터 타입 정확성 테스트"""
    test_user = {
        'user_id': 12345,
        'channel_id': 67890,
        'stage_idx': 1,
        'count': 100,
        'battles_won': 5,
        'battles_lost': 2,
        'is_copying': -1,
        'evolution_started': None,
        'last_played': "2024-01-01T00:00:00Z"
    }
    
    # 테스트 데이터 저장
    await data_manager.update_user_data(test_user['user_id'], test_user)
    
    # 데이터 조회
    users = await data_manager.get_all_user_data()
    
    # 타입 검증
    user_data = users[0]
    assert isinstance(user_data['user_id'], int)
    assert isinstance(user_data['channel_id'], int)
    assert isinstance(user_data['stage_idx'], int)
    assert isinstance(user_data['count'], int)
    assert isinstance(user_data['battles_won'], int)
    assert isinstance(user_data['battles_lost'], int)
    assert isinstance(user_data['is_copying'], int)
    assert user_data['evolution_started'] is None
    assert isinstance(user_data['last_played'], str)