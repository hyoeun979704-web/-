#!/usr/bin/env bash
# 라이브 채팅 리플레이 + 회차 메타데이터 수집
#
#   bash fetch_chat.sh @CHANNEL      out/   [회차수]   # 채널 최근 N회차 일괄
#   bash fetch_chat.sh VIDEO_URL     out/              # 회차 하나
#
# 산출: out/<videoId>.live_chat.json  +  out/views.json
set -euo pipefail

TARGET="${1:?채널 핸들(@name) 또는 영상 URL을 넘길 것}"
OUT="${2:-chats}"
LIMIT="${3:-8}"

command -v yt-dlp >/dev/null || {
  echo "yt-dlp 가 필요합니다:  pipx install yt-dlp   (또는 pip install -U yt-dlp)" >&2
  exit 1
}
command -v jq >/dev/null || { echo "jq 가 필요합니다" >&2; exit 1; }

mkdir -p "$OUT"

if [[ "$TARGET" == @* ]]; then
  echo "· 회차 목록 수집: $TARGET (최근 ${LIMIT}개)"
  yt-dlp --flat-playlist -J "https://www.youtube.com/${TARGET}/streams" \
    | jq --argjson n "$LIMIT" '[.entries[:$n][] | {id, title, views: .view_count, date: .upload_date, duration_min: ((.duration // 0) / 60 | floor)}]' \
    > "$OUT/_list.json"
  IDS=$(jq -r '.[].id' "$OUT/_list.json")
else
  yt-dlp -J "$TARGET" \
    | jq '[{id, title, views: .view_count, date: .upload_date, duration_min: ((.duration // 0) / 60 | floor)}]' \
    > "$OUT/_list.json"
  IDS=$(jq -r '.[].id' "$OUT/_list.json")
fi

# videoId 를 키로 하는 views.json 생성 (analyze_chat.py 입력)
jq 'map({(.id): {views, title, date, duration_min, kind: ""}}) | add' "$OUT/_list.json" > "$OUT/views.json"
MISSING=$(jq '[.[] | select(.views == null or .views == 0)] | length' "$OUT/views.json")
if [[ "$MISSING" -gt 0 ]]; then
  echo "  ! 조회수가 비어 있는 회차 ${MISSING}건 — 전환 지표가 계산되지 않는다." >&2
  echo "    --flat-playlist 가 조회수를 안 줄 때가 있다. 해당 회차는 yt-dlp -J 로 개별 보완할 것." >&2
fi
echo "· views.json 생성 — 회차 성격(kind: 고가/저가 등)은 직접 채워 넣을 것"

for id in $IDS; do
  if [[ -f "$OUT/$id.live_chat.json" ]]; then
    echo "· $id 이미 있음, 건너뜀"
    continue
  fi
  echo "· $id 채팅 리플레이 수집"
  yt-dlp --skip-download --write-subs --sub-langs live_chat \
         -o "$OUT/%(id)s.%(ext)s" "https://www.youtube.com/watch?v=$id" \
    || echo "  ! $id 채팅 리플레이 없음 (라이브가 아니거나 만료)" >&2
done

echo
echo "다음 단계:"
echo "  1) $OUT/views.json 의 kind 필드를 회차별로 채운다 (고가/저가 등)"
echo "  2) python3 analyze_chat.py $OUT/*.live_chat.json --views $OUT/views.json -o runs.json"
