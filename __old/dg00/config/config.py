import json
from pathlib import Path


GAME_CONFIG = {
    "stages": {
        "디지타마": {
            "evolution_time": 0,
            "evolution_count": 1,
            "copy_rate": 0,
            "data_rate": 0,
            "description": "부화를 기다리는 디지타마입니다. !쓰담쓰담으로 부화시켜주세요.",
            "image_path": "assets/digitama.webp"
        },
        "쿠라몬": {
            "evolution_time": 30,
            "evolution_count": 1010101010,
            "copy_rate": 1.0,  # 1초당 2배로 복제
            "data_rate": 1,    # 1초당 1MB 흡수
            "description": "컴퓨터 네트워크상에 갑자기 출연한 정체불명의 디지몬. 네트워크에서 병원균처럼 번식해 가벼운 네트워크 장애를 일으킵니다.",
            "special_move": "글레어 아이",
            "image_path": "assets/kuramon.webp"
        },
        "츠메몬": {
            "evolution_time": 600,
            "evolution_count": 2000000000,
            "copy_rate": 1.5,  # 1초당 2.5배로 복제
            "data_rate": 10,   # 1초당 10MB 흡수
            "description": "쿠라몬이 더 진화한 유년기 디지몬. 촉수 끝이 갈고리발톱처럼 돼서 더 포악해졌습니다.",
            "special_move": "네일 스크래치",
            "image_path": "assets/tsumemon.webp"
        },
        "케라몬": {
            "evolution_time": 6060,
            "evolution_count": 4000000000,
            "copy_rate": 2.0,  # 1초당 3배로 복제
            "data_rate": 100,  # 1초당 100MB 흡수
            "description": "츠메몬이 진화한 성장기 디지몬. 매우 활기찬 성격으로 파괴 행위는 놀이의 일환이라고 생각합니다.",
            "special_move": "찰싹 때리기",
            "image_path": "assets/kuramon.webp"
        },
        "크리사리몬": {
            "evolution_time": 121000,
            "evolution_count": 8000000000,
            "copy_rate": 2.5,  # 1초당 3.5배로 복제
            "data_rate": 1000, # 1초당 1GB 흡수
            "description": "번데기의 모습을 한 성숙기 디지몬. 이동은 전혀 할 수 없지만 단단한 외피로 보호됩니다.",
            "special_move": "데이터 파괴",
            "image_path": "assets/chrysalimon.webp"
        },
        "인펠몬": {
            "evolution_time": 266400,
            "evolution_count": 16000000000,
            "copy_rate": 3.0,  # 1초당 4배로 복제
            "data_rate": 10000, # 1초당 10GB 흡수
            "description": "손발이 긴 거미의 모습을 한 완전체 디지몬. 강력한 보안과 상관없이 모든 네트워크에 침입할 수 있습니다.",
            "special_move": "네트워크수류탄",
            "image_path": "assets/infermon.webp"
        },
        "디아블로몬": {
            "evolution_time": 600,
            "evolution_count": 0,
            "copy_rate": 0,
            "data_rate": 0,
            "description": "최종 진화 형태. 전지전능한 존재가 되어 핵 미사일 발사 시스템을 해킹했습니다!",
            "special_move": "캐논발사",
            "image_path": "assets/diablomon.webp"
        }
    },
    "battle_chances": {
        "쿠라몬": 1.0,    # 튜토리얼이므로 100% 승리
        "츠메몬": 0.8,    # 80% 승률
        "케라몬": 0.6,    # 60% 승률
        "크리사리몬": 0.5, # 50% 승률
        "인펠몬": 0.4,    # 40% 승률
        "디아블로몬": 0.0  # 전투 없음
    },
    "battle_settings": {
        "battle_chance": 0.1,      # 10% 확률로 전투 발생
        "win_bonus": 1.2,          # 승리시 20% 보너스
        "lose_penalty": 0.8,       # 패배시 20% 감소
        "cheer_bonus": 1.2         # 응원시 승률 20% 증가
    },
    "events": {
        "news": [
            {
                "data_threshold": 1024,  # 1GB
                "message": "전세계 곳곳에서 네트워크 장애 발생! 원인은 알 수 없는 바이러스?"
            },
            {
                "data_threshold": 102400,  # 100GB
                "message": "군사 시설의 네트워크가 뚫렸다! 정체불명의 디지털 생명체 발견!"
            },
            {
                "data_threshold": 1048576,  # 1TB
                "message": "전세계 핵미사일 발사 시스템 해킹 위험! 디아블로몬의 존재 확인!"
            }
        ],
        "random_messages": {
            "쿠라몬": [
                "데이터 맛있어요~",
                "더 많이 복제되고 싶어!"
            ],
            "츠메몬": [
                "네트워크가 약해빠졌네?",
                "더 강한 시스템을 찾아보자!"
            ],
            "케라몬": [
                "파괴는 정말 재미있어!",
                "이 정도 보안은 찰싹이야!"
            ],
            "크리사리몬": [
                "더 강한 힘을 원해...",
                "아무도 날 막을 수 없어"
            ],
            "인펠몬": [
                "이제 곧 최종 진화야!",
                "인류의 모든 데이터를 흡수하겠어!"
            ],
            "디아블로몬": [
                "나는 신이다!",
                "이제 세상은 끝이야!"
            ]
        }
    },
    "evolution_quiz": {
        "쿠라몬": {
            "question": "처음으로 등장한 컴퓨터 바이러스의 이름은?",
            "answer": "크리퍼",
            "hint": "1971년에 만들어진 이 바이러스는 'Creeper'라는 메시지를 출력했습니다."
        },
        "츠메몬": {
            "question": "최초의 웜 바이러스의 이름은?",
            "answer": "모리스 웜",
            "hint": "1988년 로버트 모리스가 만든 이 악성코드는 인터넷 역사상 최초의 웜입니다."
        },
        "케라몬": {
            "question": "램섬웨어의 대표적인 공격 방식은?",
            "answer": "암호화",
            "hint": "피해자의 파일을 이것을 통해 접근할 수 없게 만듭니다."
        },
        "크리사리몬": {
            "question": "DDoS 공격의 풀네임은?",
            "answer": "분산 서비스 거부 공격",
            "hint": "여러 곳에서 동시에 서버를 공격하는 방식입니다."
        },
        "인펠몬": {
            "question": "악성코드를 탐지하는 방법 중 시그니처 기반이 아닌 것은?",
            "answer": "행위기반",
            "hint": "프로그램의 패턴이 아닌 동작을 분석하는 방식입니다."
        }
    }
}

# 스테이지 순서를 리스트로 관리 (진화 순서 체크용)
EVOLUTION_ORDER = [
    "디지타마",
    "쿠라몬",
    "츠메몬",
    "케라몬",
    "크리사리몬", 
    "인펠몬",
    "디아블로몬"
]

# 편의 함수들
def get_next_stage(current_stage: str) -> str:
    """현재 스테이지의 다음 진화 단계를 반환"""
    if current_stage == "디아블로몬":
        return None
    current_index = EVOLUTION_ORDER.index(current_stage)
    return EVOLUTION_ORDER[current_index + 1]

def get_stage_config(stage: str) -> dict:
    """특정 스테이지의 설정을 반환"""
    return GAME_CONFIG["stages"][stage]

def get_battle_chance(stage: str) -> float:
    """특정 스테이지의 기본 전투 승률을 반환"""
    return GAME_CONFIG["battle_chances"].get(stage, 0.0)

def get_random_message(stage: str) -> str:
    """특정 스테이지의 랜덤 대사 중 하나를 반환"""
    import random
    messages = GAME_CONFIG["events"]["random_messages"].get(stage, [])
    return random.choice(messages) if messages else None

def get_evolution_quiz(stage: str) -> dict:
    """특정 스테이지의 진화 퀴즈를 반환"""
    return GAME_CONFIG["evolution_quiz"].get(stage)



class ConfigLoader:
    @staticmethod
    def load_token() -> str:
        """Discord 봇 토큰을 로드합니다."""
        try:
            with open(f"{str(Path.home())}/.discord/token.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'discord_token' not in data:
                    raise KeyError("token.json 파일에 'discord_token' 키가 없습니다.")
                return data['discord_token']
        except FileNotFoundError:
            raise FileNotFoundError(
                "token.json 파일을 찾을 수 없습니다.\n"
                "config/token.json 파일을 다음과 같이 생성해주세요:\n"
                '{\n    "discord_token": "YOUR_BOT_TOKEN"\n}'
            )
        except json.JSONDecodeError:
            raise ValueError("token.json 파일의 JSON 형식이 올바르지 않습니다.")

    @staticmethod
    def get_config() -> dict:
        """게임 설정을 반환합니다."""
        return GAME_CONFIG

    @staticmethod
    def get_stage_config(stage: str) -> dict:
        """특정 스테이지의 설정을 반환합니다."""
        return GAME_CONFIG['stages'].get(stage)

    @staticmethod
    def get_battle_settings() -> dict:
        """전투 관련 설정을 반환합니다."""
        return GAME_CONFIG['battle_settings']

    @staticmethod
    def get_events_config() -> dict:
        """이벤트 관련 설정을 반환합니다."""
        return GAME_CONFIG['events']
