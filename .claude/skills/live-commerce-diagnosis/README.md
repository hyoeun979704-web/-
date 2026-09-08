# live-commerce-diagnosis · 사용법

라방 채널의 "조회수는 나오는데 안 팔린다"를 공개 데이터로 진단해 제안서급 리포트
아티팩트를 만드는 스킬. 옐로우베리 46회차 분석에서 실제로 쓴 플로우를 그대로 뽑았다.

## 설치

`.claude/skills/live-commerce-diagnosis/` 에 있으면 이 저장소에서 자동으로 잡힌다.
다른 프로젝트에서도 쓰려면 개인 스킬 폴더로 복사한다.

```bash
cp -r .claude/skills/live-commerce-diagnosis ~/.claude/skills/
```

## 부르는 법

그냥 자연어로 말하면 된다. 스킬 이름을 몰라도 트리거된다.

```
옐로우베리 채널 라방 분석해줘
@marketunni 진단해서 제안서 만들어줘
이 채널 조회수는 높은데 매출이 안 나온대. 원인 찾아줘
경쟁 라방 채널들이랑 비교해줘
```

명시적으로 부르려면:

```
/live-commerce-diagnosis 옐로우베리
```

## 처음 시작할 때 줄 것

이 세 개만 있으면 시작된다. 나머지는 진행하며 정한다.

| 항목 | 예시 | 없으면 |
|---|---|---|
| 채널 URL | `youtube.com/@Yellowberry77` | 진행 불가 |
| 셀러가 실제로 한 질문 | "동접 대비 매출이 안 나와요" | 일반 진단으로 진행 |
| 분석 기간 | 최근 8개월 / 40회차 | 기본값(최근 8개월) 적용 |

**시작 전 30초 확인:** 회차 하나를 열어 채팅 리플레이에 `○○님 주문완료!` 봇 메시지가
찍히는지 본다.
- **있으면** → 실구매자·전환율까지 계산되는 풀 진단
- **없으면** → 구매의사 발화(대리 지표)까지만. 리포트 강도가 한 단계 내려간다

## 도구 직접 쓰기

에이전트 없이 손으로 돌릴 수도 있다.

```bash
cd .claude/skills/live-commerce-diagnosis

# 1) 채널 최근 8회차 채팅 리플레이 + 메타데이터
bash scripts/fetch_chat.sh @Yellowberry77 chats/ 8

# 2) chats/views.json 의 kind 필드를 회차별로 채운다 (고가/저가 등)

# 3) 회차별 지표 계산
python3 scripts/analyze_chat.py chats/*.live_chat.json --views chats/views.json -o runs.json

# 4) 채점 — measures.json 은 references/04-scorecard.md 참조
python3 scripts/scorecard.py measures.json
```

`yt-dlp` 가 필요하다: `pipx install yt-dlp`

### 회귀 검증

배점 로직을 손댔으면 반드시 돌린다. 원 사례 실측치로 **18/100** 이 나와야 정상이다.

```bash
python3 scripts/scorecard.py --example
```

## 산출물

- **아티팩트 1장** — 12장 구조 리포트. 이게 납품물이다
- `runs.json` — 회차별 전 지표. 재분석·다음 회차 비교용
- 채점 결과와 처방 우선순위

## 다른 카테고리에 쓰려면

여성의류 라방 기준으로 임계값이 잡혀 있다. 식품·리빙 등으로 옮길 때 손볼 곳:

| 위치 | 무엇을 |
|---|---|
| `scripts/analyze_chat.py` 상단 정규식 | 주문봇 메시지 포맷이 채널마다 다르다 |
| `scripts/scorecard.py` 의 `score()` | C1 충동가격대 구간(현재 2~5만원) |
| `references/03-benchmark.md` | 벤치마크 선정 조건(카테고리·체급) |

**임계값을 바꿨으면 리포트 방법론 장에 그 사실을 적는다.** 자체 기준을 업계 절대
기준인 척하는 순간 셀러가 한 번만 검증해도 신뢰를 잃는다.

## 파일 구성

```
SKILL.md                       진행 순서와 규칙 (에이전트 진입점)
README.md                      이 문서
references/01-collect.md       채팅 리플레이·카탈로그·퍼널 동선 수집
references/02-metrics.md       지표 18종 정의와 교차 검증
references/03-benchmark.md     벤치마크 채널 선정과 등급
references/04-scorecard.md     12항목 100점 채점 기준
references/05-report.md        12장 리포트 구조와 집필 규칙
scripts/fetch_chat.sh          yt-dlp 수집 래퍼
scripts/analyze_chat.py        채팅 → 회차 지표
scripts/scorecard.py           측정치 → 점수·우선순위
assets/report-skeleton.html    리포트 HTML 뼈대 (디자인 시스템 + 차트 헬퍼)
```
