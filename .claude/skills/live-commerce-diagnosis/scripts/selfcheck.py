#!/usr/bin/env python3
"""스킬 자체의 정합성을 점검한다. 기계로 확인 가능한 항목만.

스킬을 고친 뒤 돌린다 — 문서와 코드가 어긋났는지(필드명·열거형·스크립트명),
스크립트가 여전히 도는지, 채점 회귀가 유지되는지를 한 번에 본다.

  python3 scripts/selfcheck.py                 # 이 스킬을 점검
  AUDIT_E2E=<픽스처디렉터리> python3 scripts/selfcheck.py   # 파이프라인 완주까지

종료 코드 0 = 전부 통과.
"""
import json, os, re, subprocess, sys, tempfile, shutil

SKILL = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))
results = []          # (코드, 이름, 만점, 획득, 근거)

def add(code, name, full, got, why):
    results.append((code, name, full, got, why))

def sh(cmd, cwd=None):
    p = subprocess.run(cmd, shell=True, cwd=cwd or SKILL,
                       capture_output=True, text=True, timeout=180)
    return p.returncode, p.stdout, p.stderr

def read(rel):
    with open(os.path.join(SKILL, rel), encoding="utf-8") as f:
        return f.read()

# ─────────── A · 구조 (20) ───────────
skill_md = read("SKILL.md")
fm = re.match(r"^---\n(.*?)\n---\n", skill_md, re.S)
if fm and "name:" in fm.group(1) and "description:" in fm.group(1):
    desc = re.search(r"description:\s*(.+)", fm.group(1)).group(1)
    add("A1", "frontmatter 유효", 5, 5, f"name+description 존재 (desc {len(desc)}자)")
else:
    add("A1", "frontmatter 유효", 5, 0, "name 또는 description 누락")

n = skill_md.count("\n")
add("A2", "SKILL.md 길이", 3, 3 if n < 500 else 0, f"{n}줄 (기준 500 미만)")

# SKILL.md 가 참조하는 파일이 전부 실존하는가
refs = set(re.findall(r"`?((?:references|scripts|assets)/[\w./-]+)`?", skill_md))
missing = [r for r in sorted(refs) if not os.path.exists(os.path.join(SKILL, r))]
add("A3", "참조 경로 실존", 5, 5 if not missing else 0,
    f"{len(refs)}개 참조" + ("" if not missing else f" · 없음: {missing}"))

# 반대로, 존재하는 references 가 전부 SKILL.md 또는 README 에서 언급되는가
readme = read("README.md") if os.path.exists(os.path.join(SKILL, "README.md")) else ""
allrefs = sorted(os.listdir(os.path.join(SKILL, "references")))
orphan = [r for r in allrefs if r not in skill_md and r not in readme]
add("A4", "고아 문서 없음", 4, 4 if not orphan else 0,
    f"references {len(allrefs)}개" + ("" if not orphan else f" · 미언급: {orphan}"))

SELF = os.path.basename(__file__)
# 존재 확인·문서 대조에는 자기 자신도 포함한다.
scripts = sorted(f for f in os.listdir(os.path.join(SKILL, "scripts"))
                 if f.endswith((".py", ".sh")))
# 실행 검사에서만 뺀다 — 넣으면 selfcheck 가 selfcheck 를 부른다.
runnable = [f for f in scripts if f != SELF]
noexec = [f for f in scripts if not os.access(os.path.join(SKILL, "scripts", f), os.X_OK)]
add("A5", "스크립트 실행권한", 3, 3 if not noexec else 0,
    f"{len(scripts)}개" + ("" if not noexec else f" · 권한없음: {noexec}"))

# ─────────── B · 코드 건전성 (30) ───────────
rc, _, err = sh(f"python3 -m py_compile {' '.join('scripts/'+f for f in scripts if f.endswith('.py'))}")  # 문법은 자기 자신도 검사
add("B1", "파이썬 문법", 5, 5 if rc == 0 else 0, "통과" if rc == 0 else err.strip()[:120])

shs = [f for f in runnable if f.endswith(".sh")]
rc2 = all(sh(f"bash -n scripts/{f}")[0] == 0 for f in shs)
add("B2", "셸 문법", 3, 3 if rc2 else 0, f"{len(shs)}개 통과" if rc2 else "실패")

rc, out, _ = sh("python3 scripts/scorecard.py --example")
ok = rc == 0 and "18/100" in out and "일치" in out
add("B3", "채점 회귀 18/100", 8, 8 if ok else 0, "재현" if ok else "불일치")

# 인자 없이 실행해도 트레이스백 없이 안내가 나오는가
bad = []
for f in [f for f in runnable if f.endswith(".py")]:
    rc, out, err = sh(f"python3 scripts/{f}")
    if "Traceback" in err:
        bad.append(f)
add("B4", "인자 없이 실행 시 안내", 5, 5 if not bad else 0,
    "전부 안내 출력" if not bad else f"트레이스백: {bad}")

# 잘못된 입력에 안내가 나오는가
tmp = tempfile.mkdtemp()
json.dump({"views": 0, "buyers": 0}, open(f"{tmp}/bad.json", "w"))
rc, out, err = sh(f"python3 scripts/scorecard.py {tmp}/bad.json")
ok = "Traceback" not in err and ("채워야" in out + err or "채워야" in err)
add("B5", "잘못된 입력에 안내", 5, 5 if ok else 0,
    "안내 출력" if ok else "트레이스백 또는 무응답")

# 번들 픽스처로 전 구간 완주 + 값 회귀 (assets/testdata)
FIX = os.path.join(SKILL, "assets", "testdata")
EXPECT = {"chats": 100, "participants": 65, "orders": 20, "buyers": 10,
          "buyers_per_1k": 1.0, "first20_share_pct": 60.0, "dead_ratio_pct": 80.0,
          "orders_per_buyer": 2.0, "top3_share_pct": 75.0}
if os.path.isdir(FIX):
    rc, _, err = sh(f'python3 scripts/analyze_chat.py "{FIX}/sample.live_chat.json" '
                    f'--views "{FIX}/views.json" -o {tmp}/runs.json')
    rc2, _, _ = sh(f"python3 scripts/make_measures.py {tmp}/runs.json -o {tmp}/m.json")
    if rc == 0 and os.path.exists(f"{tmp}/runs.json"):
        got = json.load(open(f"{tmp}/runs.json", encoding="utf-8"))[0]
        wrong = {k: got.get(k) for k, v in EXPECT.items()
                 if got.get(k) is None or abs(got[k] - v) > 0.051}
        ok = not wrong and rc2 == 0
        add("B6", "번들 픽스처 값 회귀", 4, 4 if ok else 0,
            "9개 지표 정답 일치 · 집계까지 통과" if ok else f"불일치 {wrong}")
    else:
        add("B6", "번들 픽스처 값 회귀", 4, 0, f"분석 실패: {err.strip()[:80]}")
else:
    add("B6", "번들 픽스처 값 회귀", 4, 0, "assets/testdata 없음")

# ─────────── C · 문서·코드 정합성 (25) ───────────
docs = {p: read(p) for p in
        ["SKILL.md", "README.md"] + [f"references/{r}" for r in allrefs]}
alldoc = "\n".join(docs.values())

# C1 문서에 등장하는 scripts/파일 이 실존하는가
doc_scripts = set(re.findall(r"scripts/([\w.-]+\.(?:py|sh))", alldoc))
ghost = sorted(s for s in doc_scripts if s not in scripts)
add("C1", "문서의 스크립트명 정확", 8, 8 if not ghost else 0,
    f"{len(doc_scripts)}개 언급" + ("" if not ghost else f" · 없는 파일: {ghost}"))

# C2 문서에 나오는 지표 필드명이 실제 산출 키에 존재하는가
analyze = read("scripts/analyze_chat.py")
out_keys = set(re.findall(r'^\s*"(\w+)":', analyze, re.M))
doc_fields = set(re.findall(r"`(buyers_per_1k|first20_share_pct|dead_ratio_pct|intent_per_1k|"
                            r"chats_without_timestamp|pre_show_chats|top3_share_pct|"
                            r"orders_per_min|participants_pct|seller_rate_pct)`", alldoc))
missf = sorted(f for f in doc_fields if f not in out_keys)
add("C2", "문서의 지표 필드명 정확", 8, 8 if not missf else 0,
    f"{len(doc_fields)}개 대조" + ("" if not missf else f" · 코드에 없음: {missf}"))

# C3 열거형 허용값이 문서와 코드에서 일치
sc = read("scripts/scorecard.py")
enum_blk = re.search(r"ENUMS = \{(.*?)\n\}", sc, re.S).group(1)
code_enums = {k: set(re.findall(r'"([\w]+)":', v))
              for k, v in re.findall(r'"(\w+)":\s*\{([^}]*)\}', enum_blk)}
mismatch = []
for key, vals in code_enums.items():
    for v in vals:
        # 문서 어딘가에 그 값이 나와야 한다
        if f"`{v}`" not in alldoc and f'"{v}"' not in alldoc:
            mismatch.append(f"{key}.{v}")
add("C3", "열거형 값 문서화", 5, 5 if not mismatch else 0,
    f"{sum(len(v) for v in code_enums.values())}개 값" +
    ("" if not mismatch else f" · 문서 누락: {mismatch}"))

# C4 make_measures 의 수동 항목이 문서에 전부 설명돼 있는가
mm = read("scripts/make_measures.py")
manual = set(re.findall(r'^\s{4}"(\w+)":', re.search(r"MANUAL = \{(.*?)\n\}", mm, re.S).group(1), re.M))
undoc = sorted(m for m in manual if m not in alldoc)
add("C4", "수동 입력 항목 문서화", 4, 4 if not undoc else 0,
    f"{len(manual)}개" + ("" if not undoc else f" · 미문서화: {undoc}"))

shutil.rmtree(tmp, ignore_errors=True)

# ─────────── 출력 ───────────
GROUPS = {"A": "구조", "B": "코드 건전성", "C": "문서·코드 정합성"}
total = sum(g for _, _, _, g, _ in results)
full = sum(f for _, _, f, _, _ in results)
print(f"스킬 정합성 점검   {total}/{full}   ({os.path.basename(SKILL)})\n")
for gk, gname in GROUPS.items():
    rows = [r for r in results if r[0][0] == gk]
    print(f"{gk} · {gname}   {sum(r[3] for r in rows)}/{sum(r[2] for r in rows)}")
    for code, name, f_, g_, why in rows:
        mark = "PASS" if g_ == f_ else "FAIL"
        print(f"   [{mark}] {code} {name:<22} {g_}/{f_}  {why}")
    print()
fails = [r for r in results if r[3] < r[2]]
if fails:
    print("고칠 것:")
    for code, name, f_, g_, why in fails:
        print(f"  · {code} {name} — {why}")
else:
    print("기계 검증 항목 전부 통과.")
sys.exit(0 if not fails else 1)
