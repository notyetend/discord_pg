import os
import sqlite3
import aiosqlite
from typing import Optional, Dict, Any, List
from dg01.digimon_data import DigimonDataFields
from dg01.errors import setup_logger, GameError


logger = setup_logger(__name__)


class DataManager:
    def __init__(self, db_path: str = '__game_data/game.db', table_name: str = 'user_data'):
        """
        GameDataManager 초기화
        
        Args:
            db_path (str): 데이터베이스 파일 경로
        """
        self.db_path = db_path
        self.table_name = table_name
        self.fields = DigimonDataFields()
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()

    @property
    def create_table_sql(self) -> str:
        """테이블 생성 SQL 쿼리 생성"""
        fields = []
        for field_name, field_info in self.fields.__dataclass_fields__.items():
            metadata = field_info.metadata
            field_def = [
                field_name,
                metadata.get("type", "TEXT")
            ]
            
            if metadata.get("primary_key"):
                field_def.append("PRIMARY KEY")
            if not metadata.get("nullable", True):
                field_def.append("NOT NULL")
            if "default" in metadata:
                default_value = metadata["default"]
                if isinstance(default_value, str):
                    field_def.append(f"DEFAULT '{default_value}'")
                else:
                    field_def.append(f"DEFAULT {default_value}")
                
            fields.append(" ".join(field_def))
            
        return f"""CREATE TABLE IF NOT EXISTS {self.table_name} (\n\t{'\n\t, '.join(fields)}\n)"""

    @property
    def default_user_data(self) -> Dict[str, Any]:
        """기본 사용자 데이터"""
        return {
            field_name: field_info.default
            for field_name, field_info in self.fields.__dataclass_fields__.items()
            if "default" in field_info.metadata
        }

    @property
    def columns(self) -> List[str]:
        """컬럼 목록"""
        return list(self.fields.__dataclass_fields__.keys())

    def _init_db(self) -> None:
        """데이터베이스와 테이블을 초기화합니다."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(self.create_table_sql)
        except sqlite3.Error as e:
            logger.error(f"데이터베이스 초기화 실패: {e}")
            raise

    async def get_or_create_user_data(self, user_id: int) -> Dict[str, Any]:
        """
        사용자의 게임 데이터를 불러옵니다.
        
        Args:
            user_id (int): 사용자 ID
            
        Returns:
            Dict[str, Any]: 사용자 게임 데이터
        """
        async with aiosqlite.connect(self.db_path) as db:
            try:
                async with db.execute(
                    f'SELECT {", ".join(self.columns)} FROM {self.table_name} WHERE user_id = ?',
                    (user_id,)
                ) as cursor:
                    row = await cursor.fetchone()
                    
                if row is None:
                    # 새 사용자 데이터 생성
                    user_data = self.default_user_data.copy()
                    
                    placeholders = ", ".join(["?"] * len(self.columns))
                    values = [
                        user_id,
                        *[user_data.get(col) for col in self.columns[1:]]
                    ]
                    
                    await db.execute(
                        f"""
                        INSERT INTO {self.table_name} (
                            {", ".join(self.columns)}
                        ) VALUES ({placeholders})
                        """,
                        values
                    )
                    await db.commit()

                    async with db.execute(
                        f'SELECT {", ".join(self.columns)} FROM {self.table_name} WHERE user_id = ?',
                        (user_id,)
                    ) as cursor:
                        row = await cursor.fetchone()
                        if row is None:
                            raise GameError("Fail to fetch data.")
                else:
                    pass
                
                return {
                    self.columns[i]: (
                        None if row[i] == ''
                        else row[i]
                    )
                    for i in range(len(self.columns))
                }
                
            except Exception as e:
                logger.error(f"데이터 로드 실패 (user_id: {user_id}): {e}")
                raise


    async def create_user_data(self, user_id: int) -> Dict[str, Any]:
        """
        사용자의 게임 데이터를 불러옵니다.
        
        Args:
            user_id (int): 사용자 ID
            
        Returns:
            Dict[str, Any]: 사용자 게임 데이터
        """
        async with aiosqlite.connect(self.db_path) as db:
            try:
                async with db.execute(
                    f'SELECT {", ".join(self.columns)} FROM {self.table_name} WHERE user_id = ?',
                    (user_id,)
                ) as cursor:
                    row = await cursor.fetchone()
                
                assert row is None
                
                # 새 사용자 데이터 생성
                user_data = self.default_user_data.copy()
                
                placeholders = ", ".join(["?"] * len(self.columns))
                values = [
                    user_id,
                    *[user_data.get(col) for col in self.columns[1:]]
                ]
                
                await db.execute(
                    f"""
                    INSERT INTO {self.table_name} (
                        {", ".join(self.columns)}
                    ) VALUES ({placeholders})
                    """,
                    values
                )
                await db.commit()

                async with db.execute(
                    f'SELECT {", ".join(self.columns)} FROM {self.table_name} WHERE user_id = ?',
                    (user_id,)
                ) as cursor:
                    row = await cursor.fetchone()
                    if row is None:
                        raise GameError("Fail to fetch data.")
                    
                return {
                    self.columns[i]: (
                        None if row[i] == ''
                        else row[i]
                    )
                    for i in range(len(self.columns))
                }
                
            except Exception as e:
                logger.error(f"데이터 로드 실패 (user_id: {user_id}): {e}")
                raise

    async def get_user_data(self, user_id: int) -> Dict[str, Any]:
        """
        사용자의 게임 데이터를 불러옵니다.
        
        Args:
            user_id (int): 사용자 ID
            
        Returns:
            Dict[str, Any]: 사용자 게임 데이터
        """
        async with aiosqlite.connect(self.db_path) as db:
            try:
                async with db.execute(
                    f'SELECT {", ".join(self.columns)} FROM {self.table_name} WHERE user_id = ?',
                    (user_id,)
                ) as cursor:
                    row = await cursor.fetchone()
                    
                if row is None:
                    return None
                else:
                    return {
                        self.columns[i]: (
                            None if row[i] == ''
                            else row[i]
                        )
                        for i in range(len(self.columns))
                    }
                
            except Exception as e:
                logger.error(f"데이터 로드 실패 (user_id: {user_id}): {e}")
                raise

    async def update_user_data(self, user_id: int, data: Dict[str, Any]) -> bool:
        """
        사용자의 게임 데이터를 저장합니다.
        
        Args:
            user_id (int): 사용자 ID
            data (Dict[str, Any]): 저장할 게임 데이터
            
        Returns:
            bool: 저장 성공 여부
        """
        if not isinstance(data, dict):
            logger.error(f"잘못된 데이터 형식 (user_id: {user_id}): {type(data)}")
            return False
        
        try:
            update_fields = [c for c in self.columns if c in data.keys() and c != "user_id"]
            if len(update_fields) == 0:
                return False
                        
            update_expr = [f"{col} = :{col}" for col in update_fields]
            update_data = {k: v for k, v in data.items() if k in update_fields}
            update_query = f"""UPDATE user_data SET {', '.join(update_expr)} WHERE user_id = :user_id"""
            update_params = {**{col: update_data.get(col) for col in update_fields}, 'user_id': user_id}
            print(f"{update_query=}")
            print(f"{update_data=}")
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(sql=update_query, parameters=update_params)
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"데이터 저장 실패 (user_id: {user_id}): {e}")
            return False


    async def get_all_user_data(self) -> List[Dict[str, Any]]:
        """
        모든 사용자의 게임 데이터를 조회합니다.
        
        Returns:
            List[Dict[str, Any]]: 전체 사용자 게임 데이터 목록
        """
        async with aiosqlite.connect(self.db_path) as db:
            try:
                async with db.execute(
                    f'SELECT {", ".join(self.columns)} FROM {self.table_name}'
                ) as cursor:
                    rows = await cursor.fetchall()
                    
                    return [
                        {
                            self.columns[i]: (
                                None if row[i] == ''
                                else row[i]
                            )
                            for i in range(len(self.columns))
                        }
                        for row in rows
                    ]
                    
            except Exception as e:
                logger.error(f"전체 데이터 로드 실패: {e}")
                raise
