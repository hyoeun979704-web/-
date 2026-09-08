#!/usr/bin/env python3
"""runs.json → measures.json — 2단계와 4단계를 잇는다.

채팅에서 자동으로 뽑히는 값은 계산해 채우고, 사람이 직접 확인해야 하는 값
(홉 수·게스트 결제·가격대·사이즈·VOD 롱테일)은 null 로 남긴다. null 이 남아
있으면 scorecard.py 가 무엇을 어디서 확인해야 하는지 알려주고 멈춘다.

  python3 make_measures.py runs.json -o measures.json
"""
import argparse
import json
import math
import sys

# 사람이 직접 확인해야 하는 값 — 채팅에 없다. 1단계 퍼널 동선·카탈로그에서 온다.
MANUAL = {
    "inapp_checkout":       '방송 화면 안에서 결제가 끝나는가 — "full" / "partial" / "none"',
    "hops":                 "결제까지 화면이 바뀌는 횟수 (정수). 직접 주문 직전까지 가보고 센다",
    "guest_checkout":       '회원가입 없이 결제되는가 — "guest" / "social_1tap" / "signup_required" / "app_required"',
    "impulse_price_share":  "카탈로그에서 2~5만원대 상품 비중 (%)",
    "size_coverage":        '사이즈 커버리지 — "broad" / "two" / "one_plus" / "single"',
    "vod_longtail":         '지난 회차 상품이 언제까지 남는가 — "all" / "30d" / "recent_few" / "live_only"',
}


def _ranks(xs):
    """동점은 평균 순위로 — 동점을 무시하면 상관계수가 왜곡된다."""
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    rk = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2 + 1
        for k in range(i, j + 1):
            rk[order[k]] = avg
        i = j + 1
    return rk


def spearman(a, b):
    ra, rb = _ranks(a), _ranks(b)
    n = len(a)
    if n < 3:
        return None
    ma, mb = sum(ra) / n, sum(rb) / n
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    da = math.sqrt(sum((x - ma) ** 2 for x in ra))
    db = math.sqrt(sum((y - mb) ** 2 for y in rb))
    return round(num / (da * db), 3) if da and db else None


def seller_cohorts(runs):
    """진행자 응대량의 '지금'과 '가장 좋았던 때'를 가른다 (D1 입력).

    회차 날짜(date, YYYYMMDD)가 있어야 한다. 없으면 None 을 돌려 수동 입력으로 넘긴다.
    """
    dated = [r for r in runs if r.get("date") and r.get("seller_chats") is not None]
    if len(dated) < 4:
        return None, None
    dated.sort(key=lambda r: r["date"])
    n_recent = max(len(dated) // 4, 2)          # 최근 4분의 1을 '지금'으로
    recent, older = dated[-n_recent:], dated[:-n_recent]
    if not older:
        return None, None
    now = sum(r["seller_chats"] for r in recent) / len(recent)
    # 과거를 같은 크기 창으로 훑어 최고 코호트를 찾는다
    peak = max(
        sum(r["seller_chats"] for r in older[i:i + n_recent]) / len(older[i:i + n_recent])
        for i in range(0, max(len(older) - n_recent + 1, 1))
    )
    return round(now, 1), round(peak, 1)


def build(runs):
    scored = [r for r in runs if r.get("views") and r.get("buyers") is not None]
    if not scored:
        sys.exit("! runs.json 에 조회수·구매자가 있는 회차가 없다. views.json 을 먼저 채울 것.")

    views = sum(r["views"] for r in scored)
    buyers = sum(r["buyers"] for r in scored)
    # 참여자는 회차 간 중복 제거가 불가능하다. 합/합은 조회수 가중 평균 밀도이며,
    # 유니크 인원이 아니다 — A3 는 밀도 지표이므로 이게 맞다.
    participants = sum(r["participants"] for r in scored)

    per1k = [r["buyers"] / r["views"] * 1000 for r in scored]
    rho = spearman([r["views"] for r in scored], per1k)

    def mean(key):
        vals = [r[key] for r in scored if r.get(key) is not None]
        return round(sum(vals) / len(vals), 1) if vals else None

    now, peak = seller_cohorts(runs)

    m = {
        "_source": f"runs.json · 회차 {len(scored)}건",
        "views": views,
        "buyers": buyers,
        "participants": participants,
        "view_buy_rho": rho,
        "dead_ratio": mean("dead_ratio_pct"),
        "top3_share": mean("top3_share_pct"),
        "seller_chat_now": now,
        "seller_chat_peak": peak,
    }
    for k in MANUAL:
        m[k] = None

    todo = [k for k in MANUAL if m[k] is None]
    if now is None:
        todo += ["seller_chat_now", "seller_chat_peak"]
    m["_todo"] = {k: MANUAL.get(k, "회차 날짜(date)가 없어 코호트를 못 나눴다 — 직접 넣을 것")
                  for k in todo}
    if rho is None:
        m["_todo"]["view_buy_rho"] = "회차가 3건 미만이라 순위상관을 못 낸다"
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", help="analyze_chat.py 가 만든 runs.json")
    ap.add_argument("-o", "--out", default="measures.json")
    a = ap.parse_args()

    with open(a.runs, encoding="utf-8") as f:
        runs = json.load(f)
    m = build(runs)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(m, f, ensure_ascii=False, indent=2)

    print(f"{m['_source']}")
    print(f"  조회수 {m['views']:,} · 구매자 {m['buyers']:,} · "
          f"전환 {m['buyers'] / m['views'] * 100:.3f}%")
    print(f"  순위상관 rho = {m['view_buy_rho']}  "
          f"(음수면 '밀어주는 콘텐츠와 팔리는 콘텐츠가 반대')")
    print(f"  죽은구간 {m['dead_ratio']}% · 상위3품목 {m['top3_share']}%")
    if m["_todo"]:
        print(f"\n직접 채울 것 {len(m['_todo'])}개 — {a.out} 의 _todo 참조:")
        for k, why in m["_todo"].items():
            print(f"  · {k:<22} {why}")
    print(f"\n→ {a.out}")


if __name__ == "__main__":
    main()
