#!/usr/bin/env python3
"""전환 구조 스코어카드 — 4층 × 25점 = 100점.

측정치를 넣으면 점수·처방 우선순위가 나온다. 배점과 구간은 자체 기준이며
업계 절대 등급이 아니다. "어디를 먼저 고칠지" 정하는 도구로만 쓴다.

사용:
  python3 scorecard.py measures.json
  python3 scorecard.py --example        # 옐로우베리 실측치로 검증 (18점)
"""
import json
import sys

# (코드, 이름, 만점, 층)
ITEMS = [
    ("A1", "구매전환율",        10, "A"),
    ("A2", "유입–구매 정합성",   8, "A"),
    ("A3", "실참여자 비율",      7, "A"),
    ("B1", "인앱 결제",         10, "B"),
    ("B2", "결제까지 홉 수",     8, "B"),
    ("B3", "게스트 결제",        7, "B"),
    ("C1", "충동구매 가격대 비중", 10, "C"),
    ("C2", "매출 분산",          8, "C"),
    ("C3", "사이즈·옵션 커버리지", 7, "C"),
    ("D1", "진행자 응대",        9, "D"),
    ("D2", "방송 시간 활용",     8, "D"),
    ("D3", "VOD 롱테일 회수",    8, "D"),
]

LAYERS = {
    "A": "트래픽 품질 — 유입이 살 사람인가",
    "B": "결제 경로 — 사고 싶을 때 살 수 있나",
    "C": "상품 적합성 — 라이브에서 팔릴 물건인가",
    "D": "방송 운영 — 파는 행위를 하고 있나",
}

# A1·A3는 다른 항목 개선의 결과로 따라 움직이는 결과지표. 처방 합계에서 중복 제외.
RESULT_ITEMS = {"A1", "A3"}
# 자체 실행으로 닫을 수 없는 항목(플랫폼 구조 의존).
PLATFORM_ITEMS = {"B1", "B3"}


# 열거형 항목의 허용값 — measures.json 검증에 쓴다.
ENUMS = {
    "inapp_checkout":  {"full": 1.0, "partial": .5, "none": 0.0},
    "guest_checkout":  {"guest": 1.0, "social_1tap": .571, "signup_required": .143, "app_required": 0.0},
    "size_coverage":   {"broad": 1.0, "two": .571, "one_plus": .286, "single": .143},
    "vod_longtail":    {"all": 1.0, "30d": .75, "recent_few": .125, "live_only": 0.0},
}

NUMERIC = ["views", "buyers", "participants", "view_buy_rho", "hops",
           "impulse_price_share", "top3_share", "seller_chat_now",
           "seller_chat_peak", "dead_ratio"]

# 0 이면 나눗셈이 터지는 값들
NONZERO = {"views": "조회수", "seller_chat_peak": "진행자 채팅 최고 코호트"}


def validate(m):
    """빠져 있거나 잘못된 입력을 트레이스백 대신 사람이 읽는 말로 알린다."""
    problems = []
    todo = m.get("_todo", {})
    for k in NUMERIC:
        if m.get(k) is None:
            hint = todo.get(k, "")
            problems.append(f"  · {k} 없음" + (f" — {hint}" if hint else ""))
        elif not isinstance(m[k], (int, float)):
            problems.append(f"  · {k} 는 숫자여야 한다 (지금: {m[k]!r})")
    for k, table in ENUMS.items():
        v = m.get(k)
        if v is None:
            hint = todo.get(k, "")
            problems.append(f"  · {k} 없음" + (f" — {hint}" if hint else ""))
        elif v not in table:
            problems.append(f"  · {k} = {v!r} 는 허용값이 아니다. "
                            f"가능한 값: {' / '.join(table)}")
    for k, label in NONZERO.items():
        if isinstance(m.get(k), (int, float)) and m[k] == 0:
            problems.append(f"  · {k}({label})가 0이라 비율을 낼 수 없다")
    if problems:
        raise SystemExit(
            "measures.json 을 채워야 채점할 수 있다:\n" + "\n".join(problems)
            + "\n\nmake_measures.py 로 자동 채울 수 있는 값은 채우고, "
              "나머지는 references/04-scorecard.md 를 참고할 것."
        )


def band(value, cuts):
    """cuts = [(임계값, 비율), ...] 내림차순. value 이상인 첫 구간의 비율을 쓴다."""
    for threshold, ratio in cuts:
        if value >= threshold:
            return ratio
    return cuts[-1][1]


def band_desc(value, cuts):
    """작을수록 좋은 지표용 — cuts는 오름차순 (임계값 이하, 비율)."""
    for threshold, ratio in cuts:
        if value <= threshold:
            return ratio
    return cuts[-1][1]


def score(m):
    """m: 측정치 dict → {코드: (획득점수, 만점, 근거문자열)}"""
    validate(m)
    r = {}

    # ---- A · 트래픽 품질 ----
    conv = m["buyers"] / m["views"] * 100  # 구매전환율 %
    r["A1"] = (band(conv, [(2.0, 1.0), (1.0, .8), (0.6, .6), (0.5, .4), (0.25, .2), (0, 0)]),
               f"구매자 {m['buyers']:,}명 ÷ 조회수 {m['views']:,} = {conv:.3f}%")

    rho = m["view_buy_rho"]  # 조회수 순위 vs 1천뷰당 구매자 순위의 스피어만 상관
    r["A2"] = (band(rho, [(0.6, 1.0), (0.3, .75), (0.0, .5), (-0.3, .25), (-1, .125)]),
               f"조회수 순위 대 전환 순위 상관 ρ={rho:+.2f}")

    part = m["participants"] / m["views"] * 100  # 실참여자 비율 %
    r["A3"] = (band(part, [(3.0, 1.0), (1.5, .714), (0.8, .571), (0.4, .429), (0.25, .286), (0, .143)]),
               f"채팅 참여자 {m['participants']:,}명 ÷ 조회수 = {part:.2f}%")

    # ---- B · 결제 경로 ----
    r["B1"] = (ENUMS["inapp_checkout"][m["inapp_checkout"]],
               f"인앱 결제 = {m['inapp_checkout']}")

    hops = m["hops"]
    r["B2"] = (band_desc(hops, [(1, 1.0), (2, .75), (3, .375), (4, .125), (99, 0)]),
               f"결제까지 {hops}홉 — {' → '.join(m.get('hop_path', []))}" if m.get("hop_path")
               else f"결제까지 {hops}홉")

    r["B3"] = (ENUMS["guest_checkout"][m["guest_checkout"]],
               f"게스트 결제 = {m['guest_checkout']}")

    # ---- C · 상품 적합성 ----
    imp = m["impulse_price_share"]  # 2~5만원대 비중 %
    r["C1"] = (band(imp, [(30, 1.0), (20, .7), (10, .4), (5, .2), (0, .1)]),
               f"충동구매 가격대 비중 {imp:.1f}% (기준선 30%)")

    top3 = m["top3_share"]  # 상위 3품목 주문 점유율 %
    r["C2"] = (band_desc(top3, [(30, 1.0), (45, .75), (60, .375), (80, .25), (100, .125)]),
               f"상위 3품목이 주문의 {top3:.1f}%")

    r["C3"] = (ENUMS["size_coverage"][m["size_coverage"]],
               f"사이즈 커버리지 = {m['size_coverage']}")

    # ---- D · 방송 운영 ----
    ratio = m["seller_chat_now"] / m["seller_chat_peak"]  # 자기 채널 최고 코호트 대비
    r["D1"] = (band(ratio, [(0.8, 1.0), (0.5, .667), (0.3, .444), (0.2, .222), (0, .111)]),
               f"셀러 채팅 {m['seller_chat_now']:.0f}건 / 최고 코호트 {m['seller_chat_peak']:.0f}건 = {ratio:.2f}배")

    dead = m["dead_ratio"]  # 죽은 10분 구간 비율 %
    r["D2"] = (band_desc(dead, [(10, 1.0), (25, .75), (40, .5), (60, .25), (100, .125)]),
               f"죽은 10분 구간 {dead:.1f}%")

    r["D3"] = (ENUMS["vod_longtail"][m["vod_longtail"]],
               f"VOD 롱테일 = {m['vod_longtail']}")

    out = {}
    for code, name, full, layer in ITEMS:
        ratio_, why = r[code]
        out[code] = {
            "name": name, "layer": layer, "full": full,
            "points": round(ratio_ * full),
            "ratio": ratio_, "why": why,
        }
    return out


def report(m):
    s = score(m)
    total = sum(v["points"] for v in s.values())
    lines = [f"전환 구조 점수  {total}/100", ""]

    for layer, title in LAYERS.items():
        codes = [c for c, _, _, l in ITEMS if l == layer]
        sub = sum(s[c]["points"] for c in codes)
        cap = sum(s[c]["full"] for c in codes)
        lines.append(f"{layer} · {title}   {sub}/{cap}")
        for c in codes:
            v = s[c]
            flag = " [결과지표]" if c in RESULT_ITEMS else (" [플랫폼]" if c in PLATFORM_ITEMS else "")
            lines.append(f"   {c} {v['name']:<16} {v['points']:>2}/{v['full']:<2}{flag}  {v['why']}")
        lines.append("")

    # 자체 실행으로 회복 가능한 여유분 — 결과지표·플랫폼 항목 제외
    own = [c for c, _, _, _ in ITEMS if c not in RESULT_ITEMS and c not in PLATFORM_ITEMS]
    gap = sum(s[c]["full"] - s[c]["points"] for c in own)
    plat = sum(s[c]["full"] - s[c]["points"] for c in PLATFORM_ITEMS)
    res = sum(s[c]["full"] - s[c]["points"] for c in RESULT_ITEMS)
    lines += [
        f"자체 실행 여지(이론상 최대)  +{gap}",
        f"  └ 실행 계획에 쓸 값은 항목별로 목표점을 따로 잡아 합산한다 — 만점을 목표로 잡지 말 것.",
        f"    (원 보고서는 7개 항목에 목표점을 잡아 +28로 제출했다. 이론상 최대의 약 절반이다.)",
        f"플랫폼 구조 의존          {plat}",
        f"결과지표 연동             {res}   (다른 항목이 오르면 따라 오름)",
        "",
        "먼저 고칠 곳 — 만점 대비 손실이 큰 순 (자체 실행 항목만):",
    ]
    rank = sorted(own, key=lambda c: s[c]["points"] - s[c]["full"])
    for c in rank[:5]:
        v = s[c]
        lines.append(f"   {c} {v['name']}  {v['points']}/{v['full']}  (−{v['full'] - v['points']})")
    return "\n".join(lines), total


# 옐로우베리 46회차 실측치 — 스코어카드 회귀 테스트용 고정 입력
EXAMPLE = {
    "views": 422400, "buyers": 1536, "participants": 1330,
    "view_buy_rho": -0.882,   # 원본 13회차에서 실제 계산한 값
    "inapp_checkout": "none", "hops": 4,
    "hop_path": ["youtube", "인포크링크", "fple.live", "카카오 로그인", "주문"],
    "guest_checkout": "signup_required",
    "impulse_price_share": 2.2, "top3_share": 56.8, "size_coverage": "one_plus",
    "seller_chat_now": 130, "seller_chat_peak": 593,
    "dead_ratio": 52.3, "vod_longtail": "recent_few",
}

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--example":
        text, total = report(EXAMPLE)
        print(text)
        expected = 18
        print()
        print(f"회귀 검증: 원 보고서 {expected}점 / 재계산 {total}점 — "
              + ("일치" if total == expected else "불일치! 배점 구간을 확인할 것"))
        sys.exit(0 if total == expected else 1)
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    with open(sys.argv[1], encoding="utf-8") as f:
        print(report(json.load(f))[0])
