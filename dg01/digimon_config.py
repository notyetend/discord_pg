import pandas as pd

STAGES = {  # stage_idx: stage_name
    0: "디지타마",
    1: "쿠라몬",
    2: "츠메몬",
    3: "케라몬",
    4: "크리사리몬",
    5: "인펠몬",
    6: "디아블로몬"
}

STAGE_CONFIG = [
    {
        "stage_idx": 0,
        "evolution_time": 30,  # 예상 진화 시간(초)
        "evolution_count": 100,  # MB
        "copy_rate": 3,  # MB, 초당 증식
        "description": "부화를 기다리는 디지타마입니다. !쓰담쓰담으로 부화시켜주세요.",
        "image_path": "assets/digitama.webp",
        "battle_chance": 1,
        "random_messages": [],
        "evolution_quiz": [],
    },
    {
        "stage_idx": 1,
        "evolution_time": 7 * 60 + 30,
        "evolution_count": 10_000,
        "copy_rate": 22,
        "description": "컴퓨터 네트워크상에 갑자기 출연한 정체불명의 디지몬. 네트워크에서 병원균처럼 번식해 가벼운 네트워크 장애를 일으킵니다.",
        "special_move": "글레어 아이",
        "image_path": "assets/kuramon.webp",
        "battle_chance": 1.0,  # 튜토리얼이므로 100% 승리
        "random_messages": [
            "데이터 맛있어요~",
            "더 많이 복제되고 싶어!"
        ],
        "evolution_quiz": [
            {
                "question": "처음으로 등장한 컴퓨터 바이러스의 이름은?",
                "answer": "크리퍼",
                "hint": "1971년에 만들어진 이 바이러스는 'Creeper'라는 메시지를 출력했습니다."
            },
        ],
    },
    {
        "stage_idx": 2,
        "evolution_time": 60 * 60,
        "evolution_count": 1_000_000,  # 1TB
        "copy_rate": 278,
        "description": "쿠라몬이 더 진화한 유년기 디지몬. 촉수 끝이 갈고리발톱처럼 돼서 더 포악해졌습니다.",
        "special_move": "네일 스크래치",
        "image_path": "assets/tsumemon.webp",
        "battle_chance": 0.8,  # 80% 승률
        "random_messages": [
            "네트워크가 약해빠졌네?",
            "더 강한 시스템을 찾아보자!"
        ],
        "evolution_quiz": [
            {
                "question": "최초의 웜 바이러스의 이름은?",
                "answer": "모리스 웜",
                "hint": "1988년 로버트 모리스가 만든 이 악성코드는 인터넷 역사상 최초의 웜입니다."
            },
        ],
    },
    {
        "stage_idx": 3,
        "evolution_time": 12 * 60 * 60,
        "evolution_count": 1_000_000_000,  # 1PB
        "copy_rate": 23_148,
        "description": "츠메몬이 진화한 성장기 디지몬. 매우 활기찬 성격으로 파괴 행위는 놀이의 일환이라고 생각합니다.",
        "special_move": "찰싹 때리기",
        "image_path": "assets/kuramon.webp",
        "battle_chance": 0.6,  # 60% 승률
        "random_messages": [
            "파괴는 정말 재미있어!",
            "이 정도 보안은 찰싹이야!"
        ],
        "evolution_quiz": [
            {
                "question": "램섬웨어의 대표적인 공격 방식은?",
                "answer": "암호화",
                "hint": "피해자의 파일을 이것을 통해 접근할 수 없게 만듭니다."
            },
        ],
    },
    {
        "stage_idx": 4,
        "evolution_time": 24 * 60 * 60,
        "evolution_count": 1_000_000_000_000,  # 1EB
        "copy_rate": 11_574_074,  # 1초당 3.5배로 복제
        "description": "번데기의 모습을 한 성숙기 디지몬. 이동은 전혀 할 수 없지만 단단한 외피로 보호됩니다.",
        "special_move": "데이터 파괴",
        "image_path": "assets/chrysalimon.webp",
        "battle_chance": 0.5,  # 50% 승률
        "random_messages": [
            "더 강한 힘을 원해...",
            "아무도 날 막을 수 없어"
        ],
        "evolution_quiz": [
            {
                "question": "DDoS 공격의 풀네임은?",
                "answer": "분산 서비스 거부 공격",
                "hint": "여러 곳에서 동시에 서버를 공격하는 방식입니다."
            },
        ],
    },
    {
        "stage_idx": 5,
        "evolution_time": 48 * 60 * 60,
        "evolution_count": 1_000_000_000_000_000,  # 1ZB
        "copy_rate": 578_703_703,
        "description": "손발이 긴 거미의 모습을 한 완전체 디지몬. 강력한 보안과 상관없이 모든 네트워크에 침입할 수 있습니다.",
        "special_move": "네트워크수류탄",
        "image_path": "assets/infermon.webp",
        "battle_chance": 0.4,  # 40% 승률
        "random_messages": [
            "이제 곧 최종 진화야!",
            "인류의 모든 데이터를 흡수하겠어!"
        ],
        "evolution_quiz": [
            {
                "question": "악성코드를 탐지하는 방법 중 시그니처 기반이 아닌 것은?",
                "answer": "행위기반",
                "hint": "프로그램의 패턴이 아닌 동작을 분석하는 방식입니다."
            },
        ],
    },
    {
        "stage_idx": 6,
        "evolution_time": 600,
        "evolution_count": 0,
        "copy_rate": 0,
        "description": "최종 진화 형태. 전지전능한 존재가 되어 핵 미사일 발사 시스템을 해킹했습니다!",
        "special_move": "캐논발사",
        "image_path": "assets/diablomon.webp",
        "battle_chance": 0.0,  # 전투 없음
        "random_messages": [
            "나는 신이다!",
            "이제 세상은 끝이야!"
        ],
        "evolution_quiz": [
        ],
    }
]


BATTLE_CONFIG = {
    "battle_chance": 0.1,      # 10% 확률로 전투 발생
    "win_bonus": 1.2,          # 승리시 20% 보너스
    "lose_penalty": 0.8,       # 패배시 20% 감소
    "cheer_bonus": 1.2         # 응원시 승률 20% 증가
}

EVENT_NEWS_CONFIG = [
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
]

DFP_STAGE_CONFIG = pd.DataFrame(STAGE_CONFIG)
EVOLUTION_ORDER = [value for _, value in sorted(STAGES.items())]

def get_next_stage_idx(current_stage_idx):
    """현재 stage의 다음 stage_idx를 반환"""
    sorted_stages = sorted(STAGES.keys())
    current_index = sorted_stages.index(current_stage_idx)
    if current_index < len(sorted_stages) - 1:
        return sorted_stages[current_index + 1]
    return None

def get_stage_config(stage_idx: int) -> dict:
    """특정 스테이지의 설정을 반환"""
    dfp_stage_config = DFP_STAGE_CONFIG.query(f"stage_idx == {stage_idx}")
    assert dfp_stage_config.shape[0] == 1
    return dfp_stage_config.to_dict(orient="records")[0]

def get_battle_chance(stage_idx: int) -> float:
    """특정 스테이지의 기본 전투 승률을 반환"""
    return get_stage_config(stage_idx)["battle_chance"]

def get_random_message(stage_idx: int) -> str:
    """특정 스테이지의 랜덤 대사 중 하나를 반환"""
    import random
    messages = get_stage_config(stage_idx)["random_messages"]
    return random.choice(messages) if messages else None

def get_evolution_quiz(stage_idx: int) -> dict:
    """특정 스테이지의 진화 퀴즈를 반환"""
    return get_stage_config(stage_idx)["evolution_quiz"]