# Discord Digimon Game Bot

디스코드에서 즐기는 디지몬 육성 게임 봇입니다. 디지몬을 키우고, 전투하고, 진화시키는 과정을 통해 최종 진화 단계까지 성장시켜보세요!

## 개발 정보

- **개발**: dwk
- **기획**: hwione
  - [기획 문서](https://hwione.notion.site/13a6e66a4a48806e8c8ad3e40f45725e)
  - [게임 데이터 시트](https://docs.google.com/spreadsheets/d/1_VOmKB_iGmPYKOpLzysrZx9FBeSAoTLifbn8PS793rU/edit?gid=0#gid=0)

## 주요 기능

- 🥚 디지몬 부화 및 육성
- 📈 자동 성장 시스템
- ⚔️ 전투 시스템
- 🎯 진화 퀴즈
- 📊 실시간 대시보드
- 🎮 다양한 게임 커맨드

## 설치 방법

1. 저장소 클론
```bash
git clone https://github.com/notyetend/discord_pg.git
cd discord_pg/dg01
```

2. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

3. Discord 봇 토큰 설정
- `~/.discord/token.json` 파일을 생성하고 아래 형식으로 토큰을 입력합니다:
```json
{
    "discord_token": "your_bot_token_here"
}
```

4. 게임 설정 파일 업데이트
```bash
python main.py --update_config
```

## 사용 방법

### 기본 명령어

- `!쓰담쓰담` - 게임 시작
- `!현황` - 현재 디지몬 상태 확인
- `!대시보드` - 실시간 대시보드 표시
- `!치료` - 중단된 복제 재개
- `!응원` - 디지몬 응원하기
- `!방생` - 게임 종료

### 대시보드 기능

대시보드를 통해 다음 정보를 실시간으로 확인할 수 있습니다:
- 현재 스테이지와 진화 진행도
- 개체 수와 데이터량
- 전투 기록
- 시스템 상태
- 활성화된 효과

## 프로젝트 구조

```
dg01/
├── __init__.py
├── data_manager.py     # 데이터 관리
├── digimon_battle.py   # 전투 시스템
├── digimon_config.py   # 게임 설정
├── digimon_data.py     # 데이터 구조
├── digimon_logic.py    # 게임 로직
├── digimon_quiz.py     # 퀴즈 시스템
├── event_bus.py        # 이벤트 처리
├── game_events.py      # 게임 이벤트
├── game_manager.py     # 게임 관리
├── game_session.py     # 세션 관리
├── main.py            # 메인 실행 파일
└── utils.py           # 유틸리티 함수
```

## 문서 및 리소스

- [게임 기획 문서](https://hwione.notion.site/13a6e66a4a48806e8c8ad3e40f45725e)
- [게임 데이터 시트](https://docs.google.com/spreadsheets/d/1_VOmKB_iGmPYKOpLzysrZx9FBeSAoTLifbn8PS793rU/edit?gid=0#gid=0)

## 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 라이선스

This project is licensed under the MIT License - see the LICENSE file for details.

## 문의사항

GitHub Issues를 통해 버그를 제보하거나 새로운 기능을 제안하실 수 있습니다.