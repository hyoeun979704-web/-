#!/usr/bin/env python3
"""라이브 채팅 리플레이 → 회차 지표.

입력: yt-dlp가 뽑은 `*.live_chat.json` (JSON Lines). 회차당 한 개.
출력: 회차별 지표 JSON + 사람이 읽는 요약.

  python3 analyze_chat.py chats/*.live_chat.json --views views.json -o runs.json

views.json 은 {"<videoId>": {"views": 86400, "title": "...", "kind": "저가"}} 형태.
조회수는 채팅에 없으므로 반드시 따로 넣는다 (yt-dlp -J 또는 수기).

지표 정의는 references/02-metrics.md 와 1:1로 대응한다.
"""
import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict

BUCKET_MIN = 10          # 집계 버킷 크기(분)
DEAD_THRESHOLD = 10      # 이 인원 이하인 버킷 = 죽은 구간
OPENING_MIN = 20         # 오프닝 집중도 측정 구간(분)

# 방송사 봇이 자동 송출하는 주문완료 로그. 채널마다 문구가 다르므로 조정 가능.
ORDER_RE = re.compile(r"주문\s*완료")
# 마스킹된 구매자명 — "정*정님 주문완료!" 형태에서 이름을 집는다.
BUYER_RE = re.compile(r"([^\s,]{1,20}?)\s*님?\s*주문\s*완료")
# 상품 식별자 — 봇 메시지 안의 상품코드/상품명. 채널 포맷에 맞게 조정.
ITEM_RE = re.compile(r"\[([^\]]{1,40})\]")
# 구매의사 발화. 벤치마크 채널에도 "똑같은 정규식"을 적용해야 비교가 성립한다.
INTENT_RE = re.compile(r"주문|구매|결제|주세요|장바구니|살게요|살래요|담았")
# 피플라이브 선착순 주문 트리거
JEOYO_RE = re.compile(r"^\s*저요\s*$")


def load_lines(path):
    """yt-dlp live_chat.json 은 JSON Lines. 통짜 JSON 배열로 오는 경우도 받아준다."""
    with open(path, encoding="utf-8") as f:
        head = f.read(1)
        f.seek(0)
        if head == "[":
            yield from json.load(f)
            return
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def walk_actions(obj):
    """replayChatItemAction 안에 묻힌 채팅 렌더러를 시각(ms)과 함께 꺼낸다."""
    for act in obj.get("replayChatItemAction", {}).get("actions", []):
        item = act.get("addChatItemAction", {}).get("item", {})
        r = item.get("liveChatTextMessageRenderer")
        if r:
            offset = obj.get("videoOffsetTimeMsec")
            if offset is None:
                offset = act.get("videoOffsetTimeMsec", 0)
            yield int(offset), r


def runs_text(message):
    """message.runs 를 평문으로 합친다. 이모지는 :shortcut: 으로."""
    out = []
    for run in message.get("runs", []):
        if "text" in run:
            out.append(run["text"])
        elif "emoji" in run:
            e = run["emoji"]
            out.append(e.get("shortcuts", [""])[0] or "")
    return "".join(out)


def author_flags(r):
    """진행자(채널 소유자)·모더레이터 여부."""
    owner = mod = False
    for badge in r.get("authorBadges", []):
        icon = (badge.get("liveChatAuthorBadgeRenderer", {})
                     .get("icon", {}).get("iconType", ""))
        if icon == "OWNER":
            owner = True
        elif icon == "MODERATOR":
            mod = True
    return owner, mod


def analyze(path, meta):
    vid = meta.get("id") or os.path.basename(path).split(".")[0]
    chats = 0
    speakers = set()
    seller_chats = 0
    intent_chats = 0
    jeoyo = 0
    orders = 0
    buyers = set()
    items = Counter()
    bucket_msgs = Counter()
    bucket_people = defaultdict(set)
    bucket_orders = Counter()
    last_ms = 0

    for obj in load_lines(path):
        for offset_ms, r in walk_actions(obj):
            text = runs_text(r.get("message", {}))
            if not text:
                continue
            name = r.get("authorName", {}).get("simpleText", "")
            owner, mod = author_flags(r)
            b = offset_ms // 60000 // BUCKET_MIN
            last_ms = max(last_ms, offset_ms)

            if ORDER_RE.search(text):
                # 봇 주문 로그 — 채팅 지표에서는 제외하고 주문 지표로만 센다.
                orders += 1
                bucket_orders[b] += 1
                mb = BUYER_RE.search(text)
                if mb:
                    buyers.add(mb.group(1))
                mi = ITEM_RE.search(text)
                if mi:
                    items[mi.group(1)] += 1
                continue

            chats += 1
            speakers.add(name)
            bucket_msgs[b] += 1
            bucket_people[b].add(name)
            if owner or mod:
                seller_chats += 1
            if INTENT_RE.search(text):
                intent_chats += 1
            if JEOYO_RE.match(text):
                jeoyo += 1

    duration_min = meta.get("duration_min") or (last_ms / 60000 if last_ms else 0)
    n_buckets = max(int(duration_min // BUCKET_MIN) or 1, len(bucket_msgs))
    dead = sum(1 for b in range(n_buckets) if len(bucket_people.get(b, ())) <= DEAD_THRESHOLD)
    open_buckets = max(OPENING_MIN // BUCKET_MIN, 1)
    open_msgs = sum(bucket_msgs.get(b, 0) for b in range(open_buckets))

    views = meta.get("views")
    top3 = sum(c for _, c in items.most_common(3))

    def per1k(n):
        return round(n / views * 1000, 2) if views else None

    return {
        "id": vid,
        "title": meta.get("title", ""),
        "kind": meta.get("kind", ""),
        "views": views,
        "duration_min": round(duration_min, 1),
        "chats": chats,
        "participants": len(speakers),
        "orders": orders,
        "buyers": len(buyers),
        # --- 핵심 비교 지표 ---
        "buyers_per_1k": per1k(len(buyers)),
        "conv_pct": round(len(buyers) / views * 100, 4) if views else None,
        "orders_per_buyer": round(orders / len(buyers), 2) if buyers else None,
        "orders_per_min": round(orders / duration_min, 2) if duration_min else None,
        "participants_pct": round(len(speakers) / views * 100, 3) if views else None,
        "intent_per_1k": per1k(intent_chats),
        "intent_rate_pct": round(intent_chats / chats * 100, 1) if chats else None,
        "seller_rate_pct": round(seller_chats / chats * 100, 1) if chats else None,
        "seller_chats": seller_chats,
        "first20_share_pct": round(open_msgs / chats * 100, 1) if chats else None,
        "dead_ratio_pct": round(dead / n_buckets * 100, 1) if n_buckets else None,
        "jeoyo": jeoyo,
        "items_seen": len(items),
        "top3_share_pct": round(top3 / orders * 100, 1) if orders else None,
        # --- 차트용 원자료 ---
        "buckets": {
            "size_min": BUCKET_MIN,
            "chats": [bucket_msgs.get(b, 0) for b in range(n_buckets)],
            "people": [len(bucket_people.get(b, ())) for b in range(n_buckets)],
            "orders": [bucket_orders.get(b, 0) for b in range(n_buckets)],
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--views", help="videoId → {views,title,kind,duration_min} JSON")
    ap.add_argument("-o", "--out", default="runs.json")
    a = ap.parse_args()

    meta_all = {}
    if a.views:
        with open(a.views, encoding="utf-8") as f:
            meta_all = json.load(f)

    runs = []
    for path in a.files:
        vid = os.path.basename(path).split(".")[0]
        meta = dict(meta_all.get(vid, {}))
        meta.setdefault("id", vid)
        if not meta.get("views"):
            print(f"  ! {vid}: 조회수 없음 — 전환 지표는 건너뜀", file=sys.stderr)
        runs.append(analyze(path, meta))

    runs.sort(key=lambda r: (r["buyers_per_1k"] is None, -(r["buyers_per_1k"] or 0)))
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(runs, f, ensure_ascii=False, indent=2)

    hdr = f"{'회차':<14}{'조회수':>9}{'구매자':>7}{'/1천뷰':>8}{'첫20분':>8}{'죽은구간':>9}{'구매의사/1천':>13}"
    print(hdr)
    print("-" * len(hdr))
    for r in runs:
        print(f"{r['id']:<14}{(r['views'] or 0):>9,}{r['buyers']:>7}"
              f"{(r['buyers_per_1k'] or 0):>8.2f}{(r['first20_share_pct'] or 0):>7.1f}%"
              f"{(r['dead_ratio_pct'] or 0):>8.1f}%{(r['intent_per_1k'] or 0):>13.2f}")
    print(f"\n→ {a.out}")


if __name__ == "__main__":
    main()
