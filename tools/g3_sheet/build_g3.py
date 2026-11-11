#!/usr/bin/env python3
"""G3 경제·밸런스 시뮬레이션 워크북 생성기 (docs/G3-economy-simulation-sheet.md 구현).

출력 : data/g3/G3-economy-simulation.xlsx
사용 : python3 -I tools/g3_sheet/build_g3.py [--recalc /path/to/recalc.py] [--no-snapshot]

- 모든 계산은 엑셀 수식이다(결과값 하드코딩 없음). 입력은 파란 글씨.
- 시나리오 비교표(Scenarios의 스냅샷)만 스크립트가 시나리오별로 재계산해 붙인 **정적 값**이다.
- 모든 수치는 [제안]이며 실측으로 교체한다.
"""
import argparse
import datetime
import json
import random
import subprocess
import sys
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.comments import Comment
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter as CL
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "g3" / "G3-economy-simulation.xlsx"
DEFAULT_RECALC = Path("/root/.claude/skills/synced/baf91e1b-9a7e-4319-a8ac-e2940f25754a_ca96c540-674a-4438-bf07-5afee182726f/xlsx/scripts/recalc.py")

# ---------- 스타일 ----------
FN = "Arial"
F_BASE = Font(name=FN, size=10)
F_BOLD = Font(name=FN, size=10, bold=True)
F_IN = Font(name=FN, size=10, color="0000FF")
F_LINK = Font(name=FN, size=10, color="008000")
F_HDR = Font(name=FN, size=10, bold=True, color="FFFFFF")
F_TITLE = Font(name=FN, size=14, bold=True)
F_NOTE = Font(name=FN, size=9, italic=True, color="595959")
FILL_HDR = PatternFill("solid", fgColor="1F3864")
FILL_SEC = PatternFill("solid", fgColor="D9E1F2")
FILL_KEY = PatternFill("solid", fgColor="FFFF00")
FILL_OUT = PatternFill("solid", fgColor="F2F2F2")

NUM = '#,##0;(#,##0);-'
NUM1 = '#,##0.0;(#,##0.0);-'
NUM2 = '#,##0.00;(#,##0.00);-'
PCT = '0.0%'
RATIO = '0.000'


def put(ws, ref, value, kind="f", fmt=None, key=False, bold=False, wrap=False, align=None):
    c = ws[ref]
    c.value = value
    c.font = {"f": F_BASE, "in": F_IN, "link": F_LINK, "label": F_BASE, "hdr": F_HDR, "title": F_TITLE, "note": F_NOTE, "bold": F_BOLD}[kind]
    if kind == "hdr":
        c.fill = FILL_HDR
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    if key:
        c.fill = FILL_KEY
    if fmt:
        c.number_format = fmt
    if wrap or align:
        c.alignment = Alignment(wrap_text=wrap, horizontal=align, vertical="top" if wrap else None)
    if bold and kind != "hdr":
        c.font = Font(name=FN, size=10, bold=True, color=c.font.color.rgb if c.font.color and c.font.color.rgb else None)
    return c


def hdr_row(ws, row, labels, start_col=1):
    for i, lab in enumerate(labels):
        put(ws, f"{CL(start_col + i)}{row}", lab, "hdr")
    ws.row_dimensions[row].height = 30


def widths(ws, spec):
    for col, w in spec.items():
        ws.column_dimensions[col].width = w


def section(ws, row, text, ncols=4):
    for i in range(ncols):
        ws[f"{CL(1 + i)}{row}"].fill = FILL_SEC
    put(ws, f"A{row}", text, "bold")
    ws[f"A{row}"].fill = FILL_SEC


def status_format(ws, rng):
    ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=['"OK"'], fill=PatternFill("solid", bgColor="C6EFCE", fgColor="C6EFCE"), font=Font(name=FN, color="006100")))
    ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=['"검토"'], fill=PatternFill("solid", bgColor="FFC7CE", fgColor="FFC7CE"), font=Font(name=FN, color="9C0006")))


# ---------- 데이터 ----------
JOBS = ["농부", "광부", "요리사", "어부"]
BANDS = ["초급", "중급", "고급"]

# (item_id, job, name, P_base, rates(초급,중급,고급), unit_cost)
ITEMS = [
    ("farm:wheat", "농부", "밀", 12, (45, 70, 110), 0),
    ("farm:carrot", "농부", "당근", 15, (34, 55, 85), 0),
    ("farm:pumpkin", "농부", "호박", 28, (16, 28, 45), 0),
    ("mine:coal", "광부", "석탄", 10, (45, 70, 100), 0),
    ("mine:iron_ore", "광부", "철광석", 38, (17, 28, 42), 0),
    ("mine:gold_ore", "광부", "금광석", 120, (3, 6, 10), 0),
    ("cook:grilled_fish_set", "요리사", "구운 생선 정식", 140, (7, 10, 15), 55),
    ("cook:veg_stew", "요리사", "채소 스튜", 90, (10, 16, 24), 35),
    ("cook:golden_pie", "요리사", "황금 파이", 320, (2, 3.5, 6), 120),
    ("fish:crucian", "어부", "붕어", 18, (30, 47, 62), 0),
    ("fish:salmon", "어부", "연어", 45, (12, 20, 32), 0),
    ("fish:rare", "어부", "희귀어", 260, (1.5, 2.8, 4.6), 0),
]
JOB_COST = {  # 시간당 비용 (초급, 중급, 고급) — 씨앗·입장·연료·미끼 등
    "농부": (150, 250, 420),
    "광부": (80, 150, 260),
    "요리사": (60, 100, 180),
    "어부": (100, 180, 300),
}

SCENARIOS = [
    # name, ccu_mult, farmer_mult, alpha_add, enh_delta, gacha_price_mult
    ("1. 기본", 1.0, 1.0, 0.0, 0.0, 1.0),
    ("2. 인구 2배", 2.0, 1.0, 0.0, 0.0, 1.0),
    ("3. 인구 0.5배", 0.5, 1.0, 0.0, 0.0, 1.0),
    ("4. 농부 쏠림(약 70%)", 1.0, 7.0, 0.0, 0.0, 1.0),
    ("5. 시세 민감도 상승(alpha +0.3)", 1.0, 1.0, 0.3, 0.0, 1.0),
    ("6. 강화 성공률 -5%p", 1.0, 1.0, 0.0, -0.05, 1.0),
    ("7. 가구 뽑기 가격 -20%", 1.0, 1.0, 0.0, 0.0, 0.8),
]

ENH_S = [0.95, 0.90, 0.85, 0.80, 0.75, 0.65, 0.60, 0.55, 0.50, 0.45, 0.40, 0.35, 0.30, 0.27, 0.24, 0.20, 0.18, 0.16, 0.14, 0.12]
ENH_D = [0, 0, 0, 0, 0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.12, 0.14, 0.16, 0.18, 0.20]


def load_archetypes():
    sys.path.insert(0, str(ROOT / "tools" / "weapon_catalog"))
    import gen  # noqa
    cfg = gen.load("archetypes.json")
    out = []
    for a in cfg["archetypes"]:
        base = gen.template_base(a, cfg)
        out.append((a["id"], a["name_ko"], 1 if a["aoe"] else 0, base, [(h["factor"], h["cooldown"]) for h in a["left"]]))
    return out, cfg["target_dps"], cfg["target_dps_aoe"]


# ---------- 난수 시뮬레이션 ----------
def _stats(xs):
    xs = sorted(xs)
    n = len(xs)

    def q(p):
        return xs[min(n - 1, int(p * (n - 1)))]
    return {"mean": sum(xs) / n, "p50": q(0.50), "p90": q(0.90), "p95": q(0.95), "p99": q(0.99), "max": xs[-1]}


def run_mc(v, n_enh=50000, n_first=100000, n_spec=20000, n_full=2000, seed=20261111):
    """v: Enhance/Gacha 입력(재계산된 값). 모든 난수는 시드 고정."""
    rng = random.Random(seed)
    S_, K_, D_, C_ = v["s"], v["k"], v["d"], v["c"]
    start = v["start_price"]
    levels = sorted(set([5, 8, 10, 12, 15, int(v["target_lv"])]))
    maxl = max(levels)
    acc = {L: {"cost": [], "destroy": [], "attempts": []} for L in levels}
    for _ in range(n_enh):
        cost = start
        n = 0
        destroys = 0
        attempts = 0
        done = set()
        while n < maxl:
            attempts += 1
            cost += C_[n]
            u = rng.random()
            if u < S_[n]:
                n += 1
                if n in acc and n not in done:
                    done.add(n)
                    acc[n]["cost"].append(cost)
                    acc[n]["destroy"].append(destroys)
                    acc[n]["attempts"].append(attempts)
            elif u < S_[n] + K_[n]:
                pass
            else:
                destroys += 1
                cost += start
                n = 0
    enh = {}
    for L in levels:
        st = _stats(acc[L]["cost"])
        dl = acc[L]["destroy"]
        st["destroy_prob"] = sum(1 for x in dl if x > 0) / len(dl)
        st["destroy_mean"] = sum(dl) / len(dl)
        st["attempts_mean"] = sum(acc[L]["attempts"]) / len(acc[L]["attempts"])
        enh[L] = st
    tl = int(v["target_lv"])
    tc = sorted(acc[tl]["cost"])
    pts = [0.01, 0.05] + [x / 100 for x in range(10, 100, 10)] + [0.95, 0.99]
    cdf = {"p": pts, "cost": [tc[min(len(tc) - 1, int(p * (len(tc) - 1)))] for p in pts]}
    mean_t = enh[tl]["mean"]
    edges = [0.5, 1.0, 1.5, 2.0, 3.0, 4.0]
    counts = [0] * (len(edges) + 1)
    for x in tc:
        r_ = x / mean_t
        i = 0
        while i < len(edges) and r_ >= edges[i]:
            i += 1
        counts[i] += 1
    hist_enh = {"edges": edges, "counts": counts}

    pc, pr, pe, pl = v["g_common"], v["g_rare"], v["g_epic"], v["g_legend"]
    pity = int(v["pity"])
    nl = int(v["n_legend"])
    forced_leg = pl / (pe + pl)

    def draw(counter):
        r_ = rng.random()
        if counter >= pity - 1:
            return 3 if r_ < forced_leg else 2
        if r_ < pc:
            return 0
        if r_ < pc + pr:
            return 1
        if r_ < pc + pr + pe:
            return 2
        return 3

    first_epic, first_leg = [], []
    for _ in range(n_first):
        counter = 0
        pulls = 0
        fe = None
        while True:
            pulls += 1
            t = draw(counter)
            if t >= 2:
                counter = 0
                if fe is None:
                    fe = pulls
                if t == 3:
                    break
            else:
                counter += 1
        first_epic.append(fe)
        first_leg.append(pulls)
    spec = []
    for _ in range(n_spec):
        counter = 0
        pulls = 0
        while True:
            pulls += 1
            t = draw(counter)
            if t >= 2:
                counter = 0
            if t == 3 and rng.random() < 1.0 / nl:
                break
            if t < 2:
                counter += 1
        spec.append(pulls)
    pools = [int(v["n_common"]), int(v["n_rare"]), int(v["n_epic"]), nl]
    total_items = sum(pools)
    full = []
    for _ in range(n_full):
        owned = [set() for _ in pools]
        have = 0
        counter = 0
        pulls = 0
        while have < total_items:
            pulls += 1
            t = draw(counter)
            if t >= 2:
                counter = 0
            else:
                counter += 1
            it = rng.randrange(pools[t])
            if it not in owned[t]:
                owned[t].add(it)
                have += 1
        full.append(pulls)
    lb = [25, 50, 100, 150, 200, 300, 400, 600]
    lc = [0] * (len(lb) + 1)
    for x in first_leg:
        i = 0
        while i < len(lb) and x > lb[i]:
            i += 1
        lc[i] += 1
    return {
        "seed": seed, "date": datetime.date.today().isoformat(),
        "n_enh": n_enh, "n_first": n_first, "n_spec": n_spec, "n_full": n_full,
        "levels": levels, "enh": enh, "target_level": tl, "cdf": cdf, "hist_enh": hist_enh,
        "g_epic": _stats(first_epic), "g_leg": _stats(first_leg), "g_spec": _stats(spec), "g_full": _stats(full),
        "hist_leg": {"edges": lb, "counts": lc},
    }


def build_mc_sheet(ws, P, mc):
    put(ws, "A1", "MonteCarlo — 난수 시뮬레이션 결과 (강화 비용 분위·뽑기 분포)", "title")
    if mc is None:
        put(ws, "A3", "(미생성) build_g3.py 실행 시 채워진다.", "note")
        P["mc_p90_ratio"] = "MonteCarlo!$A$3"
        P["mc_leg_ratio"] = "MonteCarlo!$A$3"
        return
    put(ws, "A2", f"스크립트(build_g3.py)가 기본 시나리오 입력으로 돌린 **정적 결과**다. 시드 {mc['seed']}(고정), 생성일 {mc['date']}, 강화 {mc['n_enh']:,}회·뽑기 {mc['n_first']:,}/{mc['n_spec']:,}/{mc['n_full']:,}회 시행. 파란 칸이 아닌 값은 입력이 바뀌면 스크립트로 다시 생성해야 한다.", "note")
    put(ws, "A3", "강화 알고리즘: 장비 구매 → 단계마다 비용 지불 후 성공/유지/파괴 판정 → 파괴 시 장비 재구매 + 0단계부터 재시작 (Enhance 시트의 분석식과 같은 모델)", "note")
    # --- 1. 강화 ---
    section(ws, 5, "1. 강화 — 목표 단계별 총비용 분포 (장비 구매가 포함)", 14)
    hdr_row(ws, 6, ["목표 단계(+)", "분석 기대 비용(수식)", "MC 평균", "MC÷분석", "P50", "P90", "P95", "P99", "P90÷평균", "파괴 1회 이상 확률", "평균 파괴 횟수", "평균 시도 수", "P50 소요 일수", "P90 소요 일수"])
    first = 7
    target_row = None
    for i, L in enumerate(mc["levels"]):
        r = first + i
        st = mc["enh"][L]
        put(ws, f"A{r}", L, "label", "0")
        put(ws, f"B{r}", f"={P['start_price']}+INDEX(Enhance!$N$6:$N$25,A{r})", "f", NUM)
        put(ws, f"C{r}", st["mean"], "label", NUM)
        put(ws, f"D{r}", f"=C{r}/B{r}", "f", RATIO)
        put(ws, f"E{r}", st["p50"], "label", NUM)
        put(ws, f"F{r}", st["p90"], "label", NUM)
        put(ws, f"G{r}", st["p95"], "label", NUM)
        put(ws, f"H{r}", st["p99"], "label", NUM)
        put(ws, f"I{r}", f"=F{r}/C{r}", "f", NUM2)
        put(ws, f"J{r}", st["destroy_prob"], "label", PCT)
        put(ws, f"K{r}", st["destroy_mean"], "label", NUM2)
        put(ws, f"L{r}", st["attempts_mean"], "label", NUM1)
        put(ws, f"M{r}", f"=E{r}/{P['enh_budget']}", "f", NUM1)
        put(ws, f"N{r}", f"=F{r}/{P['enh_budget']}", "f", NUM1)
        if L == mc["target_level"]:
            target_row = r
    last = first + len(mc["levels"]) - 1
    put(ws, f"A{last+1}", "※ 소요 일수 = 총비용 ÷ 중견 유저 강화 일 예산(Enhance 시트). 목표 단계 행은 Params의 목표 강화 단계와 같은 행이다.", "note")
    P["mc_p90_ratio"] = f"MonteCarlo!$I${target_row}"
    # --- 2. 예산 도달 확률 ---
    r0 = last + 3
    section(ws, r0, "2. 목표 단계 도달 확률 — 일수별 예산 (목표 단계 총비용 분포를 보간)", 6)
    hdr_row(ws, r0 + 1, ["경과 일수", "누적 예산(Coin)", "도달 확률"])
    cdf_p0 = r0 + 12
    cdf_c0 = cdf_p0
    put(ws, f"F{r0+1}", "분위(p)", "hdr")
    put(ws, f"G{r0+1}", "총비용(Coin)", "hdr")
    npts = len(mc["cdf"]["p"])
    for i in range(npts):
        put(ws, f"F{r0+2+i}", mc["cdf"]["p"][i], "label", PCT)
        put(ws, f"G{r0+2+i}", mc["cdf"]["cost"][i], "label", NUM)
    cp_first, cp_last = r0 + 2, r0 + 1 + npts
    for j, dday in enumerate([7, 14, 21, 30, 45]):
        r = r0 + 2 + j
        put(ws, f"A{r}", dday, "in", "0")
        put(ws, f"B{r}", f"=A{r}*{P['enh_budget']}", "f", NUM)
        idx = f"MATCH(B{r},$G${cp_first}:$G${cp_last},1)"
        pr_ = f"$F${cp_first}:$F${cp_last}"
        cr_ = f"$G${cp_first}:$G${cp_last}"
        put(ws, f"C{r}", f"=IF(B{r}<$G${cp_first},0,IF(B{r}>=$G${cp_last},1,INDEX({pr_},{idx})+(B{r}-INDEX({cr_},{idx}))/(INDEX({cr_},{idx}+1)-INDEX({cr_},{idx}))*(INDEX({pr_},{idx}+1)-INDEX({pr_},{idx}))))", "f", PCT)
    put(ws, f"A{r0+8}", "※ 분위 표(F:G)는 시뮬레이션의 정적 값이고, 예산은 Enhance 시트의 일 예산을 따라 바뀐다(분위 사이 선형 보간, 1% 미만·99% 초과는 0/100%로 처리).", "note")
    # --- 3. 가구 뽑기 ---
    g0 = max(cp_last, r0 + 8) + 3
    section(ws, g0, "3. 가구 뽑기 — 필요 뽑기 수 분포 (천장 반영, 1회 가격 기준 비용)", 12)
    hdr_row(ws, g0 + 1, ["항목", "분석 기대(수식)", "MC 평균", "MC÷분석", "P50", "P90", "P95", "P99", "평균 비용(Coin)", "P90 비용(Coin)", "P90 비용÷중견 월소득", "비고"])
    rows = [
        ("영웅 이상 첫 획득", "=Gacha!D14", mc["g_epic"], "천장 N회 보장"),
        ("전설 첫 획득", "=Gacha!D17", mc["g_leg"], "분석식은 천장 시 영웅+ 중 전설 비율 적용"),
        ("특정 전설 1종 획득", f"=Gacha!D17*{P['n_legend']}", mc["g_spec"], "풀의 특정 1종, 조각 교환 제외"),
        ("전체 컬렉션 완성", "=Gacha!D24", mc["g_full"], "분석식은 최대 티어 근사(보수적)"),
    ]
    for i, (nm, ana, st, note) in enumerate(rows):
        r = g0 + 2 + i
        put(ws, f"A{r}", nm, "label")
        put(ws, f"B{r}", ana, "f", NUM1)
        put(ws, f"C{r}", st["mean"], "label", NUM1)
        put(ws, f"D{r}", f"=C{r}/B{r}", "f", RATIO)
        put(ws, f"E{r}", st["p50"], "label", NUM)
        put(ws, f"F{r}", st["p90"], "label", NUM)
        put(ws, f"G{r}", st["p95"], "label", NUM)
        put(ws, f"H{r}", st["p99"], "label", NUM)
        put(ws, f"I{r}", f"=C{r}*{P['e_g1']}", "f", NUM)
        put(ws, f"J{r}", f"=F{r}*{P['e_g1']}", "f", NUM)
        put(ws, f"K{r}", f"=J{r}/Gacha!$D$19", "f", PCT)
        put(ws, f"L{r}", note, "note")
    P["mc_leg_ratio"] = f"MonteCarlo!$K${g0+3}"
    # --- 4. 히스토그램 ---
    h0 = g0 + 8
    section(ws, h0, "4. 분포(히스토그램)", 8)
    put(ws, f"A{h0+1}", "강화 총비용 ÷ 평균 (목표 단계)", "bold")
    he = mc["hist_enh"]
    labels = ["< 0.5×"] + [f"{he['edges'][i]}× ~ {he['edges'][i+1]}×" for i in range(len(he["edges"]) - 1)] + [f"≥ {he['edges'][-1]}×"]
    hdr_row(ws, h0 + 2, ["구간", "시행 수", "비율", "막대"])
    total = sum(he["counts"])
    c0 = h0 + 3
    for i, lab in enumerate(labels):
        r = c0 + i
        put(ws, f"A{r}", lab, "label")
        put(ws, f"B{r}", he["counts"][i], "label", NUM)
        put(ws, f"C{r}", f"=B{r}/SUM($B${c0}:$B${c0+len(labels)-1})", "f", PCT)
        put(ws, f"D{r}", f'=REPT("█",ROUND(C{r}*60,0))', "f")
    g1 = c0 + len(labels) + 1
    put(ws, f"A{g1}", "전설 첫 획득까지 뽑기 수", "bold")
    hl = mc["hist_leg"]
    labs = [f"≤ {hl['edges'][0]}"] + [f"{hl['edges'][i]+1} ~ {hl['edges'][i+1]}" for i in range(len(hl["edges"]) - 1)] + [f"> {hl['edges'][-1]}"]
    hdr_row(ws, g1 + 1, ["구간(회)", "시행 수", "비율", "막대"])
    c1 = g1 + 2
    for i, lab in enumerate(labs):
        r = c1 + i
        put(ws, f"A{r}", lab, "label")
        put(ws, f"B{r}", hl["counts"][i], "label", NUM)
        put(ws, f"C{r}", f"=B{r}/SUM($B${c1}:$B${c1+len(labs)-1})", "f", PCT)
        put(ws, f"D{r}", f'=REPT("█",ROUND(C{r}*60,0))', "f")
    put(ws, f"A{c1+len(labs)+1}", "※ 전설 확률 1%(천장 영웅+ 50회)에서 '평균 약 100회'여도 분포는 길게 늘어진다 — 평균만으로 부담을 판단하지 않는다.", "note")
    widths(ws, {"A": 26, "B": 18, "C": 14, "D": 12, "E": 12, "F": 14, "G": 14, "H": 14, "I": 14, "J": 16, "K": 18, "L": 36, "M": 14, "N": 14})
    ws.freeze_panes = "A5"


# ---------- 뽑기 천장 구조 비교 ----------
GC_SHARD_VALUE = (1, 3, 10, 30)  # 중복 시 조각(일반, 희귀, 영웅, 전설) [제안]
GC_STRUCTURES = [
    # id, 이름, 영웅+ 천장, 전설 하드 천장, 전설 소프트(시작, 회당 가산), 지정 선택 천장, 조각 교환 비용
    ("S0", "천장 없음", None, None, None, None, None),
    ("S1", "현행: 영웅+ 50회 천장", 50, None, None, None, None),
    ("S2", "영웅+ 50 + 전설 하드 150", 50, 150, None, None, None),
    ("S3", "영웅+ 50 + 전설 소프트(70회부터 +1.5%p/회)", 50, 150, (70, 0.015), None, None),
    ("S3b", "영웅+ 50 + 전설 소프트(90회부터 +0.6%p/회)", 50, 150, (90, 0.006), None, None),
    ("S4", "영웅+ 50 + 지정 전설 선택 천장 300", 50, None, None, 300, None),
    ("S5", "현행 + 조각 교환(지정 전설 400조각)", 50, None, None, None, 400),
    ("S6", "전설 하드 150 + 선택 천장 450 + 조각 400", 50, 150, None, 450, 400),
    ("S7", "추천 후보: 전설 하드 150 + 선택 450 + 조각 600", 50, 150, None, 450, 600),
]


def _sim_structure(rng, v, st, n_trials):
    _, _, epic_pity, leg_hard, soft, choice, shard_cost = st
    pc, pr, pe, pl = v["g_common"], v["g_rare"], v["g_epic"], v["g_legend"]
    pools = (int(v["n_common"]), int(v["n_rare"]), int(v["n_epic"]), int(v["n_legend"]))
    nl = pools[3]
    base_total = pc + pr + pe
    c_cut = pc / base_total
    r_cut = (pc + pr) / base_total
    rnd = rng.random
    rrange = rng.randrange
    first_leg, spec = [], []
    for _ in range(n_trials):
        c_epic = 0
        c_leg = 0
        pulls = 0
        fl = None
        owned = [bytearray(n) for n in pools] if shard_cost else None
        shards = 0
        while True:
            pulls += 1
            n_leg = c_leg + 1
            p_leg = pl
            if soft and n_leg >= soft[0]:
                p_leg = min(1.0, pl + (n_leg - soft[0] + 1) * soft[1])
            choice_hit = choice is not None and pulls >= choice
            if leg_hard is not None and n_leg >= leg_hard:
                t = 3
            elif epic_pity is not None and c_epic >= epic_pity - 1:
                t = 3 if rnd() < p_leg / (pe + p_leg) else 2
            else:
                r = rnd()
                if r < p_leg:
                    t = 3
                else:
                    r2 = (r - p_leg) / (1.0 - p_leg) if p_leg < 1.0 else 0.0
                    t = 0 if r2 < c_cut else (1 if r2 < r_cut else 2)
            if choice_hit:
                t = 3
            if t >= 2:
                c_epic = 0
            else:
                c_epic += 1
            if t == 3:
                c_leg = 0
                if fl is None:
                    fl = pulls
            else:
                c_leg += 1
            done = False
            if shard_cost:
                it = rrange(pools[t])
                if choice_hit and t == 3:
                    it = 0
                if owned[t][it]:
                    shards += GC_SHARD_VALUE[t]
                else:
                    owned[t][it] = 1
                if t == 3 and it == 0:
                    done = True
                elif shards >= shard_cost:
                    done = True
            else:
                if t == 3 and (choice_hit or rnd() < 1.0 / nl):
                    done = True
            if done:
                break
        first_leg.append(fl if fl is not None else pulls)  # 조각 교환으로 먼저 얻은 경우 교환 시점
        spec.append(pulls)
    return first_leg, spec


def run_gacha_compare(v, n_main=20000, n_sens=8000, seed=20261112):
    rng_main = random.Random(seed)
    out = []
    global rng
    for st in GC_STRUCTURES:
        rng = rng_main
        fl, sp = _sim_structure(rng_main, v, st, n_main)
        sps = sorted(sp)
        ks = [100, 200, 300, 450, 600, 900, 1200]
        out.append({
            "id": st[0], "name": st[1], "epic_pity": st[2], "leg_hard": st[3], "soft": st[4], "choice": st[5], "shard_cost": st[6],
            "first": _stats(fl), "spec": _stats(sp),
            "within": [sum(1 for x in sps if x <= k) / len(sps) for k in ks], "ks": ks,
        })
    sens = []
    base = GC_STRUCTURES[1]
    for cost in (200, 300, 400, 600, 800, 1200):
        rng = random.Random(seed + cost)
        st = (base[0], base[1], base[2], None, None, None, cost)
        _, sp = _sim_structure(rng, v, st, n_sens)
        sens.append({"cost": cost, "spec": _stats(sp)})
    return {"seed": seed, "date": datetime.date.today().isoformat(), "n_main": n_main, "n_sens": n_sens, "rows": out, "sens": sens}


def build_gc_sheet(ws, P, gc):
    put(ws, "A1", "Gacha_Compare — 뽑기 천장 구조 비교 (난수 시뮬레이션, 정적 결과)", "title")
    if gc is None:
        put(ws, "A3", "(미생성) build_g3.py 실행 시 채워진다.", "note")
        return
    put(ws, "A2", f"시드 {gc['seed']}(고정), 생성일 {gc['date']}, 구조당 {gc['n_main']:,}회·조각 민감도 {gc['n_sens']:,}회 시행. 가격·확률·풀 크기는 Params/Gacha 시트 기준(생성 시점). 신규 유저(빈 컬렉션) 시작 가정.", "note")
    put(ws, "A3", "규칙: 영웅+ 천장=N회째 영웅 이상 보장 / 전설 하드=N회째 전설 보장 / 소프트=시작 회차부터 회당 전설 확률 가산(하드 천장 도달 시 보장) / 선택 천장=N회째 지정 전설 보장(누적 뽑기 기준) / 조각=중복 시 일반1·희귀3·영웅10·전설30조각, 비용만큼 모이면 지정 전설 교환.", "note")
    put(ws, "A4", "판정 기준(입력): 전설 첫 획득 P90 비용 ÷ 중견 월소득", "label")
    put(ws, "F4", 1.0, "in", PCT)
    put(ws, "A5", "판정 기준(입력): 지정 전설 P90 비용 ÷ 중견 월소득", "label")
    put(ws, "F5", 3.0, "in", PCT)
    put(ws, "G4", "[제안] Dashboard의 100%와 동일", "note")
    put(ws, "G5", "[제안] 지정 전설은 목표 콘텐츠라 300%까지 허용", "note")
    base_row = 9 + 1  # 현행(S1) 행 (첫 표 기준)

    def table(r0, title, key, thr_cell):
        section(ws, r0, title, 12)
        hdr_row(ws, r0 + 1, ["구조", "평균(회)", "P50", "P90", "P99", "최대", "평균 비용(Coin)", "현행 대비 평균 비용", "P90 비용(Coin)", "P90 비용÷중견 월소득", "판정", "상한(하드 캡)"])
        first = r0 + 2
        for i, row in enumerate(gc["rows"]):
            r = first + i
            st = row[key]
            put(ws, f"A{r}", f'{row["id"]} {row["name"]}', "label")
            put(ws, f"B{r}", st["mean"], "label", NUM1)
            put(ws, f"C{r}", st["p50"], "label", NUM)
            put(ws, f"D{r}", st["p90"], "label", NUM)
            put(ws, f"E{r}", st["p99"], "label", NUM)
            put(ws, f"F{r}", st["max"], "label", NUM)
            put(ws, f"G{r}", f"=B{r}*{P['e_g1']}", "f", NUM)
            put(ws, f"H{r}", f"=G{r}/$G${first+1}", "f", RATIO)
            put(ws, f"I{r}", f"=D{r}*{P['e_g1']}", "f", NUM)
            put(ws, f"J{r}", f"=I{r}/Gacha!$D$19", "f", PCT)
            put(ws, f"K{r}", f'=IF(J{r}<={thr_cell},"OK","검토")', "f")
            cap = []
            if row["leg_hard"]:
                cap.append(f"전설 {row['leg_hard']}회")
            if row["choice"] and key == "spec":
                cap.append(f"지정 {row['choice']}회")
            put(ws, f"L{r}", ", ".join(cap) if cap else "없음", "note")
        status_format(ws, f"K{first}:K{first+len(gc['rows'])-1}")
        return first + len(gc["rows"])

    e1 = table(7, "1. 전설 첫 획득까지 뽑기 수", "first", "$F$4")
    e2 = table(e1 + 2, "2. 지정 전설 1종 획득까지 뽑기 수", "spec", "$F$5")
    # 3. K회 안에 얻을 확률
    r0 = e2 + 2
    section(ws, r0, "3. 지정 전설을 K회 안에 얻을 확률", 9)
    ks = gc["rows"][0]["ks"]
    hdr_row(ws, r0 + 1, ["구조"] + [f"{k}회" for k in ks])
    for i, row in enumerate(gc["rows"]):
        r = r0 + 2 + i
        put(ws, f"A{r}", f'{row["id"]} {row["name"]}', "label")
        for j, pv in enumerate(row["within"]):
            put(ws, f"{CL(2+j)}{r}", pv, "label", PCT)
    e3 = r0 + 2 + len(gc["rows"])
    # 4. 조각 교환 민감도
    r0 = e3 + 2
    section(ws, r0, "4. 조각 교환 비용 민감도 (현행 천장 + 지정 전설 교환, 지정 전설 획득까지 뽑기 수)", 8)
    hdr_row(ws, r0 + 1, ["교환 비용(조각)", "평균(회)", "P50", "P90", "P99", "평균 비용(Coin)", "P90 비용(Coin)", "P90 비용÷중견 월소득"])
    for i, sr in enumerate(gc["sens"]):
        r = r0 + 2 + i
        st = sr["spec"]
        put(ws, f"A{r}", sr["cost"], "label", NUM)
        put(ws, f"B{r}", st["mean"], "label", NUM1)
        put(ws, f"C{r}", st["p50"], "label", NUM)
        put(ws, f"D{r}", st["p90"], "label", NUM)
        put(ws, f"E{r}", st["p99"], "label", NUM)
        put(ws, f"F{r}", f"=B{r}*{P['e_g1']}", "f", NUM)
        put(ws, f"G{r}", f"=D{r}*{P['e_g1']}", "f", NUM)
        put(ws, f"H{r}", f"=G{r}/Gacha!$D$19", "f", PCT)
    e4 = r0 + 2 + len(gc["sens"])
    put(ws, f"A{e4+1}", "※ 조각은 신규 유저가 뽑기 중 중복에서 모은 값만 계산했다(조각 구매·이벤트 지급 없음). 천장이 완화될수록 '평균 소각(비용)'이 줄어 Coin 싱크가 감소하므로 현행 대비 평균 비용 열을 함께 본다.", "note")
    widths(ws, {"A": 50, "B": 12, "C": 10, "D": 10, "E": 10, "F": 10, "G": 16, "H": 16, "I": 16, "J": 20, "K": 8, "L": 22})
    ws.freeze_panes = "B7"
    # 5. 등급 없는 균등 풀 (분석식)
    r5 = e4 + 4
    section(ws, r5, "5. 등급 없는 균등 풀(가구에 희귀도를 두지 않는 경우) — 분석식", 9)
    put(ws, f"A{r5+1}", "모든 가구가 같은 확률(1/풀 크기)이라 1~4절의 등급 천장(영웅+/전설)은 의미가 없다. 지정 가구 1종을 얻는 시도는 기하분포이며, 선택 천장 K회를 두면 K회가 상한이 된다.", "note")
    hdr_row(ws, r5 + 2, ["풀 크기 N", "지정 1종 평균(회)", "P50", "P90", "P99", "전체 수집 기대(회)", "평균 비용(Coin)", "P90 비용÷중견 월소득", "선택 천장 K=2N 평균(회)", "K=2N 평균 비용(Coin)"])
    for i, n in enumerate([30, 50, 68, 100, 150]):
        r = r5 + 3 + i
        put(ws, f"A{r}", n, "in", "0")
        put(ws, f"B{r}", f"=A{r}", "f", NUM1)
        put(ws, f"C{r}", f"=LN(0.5)/LN(1-1/A{r})", "f", NUM)
        put(ws, f"D{r}", f"=LN(0.1)/LN(1-1/A{r})", "f", NUM)
        put(ws, f"E{r}", f"=LN(0.01)/LN(1-1/A{r})", "f", NUM)
        put(ws, f"F{r}", f"=A{r}*(LN(A{r})+0.5772156649+1/(2*A{r}))", "f", NUM)
        put(ws, f"G{r}", f"=B{r}*{P['e_g1']}", "f", NUM)
        put(ws, f"H{r}", f"=D{r}*{P['e_g1']}/Gacha!$D$19", "f", PCT)
        put(ws, f"I{r}", f"=(1-(1-1/A{r})^(2*A{r}))*A{r}", "f", NUM1)
        put(ws, f"J{r}", f"=I{r}*{P['e_g1']}", "f", NUM)
    put(ws, f"A{r5+9}", "※ 전체 수집 기대 = N(ln N + 0.577 + 1/(2N))(쿠폰 수집가 근사). 조각 교환을 쓰면 중복에서 모인 조각으로 지정 가구를 교환할 수 있어 평균이 더 줄어든다(등급 풀과 같은 효과, 조각 가치는 별도 설계).", "note")


# ---------- 강화 파괴 완화 장치 비교 ----------
EM_STRUCTS = [
    # id, 이름, 설명, safe_to(이 단계 미만 파괴 없음), scroll_from, scroll_cost, refund, mode, pity_keep
    {"id": "E0", "name": "현행: 파괴 시 소멸·재구매·0단계", "desc": "기본(Enhance 시트와 동일)", "safe_to": 0, "scroll_from": None, "scroll_cost": 0, "refund": 0.0, "mode": "reset", "pity_keep": None},
    {"id": "E1", "name": "보호권(8단계부터 사용, 1,500 Coin/장)", "desc": "시도마다 보호권 소모 시 파괴가 '유지'로 바뀜(성공 여부와 무관하게 소모)", "safe_to": 0, "scroll_from": 8, "scroll_cost": 1500, "refund": 0.0, "mode": "reset", "pity_keep": None},
    {"id": "E2", "name": "파괴 시 투입 강화비 50% 환급", "desc": "소멸한 장비에 쓴 강화 비용(구매가 제외)의 50%를 돌려줌", "safe_to": 0, "scroll_from": None, "scroll_cost": 0, "refund": 0.5, "mode": "reset", "pity_keep": None},
    {"id": "E3", "name": "파괴 시 단계 절반 하락(소멸 없음)", "desc": "장비는 남고 단계만 ⌊n/2⌋로 하락, 재구매 불필요", "safe_to": 0, "scroll_from": None, "scroll_cost": 0, "refund": 0.0, "mode": "halve", "pity_keep": None},
    {"id": "E4", "name": "안전 구간 확대(8단계 미만 파괴 없음)", "desc": "현행 5단계 미만 → 8단계 미만, 파괴 확률은 '유지'로 이동", "safe_to": 8, "scroll_from": None, "scroll_cost": 0, "refund": 0.0, "mode": "reset", "pity_keep": None},
    {"id": "E5", "name": "강화 천장(연속 유지 8회 후 성공 확정)", "desc": "파괴 완화가 아니라 변동성 완화(비교용)", "safe_to": 0, "scroll_from": None, "scroll_cost": 0, "refund": 0.0, "mode": "reset", "pity_keep": 8},
    {"id": "E6", "name": "추천 후보: 안전 8미만 + 보호권(10단계부터) + 환급 30%", "desc": "세 장치의 약한 조합", "safe_to": 8, "scroll_from": 10, "scroll_cost": 1500, "refund": 0.3, "mode": "reset", "pity_keep": None},
]


def _sim_enh(rng, v, st, n_trials, levels):
    S_, K_, D_, C_ = v["s"], v["k"], v["d"], v["c"]
    start = v["start_price"]
    maxl = max(levels)
    safe_to, sc_from, sc_cost, refund, mode, pity_keep = st["safe_to"], st["scroll_from"], st["scroll_cost"], st["refund"], st["mode"], st["pity_keep"]
    rnd = rng.random
    acc = {L: {"cost": [], "destroy": [], "attempts": [], "scrolls": []} for L in levels}
    lvset = set(levels)
    for _ in range(n_trials):
        cost = start
        n = 0
        destroys = attempts = scrolls = streak = 0
        spent = 0.0
        done = set()
        while n < maxl:
            attempts += 1
            c = C_[n]
            cost += c
            spent += c
            s_ = S_[n]
            d_ = D_[n]
            if sc_from is not None and n >= sc_from and d_ > 0:
                cost += sc_cost
                scrolls += 1
                d_eff = 0.0
            else:
                d_eff = 0.0 if n < safe_to else d_
            r = rnd()
            if (pity_keep and streak >= pity_keep) or r < s_:
                n += 1
                streak = 0
                if n in lvset and n not in done:
                    done.add(n)
                    a_ = acc[n]
                    a_["cost"].append(cost)
                    a_["destroy"].append(destroys)
                    a_["attempts"].append(attempts)
                    a_["scrolls"].append(scrolls)
            elif r < s_ + (1.0 - s_ - d_eff):
                streak += 1
            else:
                destroys += 1
                streak = 0
                if refund:
                    cost -= refund * spent
                if mode == "reset":
                    cost += start
                    n = 0
                    spent = 0.0
                else:
                    n = n // 2
    out = {}
    for L in levels:
        a_ = acc[L]
        st_ = _stats(a_["cost"])
        m = len(a_["cost"])
        st_["destroy_prob"] = sum(1 for x in a_["destroy"] if x > 0) / m
        st_["destroy_mean"] = sum(a_["destroy"]) / m
        st_["scroll_mean"] = sum(a_["scrolls"]) / m
        st_["attempts_mean"] = sum(a_["attempts"]) / m
        out[L] = st_
    return out


def run_enh_mitigation(v, n_main=20000, n_sens=8000, seed=20261113):
    levels = [10, 12, 15]
    res = []
    for i, st in enumerate(EM_STRUCTS):
        r_ = random.Random(seed + i)
        res.append({"st": st, "stats": _sim_enh(r_, v, st, n_main, levels)})
    base = EM_STRUCTS[1]
    sens_cost = []
    for cost in (0, 500, 1000, 1500, 2500, 4000):
        st = dict(base, scroll_cost=cost)
        sens_cost.append({"cost": cost, "stats": _sim_enh(random.Random(seed + 100 + cost), v, st, n_sens, [12])[12]})
    sens_from = []
    for frm in (5, 8, 10, 12):
        st = dict(base, scroll_from=frm)
        sens_from.append({"from": frm, "stats": _sim_enh(random.Random(seed + 200 + frm), v, st, n_sens, [12])[12]})
    return {"seed": seed, "date": datetime.date.today().isoformat(), "n_main": n_main, "n_sens": n_sens, "levels": levels, "rows": res, "sens_cost": sens_cost, "sens_from": sens_from}


def build_em_sheet(ws, P, em):
    put(ws, "A1", "Enhance_Mitigation — 강화 파괴 완화 장치 비교 (난수 시뮬레이션, 정적 결과)", "title")
    if em is None:
        put(ws, "A3", "(미생성) build_g3.py 실행 시 채워진다.", "note")
        return
    put(ws, "A2", f"시드 {em['seed']}(고정, 구조별 오프셋), 생성일 {em['date']}, 구조당 {em['n_main']:,}회·민감도 {em['n_sens']:,}회 시행. 강화 확률·비용·장비 구매가는 Enhance/Params 시트 기준(생성 시점). 비용에는 장비 구매·재구매·보호권·환급이 포함된다.", "note")
    put(ws, "A3", "모델: 단계마다 비용을 낸 뒤 성공/유지/파괴 판정. 파괴 시 기본은 장비 재구매+0단계 재시작(현행). 보호권=파괴 확률을 유지로 전환(소모형), 안전 구간=해당 단계 미만 파괴 없음, 환급=파괴 시 투입 강화비의 일부 반환, 단계 하락=소멸 대신 ⌊n/2⌋.", "note")
    put(ws, "A4", "판정 기준(입력): P90 ÷ 평균 상한", "label")
    put(ws, "F4", 2.0, "in", NUM2)
    put(ws, "A5", "판정 기준(입력): 목표 단계 장비 소멸 확률 상한", "label")
    put(ws, "F5", 0.30, "in", PCT)
    put(ws, "G4", "[제안] G3 기존 기준(90% 분위 ≤ 평균의 2배)", "note")
    put(ws, "G5", "[제안] 장비를 한 번 이상 잃는 유저 비율", "note")
    # 구조 정의표
    section(ws, 7, "구조 정의", 8)
    hdr_row(ws, 8, ["구조", "설명", "안전 구간(<)", "보호권 시작 단계", "보호권 가격(Coin)", "환급 비율", "파괴 시", "강화 천장(연속 유지)"])
    for i, row in enumerate(em["rows"]):
        st = row["st"]
        r = 9 + i
        put(ws, f"A{r}", f'{st["id"]} {st["name"]}', "label")
        put(ws, f"B{r}", st["desc"], "note")
        put(ws, f"C{r}", st["safe_to"] if st["safe_to"] else "-", "label")
        put(ws, f"D{r}", st["scroll_from"] if st["scroll_from"] is not None else "-", "label")
        put(ws, f"E{r}", st["scroll_cost"] if st["scroll_from"] is not None else "-", "label", NUM)
        put(ws, f"F{r}", st["refund"] if st["refund"] else "-", "label", PCT)
        put(ws, f"G{r}", "소멸·재구매·0단계" if st["mode"] == "reset" else "단계 ⌊n/2⌋ 하락", "label")
        put(ws, f"H{r}", st["pity_keep"] if st["pity_keep"] else "-", "label")
    r0 = 9 + len(em["rows"]) + 2
    for L in em["levels"]:
        section(ws, r0, f"+{L} 단계 도달 총비용 (장비 구매 포함)", 13)
        hdr_row(ws, r0 + 1, ["구조", "평균", "P50", "P90", "P99", "P90÷평균", "장비 소멸 확률(≥1회)", "평균 파괴 횟수", "평균 보호권 수", "현행 대비 평균 비용", "P50 소요 일수", "P90 소요 일수", "판정"])
        first = r0 + 2
        for i, row in enumerate(em["rows"]):
            r = first + i
            st = row["stats"][L]
            put(ws, f"A{r}", f'{row["st"]["id"]} {row["st"]["name"]}', "label")
            put(ws, f"B{r}", st["mean"], "label", NUM)
            put(ws, f"C{r}", st["p50"], "label", NUM)
            put(ws, f"D{r}", st["p90"], "label", NUM)
            put(ws, f"E{r}", st["p99"], "label", NUM)
            put(ws, f"F{r}", f"=D{r}/B{r}", "f", NUM2)
            put(ws, f"G{r}", st["destroy_prob"], "label", PCT)
            put(ws, f"H{r}", st["destroy_mean"], "label", NUM2)
            put(ws, f"I{r}", st["scroll_mean"], "label", NUM1)
            put(ws, f"J{r}", f"=B{r}/$B${first}", "f", RATIO)
            put(ws, f"K{r}", f"=C{r}/{P['enh_budget']}", "f", NUM1)
            put(ws, f"L{r}", f"=D{r}/{P['enh_budget']}", "f", NUM1)
            put(ws, f"M{r}", f'=IF(AND(F{r}<=$F$4,G{r}<=$F$5),"OK","검토")', "f")
        status_format(ws, f"M{first}:M{first+len(em['rows'])-1}")
        r0 = first + len(em["rows"]) + 1
    # 민감도
    section(ws, r0, "보호권 가격 민감도 (+12 도달, 8단계부터 사용)", 8)
    hdr_row(ws, r0 + 1, ["보호권 가격(Coin)", "평균", "P50", "P90", "P90÷평균", "장비 소멸 확률", "평균 보호권 수", "현행(E0) 대비 평균 비용"])
    e0_mean_row = None
    base12 = em["rows"][0]["stats"][12]["mean"]
    for i, sc in enumerate(em["sens_cost"]):
        r = r0 + 2 + i
        st = sc["stats"]
        put(ws, f"A{r}", sc["cost"], "label", NUM)
        put(ws, f"B{r}", st["mean"], "label", NUM)
        put(ws, f"C{r}", st["p50"], "label", NUM)
        put(ws, f"D{r}", st["p90"], "label", NUM)
        put(ws, f"E{r}", f"=D{r}/B{r}", "f", NUM2)
        put(ws, f"F{r}", st["destroy_prob"], "label", PCT)
        put(ws, f"G{r}", st["scroll_mean"], "label", NUM1)
        put(ws, f"H{r}", f"=B{r}/{base12}", "f", RATIO)
    r1 = r0 + 2 + len(em["sens_cost"]) + 1
    section(ws, r1, "보호권 사용 시작 단계 민감도 (+12 도달, 가격 1,500 Coin)", 8)
    hdr_row(ws, r1 + 1, ["사용 시작 단계", "평균", "P50", "P90", "P90÷평균", "장비 소멸 확률", "평균 보호권 수", "현행(E0) 대비 평균 비용"])
    for i, sf in enumerate(em["sens_from"]):
        r = r1 + 2 + i
        st = sf["stats"]
        put(ws, f"A{r}", sf["from"], "label", "0")
        put(ws, f"B{r}", st["mean"], "label", NUM)
        put(ws, f"C{r}", st["p50"], "label", NUM)
        put(ws, f"D{r}", st["p90"], "label", NUM)
        put(ws, f"E{r}", f"=D{r}/B{r}", "f", NUM2)
        put(ws, f"F{r}", st["destroy_prob"], "label", PCT)
        put(ws, f"G{r}", st["scroll_mean"], "label", NUM1)
        put(ws, f"H{r}", f"=B{r}/{base12}", "f", RATIO)
    put(ws, f"A{r1+2+len(em['sens_from'])+1}", "※ 보호권 가격은 Coin 싱크이므로 '현행 대비 평균 비용'이 낮아지면 강화 소각이 줄어든다(평균 비용이 곧 유저가 쓰는 Coin). 장비 소멸 확률은 유저 체감(손실감)을, P90÷평균은 운이 나쁠 때의 부담을 나타낸다.", "note")
    widths(ws, {"A": 52, "B": 30, "C": 12, "D": 12, "E": 12, "F": 14, "G": 20, "H": 14, "I": 14, "J": 18, "K": 14, "L": 14, "M": 8})
    ws.freeze_panes = "B7"


def build_live_sheet(ws, P):
    put(ws, "A1", "Live_Sim — 시트 안 RAND() 체험 시뮬레이션 (재계산할 때마다 값이 바뀐다)", "title")
    put(ws, "A2", "F9(재계산)로 다시 굴린다. 이 시트의 값은 다른 시트가 참조하지 않는다. 대량 분포는 MonteCarlo 시트(정적, 시드 고정)를 본다.", "note")
    # ---- 강화 한 번의 여정 ----
    put(ws, "A4", "목표 단계(+)", "label")
    put(ws, "B4", f"={P['target_lv']}", "link", "0")
    put(ws, "A5", "도달까지 시도 수", "bold")
    put(ws, "A6", "총비용(장비 구매 포함)", "bold")
    put(ws, "A7", "파괴 횟수", "bold")
    hdr_row(ws, 8, ["#", "현재 단계", "성공 확률", "유지 확률", "파괴 확률", "난수", "결과", "다음 단계", "이번 비용", "누적 비용", "누적 파괴"])
    N = 150
    first, last = 9, 8 + N
    for i in range(N):
        r = first + i
        put(ws, f"A{r}", i + 1, "label", "0")
        put(ws, f"B{r}", 0 if i == 0 else f"=H{r-1}", "in" if i == 0 else "f", "0")
        put(ws, f"C{r}", f"=IF(B{r}>=$B$4,0,INDEX(Enhance!$E$6:$E$25,MIN(B{r}+1,20)))", "f", PCT)
        put(ws, f"D{r}", f"=IF(B{r}>=$B$4,0,INDEX(Enhance!$F$6:$F$25,MIN(B{r}+1,20)))", "f", PCT)
        put(ws, f"E{r}", f"=IF(B{r}>=$B$4,0,INDEX(Enhance!$G$6:$G$25,MIN(B{r}+1,20)))", "f", PCT)
        put(ws, f"F{r}", "=RAND()", "f", "0.000")
        put(ws, f"G{r}", f'=IF(B{r}>=$B$4,"도달",IF(F{r}<C{r},"성공",IF(F{r}<C{r}+D{r},"유지","파괴")))', "f")
        put(ws, f"H{r}", f'=IF(G{r}="성공",B{r}+1,IF(G{r}="파괴",0,B{r}))', "f", "0")
        put(ws, f"I{r}", f'=IF(B{r}>=$B$4,0,INDEX(Enhance!$K$6:$K$25,MIN(B{r}+1,20))+IF(G{r}="파괴",{P["start_price"]},0))', "f", NUM)
        prev = f"J{r-1}+" if i > 0 else f"{P['start_price']}+"
        put(ws, f"J{r}", f"={prev}I{r}", "f", NUM)
        put(ws, f"K{r}", (f'=K{r-1}+' if i > 0 else "=") + f'IF(G{r}="파괴",1,0)', "f", "0")
    put(ws, "B5", f'=IFERROR(MATCH("도달",G{first}:G{last},0)-1,"미도달({N}회 초과)")', "f", "0")
    put(ws, "B6", f'=IF(ISNUMBER(B5),INDEX(J{first}:J{last},B5),MAX(J{first}:J{last}))', "f", NUM)
    put(ws, "B7", f'=IF(ISNUMBER(B5),INDEX(K{first}:K{last},B5),MAX(K{first}:K{last}))', "f", "0")
    put(ws, "C5", "← 분석 기대 시도 수는 MonteCarlo의 '평균 시도 수'", "note")
    put(ws, "C6", f"← 분석 기대 비용 {'(Enhance 시트 목표 단계 요약)'}", "note")
    # ---- 가구 뽑기 300회 ----
    put(ws, "N4", "뽑기 횟수", "label")
    put(ws, "O4", 300, "label", "0")
    hdr_row(ws, 8, ["#", "천장 카운터(이전)", "난수", "천장 발동", "결과", "다음 카운터"], start_col=14)
    G = 300
    g_first, g_last = 9, 8 + G
    for i in range(G):
        r = g_first + i
        put(ws, f"N{r}", i + 1, "label", "0")
        put(ws, f"O{r}", 0 if i == 0 else f"=S{r-1}", "in" if i == 0 else "f", "0")
        put(ws, f"P{r}", "=RAND()", "f", "0.000")
        put(ws, f"Q{r}", f'=IF(O{r}>={P["pity"]}-1,"Y","N")', "f")
        put(ws, f"R{r}", f'=IF(Q{r}="Y",IF(P{r}<{P["g_legend"]}/({P["g_epic"]}+{P["g_legend"]}),"전설","영웅"),IF(P{r}<{P["g_common"]},"일반",IF(P{r}<{P["g_common"]}+{P["g_rare"]},"희귀",IF(P{r}<{P["g_common"]}+{P["g_rare"]}+{P["g_epic"]},"영웅","전설"))))', "f")
        put(ws, f"S{r}", f'=IF(OR(R{r}="영웅",R{r}="전설"),0,O{r}+1)', "f", "0")
    hdr_row(ws, 4, ["티어", "횟수", "비율", "공개 확률"], start_col=17)
    for i, (nm, key) in enumerate((("일반", "g_common"), ("희귀", "g_rare"), ("영웅", "g_epic"), ("전설", "g_legend"))):
        r = 5 + i
        put(ws, f"Q{r}", nm, "label")
        put(ws, f"R{r}", f'=COUNTIF($R${g_first}:$R${g_last},Q{r})', "f", "0")
        put(ws, f"S{r}", f"=R{r}/$O$4", "f", PCT)
        put(ws, f"T{r}", f"={P[key]}", "link", PCT)
    put(ws, "N5", "전설 첫 획득", "bold")
    put(ws, "O5", f'=IFERROR(MATCH("전설",R{g_first}:R{g_last},0),"미획득")', "f", "0")
    put(ws, "N6", "천장 발동 횟수", "bold")
    put(ws, "O6", f'=COUNTIF(Q{g_first}:Q{g_last},"Y")', "f", "0")
    put(ws, "N7", "300회 비용(Coin)", "bold")
    put(ws, "O7", f"=O4*{P['e_g1']}", "f", NUM)
    widths(ws, {"A": 22, "B": 12, "C": 12, "D": 12, "E": 12, "F": 10, "G": 8, "H": 10, "I": 12, "J": 14, "K": 10, "L": 3, "M": 3, "N": 16, "O": 14, "P": 10, "Q": 12, "R": 10, "S": 12, "T": 12})
    ws.freeze_panes = "A9"


# ---------- 빌드 ----------
def build(scenario_index=1, mc=None, gc=None, em=None):
    wb = Workbook()
    ws_leg = wb.active
    ws_leg.title = "Legend"
    names = ["Params", "Scenarios", "Items", "JobIncome", "PriceSim", "Enhance", "Gacha", "Housing_Sinks", "FlowBalance", "Weapons_DPS", "Effect_Packs", "MonteCarlo", "Gacha_Compare", "Enhance_Mitigation", "Live_Sim", "Dashboard"]
    S = {n: wb.create_sheet(n) for n in names}
    S["Legend"] = ws_leg
    P = {}  # 파라미터 키 -> 절대 참조 문자열

    # ===== Scenarios (선택값 먼저 정의: 다른 시트가 참조) =====
    ws = S["Scenarios"]
    put(ws, "A1", "Scenarios — 시나리오 선택과 민감도 비교", "title")
    put(ws, "A2", "선택 시나리오 번호", "bold")
    put(ws, "B2", scenario_index, "in", key=True)
    put(ws, "C2", "← 1~7 중 선택. 선택한 배율이 Params의 '시나리오 적용값'에 반영되어 모든 시트가 다시 계산된다.", "note")
    dv = DataValidation(type="list", formula1='"1,2,3,4,5,6,7"', allow_blank=False)
    ws.add_data_validation(dv)
    dv.add("B2")
    hdr_row(ws, 4, ["시나리오", "CCU 배율", "농부 비중 배율", "alpha 가산", "강화 성공률 가감(%p)", "뽑기 가격 배율"])
    for i, (nm, a, b, c, d, e) in enumerate(SCENARIOS):
        r = 5 + i
        put(ws, f"A{r}", nm, "label")
        for col, v, fmt in (("B", a, '0.0"x"'), ("C", b, '0.0"x"'), ("D", c, "0.00"), ("E", d, '0.00'), ("F", e, '0.0"x"')):
            put(ws, f"{col}{r}", v, "in", fmt)
    nS = len(SCENARIOS)
    last = 4 + nS
    put(ws, "A13", "선택된 배율", "bold")
    for col in "BCDEF":
        put(ws, f"{col}13", f"=INDEX({col}5:{col}{last},$B$2)", "f", '0.00')
    put(ws, "A14", "선택된 시나리오 이름", "bold")
    put(ws, "B14", f"=INDEX(A5:A{last},$B$2)", "f")
    P["sel_ccu"] = "Scenarios!$B$13"
    P["sel_farm"] = "Scenarios!$C$13"
    P["sel_alpha"] = "Scenarios!$D$13"
    P["sel_enh"] = "Scenarios!$E$13"
    P["sel_gp"] = "Scenarios!$F$13"
    widths(ws, {"A": 34, "B": 14, "C": 16, "D": 14, "E": 20, "F": 16, "G": 14, "H": 14, "I": 14, "J": 16, "K": 16})

    # ===== Params =====
    ws = S["Params"]
    put(ws, "A1", "Params — 전역 가정 (입력은 파란 글씨, 노란 칸은 핵심 가정)", "title")
    hdr_row(ws, 3, ["항목", "값", "단위/설명", "출처·비고"])
    row = [4]

    def sec(text):
        section(ws, row[0], text)
        row[0] += 1

    def prm(key, label, val, unit="", note="[제안]", fmt=None, key_assump=False):
        r = row[0]
        put(ws, f"A{r}", label, "label")
        put(ws, f"B{r}", val, "in", fmt, key=key_assump)
        put(ws, f"C{r}", unit, "note")
        put(ws, f"D{r}", note, "note")
        P[key] = f"Params!$B${r}"
        row[0] += 1

    sec("인구")
    prm("ccu", "목표 동시접속 CCU", 100, "명", "G0에서 확정 전까지 임시값", NUM, True)
    prm("dau_ratio", "DAU / CCU 비율", 3.0, "배", "[제안] 실측으로 교체", NUM1)
    prm("mix_new", "유저 비율 — 신규", 0.40, "비율", "[제안]", PCT)
    prm("mix_mid", "유저 비율 — 중견", 0.40, "비율", "[제안]", PCT)
    prm("mix_high", "유저 비율 — 고레벨", 0.20, "비율", "[제안] 세 비율의 합 = 100%", PCT)
    prm("h_new", "1일 플레이 시간 — 신규", 1.5, "시간", "[제안]", NUM1)
    prm("h_mid", "1일 플레이 시간 — 중견", 2.5, "시간", "[제안]", NUM1)
    prm("h_high", "1일 플레이 시간 — 고레벨", 3.0, "시간", "[제안]", NUM1)
    prm("growth", "직업 생산성 일일 증가율", 0.004, "비율/일", "레벨업·장비 성장으로 시간당 생산량이 늘어나는 정도 [제안]", '0.0%')
    prm("sell_ratio", "생산물 중 NPC 판매 비율", 0.75, "비율", "나머지는 유저 거래·납품·자가 소비 [제안]", PCT)
    sec("시세 (명세 7.2장)")
    prm("ema_days", "EMA 기간", 7, "일", "명세 제안 1~7일", NUM)
    prm("alpha", "alpha(수요 민감도)", 0.5, "지수", "[제안] 시나리오로 가산", NUM2, True)
    prm("q_min", "Q 하한(분모 보호)", 1, "수량", "0 나누기 방지", NUM)
    prm("max_chg", "하루 가격 변동폭 상한", 0.10, "비율", "명세 제안 ±10%", PCT, True)
    prm("floor_mult", "가격 하한 배수", 0.40, "배", "P_floor = P_base × 값 (config 예시와 동일)", NUM2)
    prm("cap_mult", "가격 상한 배수", 2.0, "배", "P_cap = P_base × 값 [제안]", NUM2)
    sec("수수료·발행")
    prm("fee", "유저 간 거래 수수료율", 0.03, "비율", "명세 8.2장 제안 2~5%", PCT)
    prm("list_fee", "게시판 등록비", 50, "Coin", "[제안]", NUM)
    prm("p2p", "1인당 일 유저 간 거래액(이동)", 300, "Coin/DAU", "이동은 소각 아님 — 수수료만 소각 [제안]", NUM)
    prm("att_reward", "출석 보상(1일 최대)", 400, "Coin/인", "30분×4회 [제안]", NUM)
    prm("att_claim", "출석 보상 수령률", 0.60, "비율", "[제안]", PCT)
    prm("quest", "퀘스트·업적·이벤트 발행", 300, "Coin/DAU/일", "[제안]", NUM)
    prm("m0", "초기 보유 Coin", 500, "Coin/DAU", "[제안]", NUM)
    prm("sink_start", "소각 성숙도 시작 비율", 0.50, "비율", "초기에는 소비가 적다 [제안]", PCT)
    prm("sink_ramp", "소각 성숙까지 일수", 30, "일", "[제안]", NUM)
    sec("강화")
    prm("start_price", "장비 구매가(강화 시작 장비)", 1200, "Coin", "철 한손검 상점가 예시", NUM)
    prm("enh_base", "강화 1회 Coin 비용(0→1)", 230, "Coin", "[제안]", NUM)
    prm("enh_growth", "단계당 비용 증가 배율", 1.3, "배", "[제안]", NUM2)
    prm("stone_val", "강화석 1개의 Coin 환산가", 150, "Coin", "광부 수익 기반으로 보정 [제안]", NUM)
    prm("enh_k", "강화 단계당 피해 증가 k", 0.06, "비율", "combat-spec 11장 산식", PCT)
    prm("base_dmg", "예시 무기 base_damage", 6.0, "피해", "한손검 템플릿", NUM1)
    prm("enh_tier", "예시 무기 티어", 3, "T", "0~5", NUM)
    prm("target_lv", "목표 강화 단계(보스 진입)", 10, "+단계", "[제안]", NUM, True)
    prm("design_days", "설계 목표 일수", 14, "일", "G0에서 확정", NUM, True)
    prm("enh_share", "강화에 쓰는 소득 비중", 0.50, "비율", "나머지는 소비·가구·상점 [제안]", PCT)
    prm("shop_share", "상점 구매(장비·도구·씨앗)에 쓰는 소득 비중", 0.30, "비율", "Housing_Sinks 소각 계산용 [제안]", PCT)
    sec("가구 뽑기 (명세 9.3장)")
    prm("g_price", "1회 가격", 600, "Coin", "[제안]", NUM)
    prm("g_price10", "10회 가격", 5400, "Coin", "10% 할인 [제안]", NUM)
    prm("g_common", "확률 — 일반", 0.65, "비율", "예시(확정 아님)", PCT)
    prm("g_rare", "확률 — 희귀", 0.25, "비율", "예시", PCT)
    prm("g_epic", "확률 — 영웅", 0.09, "비율", "예시", PCT)
    prm("g_legend", "확률 — 전설", 0.01, "비율", "예시 (합계 100% 검증은 Gacha 시트)", PCT)
    prm("n_common", "풀 크기 — 일반", 30, "종", "[제안]", NUM)
    prm("n_rare", "풀 크기 — 희귀", 20, "종", "[제안]", NUM)
    prm("n_epic", "풀 크기 — 영웅", 12, "종", "[제안]", NUM)
    prm("n_legend", "풀 크기 — 전설", 6, "종", "[제안]", NUM)
    prm("pity", "천장(영웅 이상 보장)", 50, "회", "명세 제안", NUM)
    prm("pulls_dau", "1인당 일 뽑기 횟수(참여자 기준)", 0.8, "회", "소각 계산용 [제안]", NUM2)
    sec("밸런스 판정 기준 (Dashboard)")
    prm("t_dps", "목표 지속 DPS(일반)", 9.7, "피해/초", "weapon-archetypes-spec 3장", NUM2)
    prm("t_dps_aoe", "목표 지속 DPS(광역 -10%)", 8.7, "피해/초", "동일", NUM2)
    prm("dps_tol", "아키타입 DPS 허용 오차", 0.05, "비율", "[제안]", PCT)
    prm("dev_min", "직업 간 순수익 비율 하한", 0.8, "배", "weapon/job 설계 기준", NUM2)
    prm("dev_max", "직업 간 순수익 비율 상한", 1.25, "배", "동일", NUM2)
    prm("floor_max", "가격 하한 고착 허용 일수(90일 중)", 10, "일", "[제안]", NUM)
    prm("days_tol", "강화 도달 일수 허용 오차", 0.30, "비율", "[제안]", PCT)
    prm("legend_max", "전설 기대 비용 / 중견 월소득 상한", 0.50, "비율", "[제안]", PCT)
    prm("money_max", "1인당 보유 Coin / 일 발행 상한", 30, "배", "[제안]", NUM)
    prm("effect_cap", "특수 효과 기대 DPS 비중 상한", 0.15, "비율", "special-effects-spec 6장", PCT)

    # 시나리오 적용값 + 직업 비중
    row[0] += 1
    sec("시나리오 적용값 (수식 — 직접 수정하지 말 것)")
    r = row[0]

    def eff(key, label, formula, fmt):
        rr = row[0]
        put(ws, f"A{rr}", label, "label")
        put(ws, f"B{rr}", formula, "f", fmt)
        put(ws, f"C{rr}", "수식", "note")
        P[key] = f"Params!$B${rr}"
        row[0] += 1

    eff("e_ccu", "적용 CCU", f"={P['ccu']}*{P['sel_ccu']}", NUM)
    eff("e_dau", "적용 DAU", f"={P['e_ccu']}*{P['dau_ratio']}", NUM)
    eff("e_alpha", "적용 alpha", f"={P['alpha']}+{P['sel_alpha']}", NUM2)
    eff("e_enh", "적용 강화 성공률 가감", f"={P['sel_enh']}", NUM2)
    eff("e_g1", "적용 뽑기 1회 가격", f"={P['g_price']}*{P['sel_gp']}", NUM)
    eff("e_g10", "적용 뽑기 10회 가격", f"={P['g_price10']}*{P['sel_gp']}", NUM)
    eff("mix_sum", "유저 비율 합계(검증)", f"={P['mix_new']}+{P['mix_mid']}+{P['mix_high']}", PCT)
    row[0] += 1
    section(ws, row[0], "직업별 비중 (기본 입력 → 시나리오 배율 → 정규화)", 5)
    row[0] += 1
    jr = row[0]
    hdr_row(ws, jr, ["직업", "기본 비중", "시나리오 배율", "가중 값", "유효 비중"])
    for i, j in enumerate(JOBS):
        rr = jr + 1 + i
        put(ws, f"A{rr}", j, "label")
        put(ws, f"B{rr}", 0.25, "in", PCT)
        put(ws, f"C{rr}", f"={P['sel_farm']}" if j == "농부" else 1, "f" if j == "농부" else "in", '0.0"x"')
        put(ws, f"D{rr}", f"=B{rr}*C{rr}", "f", '0.000')
        put(ws, f"E{rr}", f"=D{rr}/SUM($D${jr+1}:$D${jr+4})", "f", PCT)
    JSHARE_NAMES = f"Params!$A${jr+1}:$A${jr+4}"
    JSHARE_VALS = f"Params!$E${jr+1}:$E${jr+4}"
    widths(ws, {"A": 40, "B": 14, "C": 18, "D": 46, "E": 14})
    ws.freeze_panes = "A4"

    # ===== Weapons_DPS =====
    ws = S["Weapons_DPS"]
    archs, t_dps, t_aoe = load_archetypes()
    put(ws, "A1", "Weapons_DPS — 아키타입 지속 DPS 균형 + 티어 배율 + 특수 효과 예산", "title")
    put(ws, "A2", "DPS = base_damage × Σfactor ÷ (Σcooldown ÷ 20)  (좌공격 콤보 1사이클, 티어 배율·강화 제외). 입력은 data/weapon_catalog/archetypes.json 값.", "note")
    heads = ["아키타입", "한글명", "광역(1/0)", "base_damage"] + [f"factor{i}" for i in range(1, 6)] + [f"cd{i}(tick)" for i in range(1, 6)] + ["Σfactor", "Σcooldown", "DPS", "목표 DPS", "비율", "판정"]
    hdr_row(ws, 4, heads)
    for i, (aid, nm, aoe, base, hits) in enumerate(archs):
        r = 5 + i
        put(ws, f"A{r}", aid, "label")
        put(ws, f"B{r}", nm, "label")
        put(ws, f"C{r}", aoe, "in", "0")
        put(ws, f"D{r}", base, "in", NUM2)
        for k in range(5):
            f_ = hits[k][0] if k < len(hits) else None
            c_ = hits[k][1] if k < len(hits) else None
            put(ws, f"{CL(5 + k)}{r}", f_, "in", "0.0")
            put(ws, f"{CL(10 + k)}{r}", c_, "in", "0")
        put(ws, f"O{r}", f"=SUM(E{r}:I{r})", "f", NUM2)
        put(ws, f"P{r}", f"=SUM(J{r}:N{r})", "f", NUM)
        put(ws, f"Q{r}", f"=D{r}*O{r}/(P{r}/20)", "f", NUM2)
        put(ws, f"R{r}", f"=IF(C{r}=1,{P['t_dps_aoe']},{P['t_dps']})", "f", NUM2)
        put(ws, f"S{r}", f"=Q{r}/R{r}", "f", RATIO)
        put(ws, f"T{r}", f'=IF(ABS(S{r}-1)<={P["dps_tol"]},"OK","검토")', "f")
    A_FIRST, A_LAST = 5, 4 + len(archs)
    status_format(ws, f"T{A_FIRST}:T{A_LAST}")
    put(ws, f"A{A_LAST+1}", "비율 최대/최소", "bold")
    put(ws, f"S{A_LAST+1}", f"=MAX(S{A_FIRST}:S{A_LAST})", "f", RATIO)
    put(ws, f"S{A_LAST+2}", f"=MIN(S{A_FIRST}:S{A_LAST})", "f", RATIO)
    P["dps_max"] = f"Weapons_DPS!$S${A_LAST+1}"
    P["dps_min"] = f"Weapons_DPS!$S${A_LAST+2}"

    tr = A_LAST + 5
    section(ws, tr - 1, "티어 배율·특수 효과 슬롯 (special-effects-spec.md 4장)", 8)
    hdr_row(ws, tr, ["티어", "등급", "티어 배율", "해금 효과 수(최대 강화 시)", "효과 DPS 비중(Effect_Packs 최대)", "효과 DPS 비중 합", "상한 대비", "판정"])
    tiers = [(0, "시작", 0.7, 0, None), (1, "일반", 1.0, 0, None), (2, "고급", 1.35, 0, None), (3, "희귀", 1.8, 1, "Effect_Packs!$B$50"), (4, "영웅", 2.4, 2, "Effect_Packs!$C$50"), (5, "전설", 3.2, 4, "Effect_Packs!$D$50")]
    for i, (t, nm, m, n, ref) in enumerate(tiers):
        r = tr + 1 + i
        put(ws, f"A{r}", t, "label", "0")
        put(ws, f"B{r}", nm, "label")
        put(ws, f"C{r}", m, "in", NUM2)
        put(ws, f"D{r}", n, "in", "0")
        if ref:
            put(ws, f"E{r}", f"={ref}", "link", PCT)
        else:
            put(ws, f"E{r}", 0, "in", PCT)
        put(ws, f"F{r}", f"=E{r}", "f", PCT)
        put(ws, f"G{r}", f"=F{r}/{P['effect_cap']}", "f", PCT)
        put(ws, f"H{r}", f'=IF(F{r}<={P["effect_cap"]},"OK","검토")', "f")
    T_FIRST, T_LAST = tr + 1, tr + len(tiers)
    status_format(ws, f"H{T_FIRST}:H{T_LAST}")
    P["tier_mult_rng"] = f"Weapons_DPS!$C${T_FIRST}:$C${T_LAST}"
    P["effect_max"] = f"MAX(Weapons_DPS!$F${T_FIRST}:$F${T_LAST})"
    put(ws, f"A{T_LAST+2}", "※ 티어별 효과 DPS 비중은 Effect_Packs 시트에서 팩·속도 클래스별로 계산한 최댓값이다(전설 = 효과 3종 + 각성 1).", "note")
    widths(ws, {"A": 18, "B": 12, "C": 12, "D": 13, **{CL(k): 9 for k in range(5, 15)}, "O": 10, "P": 11, "Q": 9, "R": 10, "S": 9, "T": 8})
    ws.freeze_panes = "C5"

    # ===== Effect_Packs =====
    ws = S["Effect_Packs"]
    put(ws, "A1", "Effect_Packs — 테마 효과 팩 6종의 기대 DPS 비중 (special-effects-spec.md 5·6장)", "title")
    put(ws, "A2", "비중 = 초당 발동 수 × 발동당 피해(타격 환산) × 유효 대상 수 ÷ 초당 타격 수.  타격 환산 1.0 = 평균 1회 타격 피해.  유틸(상태이상·회복)은 피해 환산 0이며 연출·상태 효과로 가치를 낸다.", "note")
    put(ws, "A4", "치명타 비율(점프 크리티컬)", "label")
    put(ws, "B4", 0.10, "in", PCT)
    put(ws, "A5", "광역 비율(그룹 전투 비중)", "label")
    put(ws, "B5", 0.40, "in", PCT)
    put(ws, "C5", "다수 대상 효과에서 평균 추가 대상 수 = (대상 수−1) × 이 비율", "note")
    put(ws, "A6", "티어 배율 T3", "label")
    put(ws, "B6", 1.00, "in", NUM2)
    put(ws, "A7", "티어 배율 T4", "label")
    put(ws, "B7", 1.15, "in", NUM2)
    put(ws, "A8", "티어 배율 T5", "label")
    put(ws, "B8", 1.30, "in", NUM2)
    hdr_row(ws, 10, ["속도 클래스", "기준 아키타입", "Weapons_DPS 행", "콤보 타격 수", "콤보 사이클(초)", "초당 타격 수"])
    cls = [("느림", "greatsword"), ("중간", "one_hand_sword"), ("빠름", "dagger")]
    arch_ids = [a_[0] for a_ in archs]
    for k, (cn, aid) in enumerate(cls):
        r = 11 + k
        wr = 5 + arch_ids.index(aid)
        put(ws, f"A{r}", cn, "label")
        put(ws, f"B{r}", aid, "label")
        put(ws, f"C{r}", wr, "in", "0")
        put(ws, f"D{r}", f"=COUNT(Weapons_DPS!E{wr}:I{wr})", "link", "0")
        put(ws, f"E{r}", f"=Weapons_DPS!P{wr}/20", "link", NUM2)
        put(ws, f"F{r}", f"=D{r}/E{r}", "f", NUM2)
    eh = ["팩", "팩 이름", "슬롯(1~3·4=각성)", "효과", "발동 유형", "파라미터(확률/N/주기/사이클수)", "내부 쿨다운(초)", "발동당 피해(타격 환산)", "대상 수", "분류", "설명",
          "발동/초 느림", "발동/초 중간", "발동/초 빠름", "비중 느림", "비중 중간", "비중 빠름", "비중 최대", "해금 T3(+)", "해금 T4(+)", "해금 T5(+)"]
    hdr_row(ws, 16, eh)
    ws.row_dimensions[16].height = 44
    # (key, 이름, [(slot, 효과, 유형, 파라미터, ICD, 피해, 대상, 분류, 설명, (T3,T4,T5 해금))])
    PACKS = [
        ("fire", "불꽃", [
            (1, "화염 화상", "chance", 0.10, 3.0, 0.35, 1, "피해", "3초 지속 피해(화상)", (10, 10, 5)),
            (2, "마무리 폭발", "finisher", 3, 0, 0.09, 3, "피해", "콤보 마무리 후 3사이클마다 범위 폭발", (None, 15, 10)),
            (3, "불길 전이", "chance", 0.05, 5.0, 0.28, 3, "피해", "화상이 주변 대상에게 전이", (None, None, 15)),
            (4, "화염 폭풍", "periodic", 8, 0, 0.06, 4, "피해", "8초마다 주변 지속 폭발(각성)", (None, None, 20)),
        ]),
        ("frost", "서리", [
            (1, "둔화", "chance", 0.30, 2.0, 0.0, 1, "유틸", "이동 속도 감소(상태이상)", (10, 10, 5)),
            (2, "빙결", "every_n", 4, 0, 0.08, 1, "유틸", "4번째 타격마다 짧은 빙결", (None, 15, 10)),
            (3, "서리 파편", "chance", 0.06, 4.0, 0.30, 2, "피해", "얼음 파편이 주변에 피해", (None, None, 15)),
            (4, "극한의 파동", "periodic", 10, 0, 0.06, 5, "유틸", "10초마다 주변 둔화+빙결(각성)", (None, None, 20)),
        ]),
        ("thunder", "번개", [
            (1, "연쇄 번개", "chance", 0.08, 2.0, 0.24, 3, "피해", "주변 최대 2마리에 연쇄", (10, 10, 5)),
            (2, "치명타 번개", "crit", 1.0, 0, 0.30, 1, "피해", "치명타 시 추가 번개", (None, 15, 10)),
            (3, "과충전", "every_n", 8, 0, 0.14, 2, "피해", "8번째 타격마다 충전 방전", (None, None, 15)),
            (4, "낙뢰", "periodic", 12, 0, 0.11, 3, "피해", "12초마다 대상 위치 광역 번개(각성)", (None, None, 20)),
        ]),
        ("holy", "성광", [
            (1, "처치 시 회복", "chance", 0.0, 1.0, 0.0, 1, "회복", "처치 시 소량 회복(회복 상한 필요)", (10, 10, 5)),
            (2, "아군 버프", "periodic", 15, 0, 0.0, 1, "유틸", "근처 파티원 짧은 버프", (None, 15, 10)),
            (3, "성스러운 일격", "every_n", 10, 0, 0.25, 1, "피해", "10번째 타격마다 추가 성스러운 피해", (None, None, 15)),
            (4, "심판", "periodic", 10, 0, 0.14, 2, "피해", "10초마다 표식 대상 추가 피해(각성)", (None, None, 20)),
        ]),
        ("venom", "맹독", [
            (1, "중독", "chance", 0.20, 3.0, 0.17, 1, "피해", "스택형 지속 피해(최대 5스택)", (10, 10, 5)),
            (2, "방어 감소 표식", "chance", 0.15, 4.0, 0.07, 1, "유틸", "방어력 감소 표식(피해 증폭 환산)", (None, 15, 10)),
            (3, "부식 폭발", "every_n", 12, 0, 0.21, 2, "피해", "12번째 타격마다 부식 폭발", (None, None, 15)),
            (4, "역병 확산", "periodic", 9, 0, 0.07, 4, "피해", "9초마다 주변 전이(각성)", (None, None, 20)),
        ]),
        ("shadow", "그림자", [
            (1, "후방 추가 피해", "chance", 0.15, 0, 0.23, 1, "피해", "후방 공격 비율을 확률로 환산한 추가 피해", (10, 10, 5)),
            (2, "표식 추가 타격", "every_n", 6, 0, 0.18, 1, "피해", "6번째 타격마다 표식 추가 타격", (None, 15, 10)),
            (3, "그림자 베기", "chance", 0.05, 6.0, 0.50, 1, "피해", "낮은 확률의 강한 추가 베기", (None, None, 15)),
            (4, "그림자 분신", "periodic", 10, 0, 0.16, 1, "피해", "10초마다 분신 추가 타격(각성)", (None, None, 20)),
        ]),
    ]
    r = 17
    for key, pname, effs in PACKS:
        for (slot, ename, typ, param, icd, ratio, tg, cat, desc, unlock) in effs:
            put(ws, f"A{r}", key, "label")
            put(ws, f"B{r}", pname, "label")
            put(ws, f"C{r}", slot, "in", "0")
            put(ws, f"D{r}", ename, "label")
            put(ws, f"E{r}", typ, "in")
            put(ws, f"F{r}", param, "in", "0.00")
            put(ws, f"G{r}", icd, "in", NUM1)
            put(ws, f"H{r}", ratio, "in", NUM2)
            put(ws, f"I{r}", tg, "in", "0")
            put(ws, f"J{r}", cat, "label")
            put(ws, f"K{r}", desc, "note")
            for ci, crow in enumerate((11, 12, 13)):
                hps, cyc = f"$F${crow}", f"$E${crow}"
                rate = (f'=IF($E{r}="chance",MIN({hps}*$F{r},IF($G{r}>0,1/$G{r},999)),'
                        f'IF($E{r}="every_n",{hps}/$F{r},'
                        f'IF($E{r}="periodic",1/$F{r},'
                        f'IF($E{r}="finisher",1/({cyc}*$F{r}),'
                        f'IF($E{r}="crit",MIN({hps}*$B$4*$F{r},IF($G{r}>0,1/$G{r},999)),0)))))')
                put(ws, f"{CL(12 + ci)}{r}", rate, "f", NUM2)
                put(ws, f"{CL(15 + ci)}{r}", f"={CL(12 + ci)}{r}*$H{r}*(1+($I{r}-1)*$B$5)/{hps}", "f", PCT)
            put(ws, f"R{r}", f"=MAX(O{r}:Q{r})", "f", PCT)
            for ui, u in enumerate(unlock):
                put(ws, f"{CL(19 + ui)}{r}", u, "in", "0")
            r += 1
    EF_LAST = r - 1
    # 티어별 비중 요약
    section(ws, 42, "티어별 효과 DPS 비중(팩 × 티어) — 해금 규칙: T3=슬롯1, T4=슬롯1~2, T5=슬롯1~4(각성 포함)", 5)
    hdr_row(ws, 43, ["팩", "T3", "T4", "T5", "비고"])
    ranges = {}
    for pi, (key, pname, effs) in enumerate(PACKS):
        rr = 44 + pi
        put(ws, f"A{rr}", key, "label")
        for col, k, sc in (("B", 1, "$B$6"), ("C", 2, "$B$7"), ("D", 4, "$B$8")):
            terms = ",".join(f'SUMIFS(${c}$17:${c}${EF_LAST},$A$17:$A${EF_LAST},$A{rr},$C$17:$C${EF_LAST},"<={k}")' for c in ("O", "P", "Q"))
            put(ws, f"{col}{rr}", f"={sc}*MAX({terms})", "f", PCT)
        put(ws, f"E{rr}", pname, "note")
    put(ws, "A50", "최대", "bold")
    for col in "BCD":
        put(ws, f"{col}50", f"=MAX({col}44:{col}49)", "f", PCT)
    put(ws, "A51", "상한", "label")
    put(ws, "B51", f"={P['effect_cap']}", "link", PCT)
    put(ws, "A53", "※ 유틸·회복 효과는 피해 환산 0이라 비중에 반영되지 않는다. 연출·상태 효과의 체감은 별도 설계가 필요하다. 발동당 피해 값은 '목표 비중(효과당 2~3.5%)에서 역산한 초깃값'이며 실측으로 교체한다.", "note")
    put(ws, "A54", "※ 빈도가 높은 효과는 발동당 피해가 작아야 예산(15%) 안에 들어간다 → 체감은 낮은 확률·큰 연출의 효과(예: 불길 전이, 그림자 베기)가 만든다.", "note")
    widths(ws, {"A": 26, "B": 12, "C": 14, "D": 16, "E": 10, "F": 22, "G": 12, "H": 14, "I": 8, "J": 8, "K": 40, **{CL(k): 10 for k in range(12, 22)}})
    ws.freeze_panes = "E17"

    # ===== Items =====
    ws = S["Items"]
    put(ws, "A1", "Items — 품목 마스터 (직업별 NPC 매입 품목)", "title")
    put(ws, "A2", "D(목표 매입량)의 초기값은 기본 시나리오 일 판매량의 약 95%로 설정했다(가격이 완만히 하락하는 상태에서 시작). 입력은 파란 글씨.", "note")
    heads = ["item_id", "직업", "품목", "기준가 P_base", "하한가", "상한가", "목표 매입량 D(일)", "시간당 생산(초급)", "시간당 생산(중급)", "시간당 생산(고급)", "단위 재료비", "1인 일 생산(가중)", "서버 일 판매량 Qd", "90일 후 가격", "가격 변화율", "하한 고착 일수", "1시간 판매 합(기준가)"]
    hdr_row(ws, 4, heads)
    I_FIRST = 5
    I_LAST = I_FIRST + len(ITEMS) - 1
    # D 초기값 계산 (기본 시나리오)
    mix = (0.40, 0.40, 0.20)
    hrs = (1.5, 2.5, 3.0)
    dau0 = 100 * 3.0
    for i, (iid, job, nm, pb, rates, cost) in enumerate(ITEMS):
        r = I_FIRST + i
        dpu = sum(m * h * x for m, h, x in zip(mix, hrs, rates))
        qd = dau0 * 0.25 * dpu * 0.75
        d_init = int(round(qd * 0.95, -1))
        put(ws, f"A{r}", iid, "label")
        put(ws, f"B{r}", job, "label")
        put(ws, f"C{r}", nm, "label")
        put(ws, f"D{r}", pb, "in", NUM1)
        put(ws, f"E{r}", f"=D{r}*{P['floor_mult']}", "f", NUM1)
        put(ws, f"F{r}", f"=D{r}*{P['cap_mult']}", "f", NUM1)
        put(ws, f"G{r}", d_init, "in", NUM)
        for k, x in enumerate(rates):
            put(ws, f"{CL(8 + k)}{r}", x, "in", NUM1)
        put(ws, f"K{r}", cost, "in", NUM1)
        put(ws, f"L{r}", f"={P['mix_new']}*{P['h_new']}*H{r}+{P['mix_mid']}*{P['h_mid']}*I{r}+{P['mix_high']}*{P['h_high']}*J{r}", "f", NUM1)
        put(ws, f"M{r}", f"={P['e_dau']}*INDEX({JSHARE_VALS},MATCH(B{r},{JSHARE_NAMES},0))*L{r}*{P['sell_ratio']}", "f", NUM)
        # N: 90일 후 가격 -> PriceSim
        pcol = CL(3 + 3 * i)
        put(ws, f"N{r}", f"=PriceSim!{pcol}94", "link", NUM1)
        put(ws, f"O{r}", f"=N{r}/D{r}-1", "f", PCT)
        put(ws, f"P{r}", f'=COUNTIF(PriceSim!{pcol}5:{pcol}94,"<="&E{r}*1.0001)', "f", NUM)
        put(ws, f"Q{r}", f"=H{r}*D{r}", "f", NUM)
    put(ws, f"A{I_LAST+2}", "기본 시나리오 기준 D = 일 판매량 × 0.95 (반올림). D를 바꾸면 가격이 달라진다 — 직업 간 수익 균형 조정 레버.", "note")
    # 예시 행 안내
    put(ws, f"A{I_LAST+3}", "예시 행 형식(새 품목 추가 시): item_id=farm:wheat · 직업=농부 · P_base=12 · D=10,000 · 시간당 생산=45/70/110 · 단위 재료비=0 (요리는 재료비 입력)", "note")
    P["items_job"] = f"Items!$B${I_FIRST}:$B${I_LAST}"
    P["items_pfinal"] = f"Items!$N${I_FIRST}:$N${I_LAST}"
    P["items_pbase"] = f"Items!$D${I_FIRST}:$D${I_LAST}"
    P["items_cost"] = f"Items!$K${I_FIRST}:$K${I_LAST}"
    P["items_floor"] = f"Items!$P${I_FIRST}:$P${I_LAST}"
    widths(ws, {"A": 22, "B": 8, "C": 16, **{CL(k): 12 for k in range(4, 18)}})
    ws.freeze_panes = "D5"

    # ===== PriceSim =====
    ws = S["PriceSim"]
    put(ws, "A1", "PriceSim — 변동 시세 90일 시뮬레이션 (명세 7.2장: Q=EMA, P=clamp(P_base×(D/Q)^alpha), 일일 변동폭 제한)", "title")
    put(ws, "A3", "Day", "hdr")
    for i in range(len(ITEMS)):
        r_item = I_FIRST + i
        c0 = 2 + 3 * i
        put(ws, f"{CL(c0)}2", f"=Items!C{r_item}", "link")
        put(ws, f"{CL(c0)}3", "Q(EMA)", "hdr")
        put(ws, f"{CL(c0+1)}3", "가격", "hdr")
        put(ws, f"{CL(c0+2)}3", "매출", "hdr")
    TOTC = 2 + 3 * len(ITEMS)
    put(ws, f"{CL(TOTC)}3", "NPC 판매 합계", "hdr")
    for t in range(0, 91):
        r = 4 + t
        put(ws, f"A{r}", t, "label", "0")
        parts = []
        for i in range(len(ITEMS)):
            r_item = I_FIRST + i
            cq, cp, cr = CL(2 + 3 * i), CL(3 + 3 * i), CL(4 + 3 * i)
            qd = f"Items!$M${r_item}*(1+{P['growth']})^$A{r}"
            if t == 0:
                put(ws, f"{cq}{r}", f"=Items!$M${r_item}", "link", NUM)
                put(ws, f"{cp}{r}", f"=Items!$D${r_item}", "link", NUM1)
            else:
                put(ws, f"{cq}{r}", f"={cq}{r-1}+({qd}-{cq}{r-1})*2/({P['ema_days']}+1)", "f", NUM)
                raw = f"Items!$D${r_item}*(Items!$G${r_item}/MAX({cq}{r},{P['q_min']}))^{P['e_alpha']}"
                clamp = f"MIN(MAX({raw},Items!$E${r_item}),Items!$F${r_item})"
                put(ws, f"{cp}{r}", f"={cp}{r-1}*(1+MAX(-{P['max_chg']},MIN({P['max_chg']},{clamp}/{cp}{r-1}-1)))", "f", NUM1)
            if t == 0:
                put(ws, f"{cr}{r}", f"={cq}{r}*{cp}{r}", "f", NUM)
            else:
                put(ws, f"{cr}{r}", f"={qd}*{cp}{r}", "f", NUM)
            parts.append(f"{cr}{r}")
        put(ws, f"{CL(TOTC)}{r}", "=" + "+".join(parts), "f", NUM)
    widths(ws, {"A": 6, **{CL(k): 10 for k in range(2, TOTC + 1)}, CL(TOTC): 16})
    ws.freeze_panes = "B4"
    put(ws, f"A96", "※ Day 0은 시작 상태(가격=기준가, Q=Qd). 매출은 해당일 판매량 × 해당일 가격 = 신규 Coin 발행(NPC 판매).", "note")

    # ===== JobIncome =====
    ws = S["JobIncome"]
    put(ws, "A1", "JobIncome — 직업별 레벨 구간 시간당 수익", "title")
    put(ws, "A2", "수익 = Σ(시간당 생산 × (90일 후 가격 − 단위 재료비)). 비용은 씨앗·입장·연료·미끼 등 시간당 부대비용(입력).", "note")
    hdr_row(ws, 4, ["직업", "구간", "수익(기준가)", "수익(90일 후 가격)", "시간당 부대비용", "시간당 순수익", "구간 평균", "비율(순수익/평균)", "판정"])
    J_FIRST = 5
    for ji, j in enumerate(JOBS):
        for bi, b in enumerate(BANDS):
            r = J_FIRST + ji * 3 + bi
            rate_col = ["H", "I", "J"][bi]
            put(ws, f"A{r}", j, "label")
            put(ws, f"B{r}", b, "label")
            put(ws, f"C{r}", f"=SUMPRODUCT(({P['items_job']}=A{r})*Items!${rate_col}${I_FIRST}:${rate_col}${I_LAST}*({P['items_pbase']}-{P['items_cost']}))", "f", NUM)
            put(ws, f"D{r}", f"=SUMPRODUCT(({P['items_job']}=A{r})*Items!${rate_col}${I_FIRST}:${rate_col}${I_LAST}*({P['items_pfinal']}-{P['items_cost']}))", "f", NUM)
            put(ws, f"E{r}", JOB_COST[j][bi], "in", NUM)
            put(ws, f"F{r}", f"=D{r}-E{r}", "f", NUM)
            put(ws, f"G{r}", f"=AVERAGEIF($B${J_FIRST}:$B${J_FIRST+11},B{r},$F${J_FIRST}:$F${J_FIRST+11})", "f", NUM)
            put(ws, f"H{r}", f"=F{r}/G{r}", "f", RATIO)
            put(ws, f"I{r}", f'=IF(AND(H{r}>={P["dev_min"]},H{r}<={P["dev_max"]}),"OK","검토")', "f")
    J_LAST = J_FIRST + 11
    status_format(ws, f"I{J_FIRST}:I{J_LAST}")
    r0 = J_LAST + 2
    section(ws, r0, "요약", 4)
    put(ws, f"A{r0+1}", "중견 구간 평균 시간당 순수익", "label")
    put(ws, f"D{r0+1}", f'=INDEX($G${J_FIRST}:$G${J_LAST},MATCH("중급",$B${J_FIRST}:$B${J_LAST},0))', "f", NUM)
    put(ws, f"A{r0+2}", "중견 유저 일 소득(Coin/일)", "label")
    put(ws, f"D{r0+2}", f"=D{r0+1}*{P['h_mid']}", "f", NUM)
    put(ws, f"A{r0+3}", "구간별 최소/최대 비율", "label")
    for bi, b in enumerate(BANDS):
        put(ws, f"A{r0+4+bi}", f"  {b}: 최소 / 최대", "label")
        put(ws, f"D{r0+4+bi}", f'=MIN(H{J_FIRST+bi},H{J_FIRST+3+bi},H{J_FIRST+6+bi},H{J_FIRST+9+bi})', "f", RATIO)
        put(ws, f"E{r0+4+bi}", f"=MAX(H{J_FIRST+bi},H{J_FIRST+3+bi},H{J_FIRST+6+bi},H{J_FIRST+9+bi})", "f", RATIO)
    P["income_mid_day"] = f"JobIncome!$D${r0+2}"
    P["jdev_min_rng"] = f"JobIncome!$D${r0+4}:$D${r0+6}"
    P["jdev_max_rng"] = f"JobIncome!$E${r0+4}:$E${r0+6}"
    put(ws, f"A{r0+8}", "※ 요리 수익은 재료비를 차감한 마진 기준이다(명세 7.2장: 원재료 가격 대비 마진). 직업 간 편차는 Items의 D(목표 매입량)·생산량·시간당 비용으로 조정한다.", "note")
    widths(ws, {"A": 34, "B": 8, "C": 14, "D": 18, "E": 16, "F": 14, "G": 12, "H": 16, "I": 8})

    # ===== Enhance =====
    ws = S["Enhance"]
    put(ws, "A1", "Enhance — 강화 단계별 기대 비용(파괴 시 재구축 포함)·피해 곡선", "title")
    put(ws, "A2", "E_n = (c + d × R_n) / s,  R_n = 장비 구매가 + Σ(이전 단계 E).  성공/유지/파괴 합 = 100% 검증. 시나리오의 성공률 가감은 '유지' 확률이 흡수한다. 몬테카를로(90% 분위)는 미구현.", "note")
    put(ws, "A3", "예시 무기 티어 배율", "label")
    put(ws, "C3", f"=INDEX({P['tier_mult_rng']},{P['enh_tier']}+1)", "link", NUM2)
    heads = ["n", "단계", "성공(기본)", "파괴(기본)", "성공(적용)", "유지(적용)", "파괴(적용)", "합계(검증)", "Coin 비용", "강화석 수", "1회 총비용(c)", "재구축 비용 R_n", "단계 기대 비용 E_n", "누적 기대 비용", "n+1 단계 피해", "판정"]
    hdr_row(ws, 5, heads)
    E_FIRST = 6
    for n in range(20):
        r = E_FIRST + n
        put(ws, f"A{r}", n, "label", "0")
        put(ws, f"B{r}", f"+{n} → +{n+1}", "label")
        put(ws, f"C{r}", ENH_S[n], "in", PCT)
        put(ws, f"D{r}", ENH_D[n], "in", PCT)
        put(ws, f"E{r}", f"=MAX(0.01,MIN(0.99,C{r}+{P['e_enh']}))", "f", PCT)
        put(ws, f"F{r}", f"=MAX(0,1-E{r}-G{r})", "f", PCT)
        put(ws, f"G{r}", f"=D{r}", "f", PCT)
        put(ws, f"H{r}", f"=E{r}+F{r}+G{r}", "f", PCT)
        put(ws, f"I{r}", f"={P['enh_base']}*{P['enh_growth']}^A{r}", "f", NUM)
        put(ws, f"J{r}", f"=1+INT(A{r}/4)", "f", NUM)
        put(ws, f"K{r}", f"=I{r}+J{r}*{P['stone_val']}", "f", NUM)
        prev = "0" if n == 0 else f"N{r-1}"
        put(ws, f"L{r}", f"={P['start_price']}+{prev}", "f", NUM)
        put(ws, f"M{r}", f"=(K{r}+G{r}*L{r})/E{r}", "f", NUM)
        put(ws, f"N{r}", f"={'' if n == 0 else f'N{r-1}+'}M{r}", "f", NUM)
        put(ws, f"O{r}", f"={P['base_dmg']}*$C$3*(1+{P['enh_k']}*(A{r}+1))", "f", NUM2)
        put(ws, f"P{r}", f'=IF(ABS(H{r}-1)<0.0001,"OK","검토")', "f")
    E_LAST = E_FIRST + 19
    status_format(ws, f"P{E_FIRST}:P{E_LAST}")
    r0 = E_LAST + 2
    section(ws, r0, "목표 단계 요약", 6)
    put(ws, f"A{r0+1}", "목표 강화 단계(+)", "label")
    put(ws, f"D{r0+1}", f"={P['target_lv']}", "link", NUM)
    put(ws, f"A{r0+2}", "목표까지 기대 누적 비용(Coin, 장비 구매가 별도)", "label")
    put(ws, f"D{r0+2}", f"=INDEX($N${E_FIRST}:$N${E_LAST},D{r0+1})", "f", NUM)
    put(ws, f"A{r0+3}", "장비 구매가 포함 총비용", "label")
    put(ws, f"D{r0+3}", f"=D{r0+2}+{P['start_price']}", "f", NUM)
    put(ws, f"A{r0+4}", "중견 유저 일 소득", "label")
    put(ws, f"D{r0+4}", f"={P['income_mid_day']}", "link", NUM)
    put(ws, f"A{r0+5}", "강화에 쓰는 일 예산", "label")
    put(ws, f"D{r0+5}", f"=D{r0+4}*{P['enh_share']}", "f", NUM)
    put(ws, f"A{r0+6}", "목표 도달 필요 일수", "label")
    put(ws, f"D{r0+6}", f"=D{r0+3}/D{r0+5}", "f", NUM1)
    put(ws, f"A{r0+7}", "설계 목표 일수 대비 편차", "label")
    put(ws, f"D{r0+7}", f"=D{r0+6}/{P['design_days']}-1", "f", PCT)
    put(ws, f"A{r0+8}", "목표 단계에서의 1회 총비용(소각 계산용)", "label")
    put(ws, f"D{r0+8}", f"=INDEX($K${E_FIRST}:$K${E_LAST},D{r0+1})", "f", NUM)
    put(ws, f"A{r0+9}", "목표 단계 피해 / +0 피해", "label")
    put(ws, f"D{r0+9}", f"=INDEX($O${E_FIRST}:$O${E_LAST},D{r0+1})/({P['base_dmg']}*$C$3)", "f", NUM2)
    P["enh_cum"] = f"Enhance!$D${r0+2}"
    P["enh_days"] = f"Enhance!$D${r0+6}"
    P["enh_dev"] = f"Enhance!$D${r0+7}"
    P["enh_cost1"] = f"Enhance!$D${r0+8}"
    P["enh_budget"] = f"Enhance!$D${r0+5}"
    P["enh_total_cost_row"] = r0 + 3
    widths(ws, {"A": 46, "B": 11, "C": 12, **{CL(k): 13 for k in range(4, 17)}})
    ws.freeze_panes = "C6"

    # ===== Gacha =====
    ws = S["Gacha"]
    put(ws, "A1", "Gacha — 가구 뽑기 확률·천장·컬렉션 기대값", "title")
    put(ws, "A2", "천장 효과: 영웅 이상 확률 p, 천장 N회 → 평균 N회 중 첫 영웅+ 기대 뽑기 = (1−(1−p)^N)/p. 난수 시뮬레이션은 미구현(분석식).", "note")
    hdr_row(ws, 4, ["티어", "확률", "풀 크기", "티어 평균 기대 획득 뽑기(1종)", "H_n(조화수)", "전체 수집 기대 뽑기(근사)", "전체 수집 기대 비용(Coin)"])
    tiers = [("일반", "g_common", "n_common"), ("희귀", "g_rare", "n_rare"), ("영웅", "g_epic", "n_epic"), ("전설", "g_legend", "n_legend")]
    # 조화수 보조표 (n=1..60) — 열 K,L
    put(ws, "J3", "보조표: 조화수 H_n", "bold")
    put(ws, "J4", "n", "hdr")
    put(ws, "K4", "H_n", "hdr")
    for n in range(1, 61):
        r = 4 + n
        put(ws, f"J{r}", n, "label", "0")
        put(ws, f"K{r}", f"=1/J{r}" if n == 1 else f"=K{r-1}+1/J{r}", "f", '0.0000')
    for i, (nm, kr, kn) in enumerate(tiers):
        r = 5 + i
        put(ws, f"A{r}", nm, "label")
        put(ws, f"B{r}", f"={P[kr]}", "link", PCT)
        put(ws, f"C{r}", f"={P[kn]}", "link", NUM)
        put(ws, f"D{r}", f"=1/B{r}", "f", NUM1)
        put(ws, f"E{r}", f"=INDEX($K$5:$K$64,C{r})", "f", '0.0000')
        put(ws, f"F{r}", f"=C{r}*E{r}/B{r}", "f", NUM)
        put(ws, f"G{r}", f"=F{r}*{P['e_g1']}", "f", NUM)
    put(ws, "A9", "확률 합계(검증)", "bold")
    put(ws, "B9", "=SUM(B5:B8)", "f", PCT)
    put(ws, "C9", '=IF(ABS(B9-1)<0.0001,"OK","검토")', "f")
    status_format(ws, "C9")
    section(ws, 11, "천장 반영 실효 확률", 7)
    put(ws, "A12", "영웅 이상 확률 p(1회)", "label")
    put(ws, "D12", "=B7+B8", "f", PCT)
    put(ws, "A13", "천장 N(회)", "label")
    put(ws, "D13", f"={P['pity']}", "link", NUM)
    put(ws, "A14", "영웅 이상 첫 획득까지 평균 뽑기(천장 포함)", "label")
    put(ws, "D14", "=(1-(1-D12)^D13)/D12", "f", NUM1)
    put(ws, "A15", "영웅 이상 실효 확률(1회당)", "label")
    put(ws, "D15", "=1/D14", "f", PCT)
    put(ws, "A16", "전설 실효 확률(1회당, 천장 시 영웅+ 중 전설 비율 적용)", "label")
    put(ws, "D16", "=B8/(D12*D14)", "f", '0.00%')
    put(ws, "A17", "전설 1개 기대 뽑기", "label")
    put(ws, "D17", "=1/D16", "f", NUM1)
    put(ws, "A18", "전설 1개 기대 비용(Coin, 1회 가격 기준)", "label")
    put(ws, "D18", f"=D17*{P['e_g1']}", "f", NUM)
    put(ws, "A19", "중견 유저 월소득(Coin)", "label")
    put(ws, "D19", f"={P['income_mid_day']}*30", "link", NUM)
    put(ws, "A20", "전설 기대 비용 / 중견 월소득", "label")
    put(ws, "D20", "=D18/D19", "f", PCT)
    put(ws, "A21", "10회 구매 할인율(실효)", "label")
    put(ws, "D21", f"=1-{P['e_g10']}/(10*{P['e_g1']})", "f", PCT)
    put(ws, "A27", "※ 가구에 등급(일반/희귀/영웅/전설)을 두지 않는 경우 이 시트의 티어 확률은 참고용이며, Gacha_Compare 5절의 등급 없는 균등 풀 분석을 본다.", "note")
    put(ws, "A23", "※ 전체 수집 기대 뽑기는 티어별 쿠폰 수집가 근사(n×H_n÷확률)이며 티어 간 최대값을 전체 근사로 본다(천장 효과 미반영 → 보수적).", "note")
    put(ws, "A24", "전체 수집 기대 뽑기(근사)", "label")
    put(ws, "D24", "=MAX(F5:F8)", "f", NUM)
    put(ws, "A25", "전체 수집 기대 비용(Coin)", "label")
    put(ws, "D25", f"=D24*{P['e_g1']}", "f", NUM)
    P["g_epic_eff"] = "Gacha!$D$15"
    P["g_leg_ratio"] = "Gacha!$D$20"
    P["g_prob_ok"] = "Gacha!$C$9"
    widths(ws, {"A": 52, "B": 10, "C": 10, "D": 26, "E": 12, "F": 24, "G": 24, "J": 6, "K": 10})

    # ===== Housing_Sinks =====
    ws = S["Housing_Sinks"]
    put(ws, "A1", "Housing_Sinks — Coin 소각 항목 (성숙 시 일 소각 = DAU × 참여율 × 1인당 일 이용 × 단가)", "title")
    hdr_row(ws, 3, ["항목", "단가(Coin)", "1인당 일 이용(참여자 기준)", "참여 비율", "일 소각(성숙 시)", "비중", "단가 출처·비고"])
    terms = []
    for ji in range(4):
        for bi, (mk, hk) in enumerate((("mix_new", "h_new"), ("mix_mid", "h_mid"), ("mix_high", "h_high"))):
            terms.append(f"Params!$E${jr+1+ji}*{P[mk]}*{P[hk]}*JobIncome!$E${J_FIRST + ji*3 + bi}")
    JOBCOST_FORMULA = "=" + "+".join(terms)
    sinks = [
        ("경작지 구매·확장", 8000, 0.03, 0.15, "[제안]"),
        ("주택 구매", 40000, 0.006, 0.10, "[제안]"),
        ("주택 임대·유지(일환산)", 115, 1.0, 0.10, "800/주 ÷ 7 [제안]"),
        ("주택 확장·슬롯", 5000, 0.01, 0.10, "[제안]"),
        ("가구 직접 구매", 500, 0.2, 0.40, "[제안]"),
        ("가구 뽑기", f"={P['e_g1']}", f"={P['pulls_dau']}", 0.25, "Gacha·Params 참조"),
        ("창고 확장", 1500, 0.01, 0.20, "[제안]"),
        ("편의 워프", 30, 3.0, 0.50, "[제안]"),
        ("인챈트(별도 서비스)", 1200, 0.2, 0.40, "[제안]"),
        ("강화(일 예산 = 중견 일 소득 × 강화 비중)", f"={P['income_mid_day']}*{P['enh_share']}", 1.0, 0.80, "JobIncome·Params 참조(참여자는 예산을 모두 사용한다고 가정)"),
        ("상점 구매(장비·도구·씨앗 등)", f"={P['income_mid_day']}*{P['shop_share']}", 1.0, 0.90, "중견 일 소득 × 상점 소비 비중"),
        ("직업 부대비용(씨앗·입장·연료·미끼)", JOBCOST_FORMULA, 1.0, 1.0, "JobIncome 시간당 비용 × 시간 × 비중(1인당 평균)"),
        ("요리 재료비(NPC 구매)", f"=SUMPRODUCT(Items!$K${I_FIRST}:$K${I_LAST},Items!$M${I_FIRST}:$M${I_LAST})/{P['e_dau']}", 1.0, 1.0, "요리 재료비 × 일 생산량 ÷ DAU"),
        ("이름 스타일 구매", 800, 0.02, 0.20, "[제안]"),
        ("칭호 상점 구매", 500, 0.02, 0.20, "[제안]"),
        ("직업 변경 수수료", 2000, 0.01, 1.00, "[제안]"),
        ("닉네임 변경", 5000, 0.002, 1.00, "[제안]"),
        ("시작 무기 진화", 300, 0.03, 0.30, "[제안]"),
        ("유저 간 거래 수수료", f"={P['fee']}*{P['p2p']}", 1.0, 1.0, "수수료율 × 1인당 거래액"),
    ]
    S_FIRST = 4
    for i, (nm, price, use, part, note) in enumerate(sinks):
        r = S_FIRST + i
        put(ws, f"A{r}", nm, "label")
        isf = isinstance(price, str)
        put(ws, f"B{r}", price, "link" if isf else "in", NUM)
        usf = isinstance(use, str)
        put(ws, f"C{r}", use, "link" if usf else "in", NUM2 if not usf else NUM2)
        put(ws, f"D{r}", part, "in", PCT)
        put(ws, f"E{r}", f"={P['e_dau']}*D{r}*C{r}*B{r}", "f", NUM)
        put(ws, f"G{r}", note, "note")
    S_LAST = S_FIRST + len(sinks) - 1
    for r in range(S_FIRST, S_LAST + 1):
        put(ws, f"F{r}", f"=E{r}/$E${S_LAST+1}", "f", PCT)
    put(ws, f"A{S_LAST+1}", "합계(일, 성숙 시)", "bold")
    put(ws, f"E{S_LAST+1}", f"=SUM(E{S_FIRST}:E{S_LAST})", "f", NUM)
    put(ws, f"A{S_LAST+2}", "1인(DAU)당 일 소각", "label")
    put(ws, f"E{S_LAST+2}", f"=E{S_LAST+1}/{P['e_dau']}", "f", NUM)
    put(ws, f"A{S_LAST+4}", "※ '유저 간 거래 수수료'는 거래액 자체가 아닌 수수료만 소각이다(거래액은 이동이므로 FlowBalance에서 별도 집계).", "note")
    P["sink_total"] = f"Housing_Sinks!$E${S_LAST+1}"
    widths(ws, {"A": 34, "B": 14, "C": 22, "D": 12, "E": 18, "F": 10, "G": 34})

    # ===== FlowBalance =====
    ws = S["FlowBalance"]
    put(ws, "A1", "FlowBalance — 발행·소각·이동 집계와 총통화량 (90일)", "title")
    put(ws, "A2", "발행=NPC 판매+출석+퀘스트, 소각=Housing_Sinks × 성숙도, 이동=유저 간 거래액(통화량 불변). 총통화량 = 이전 + 발행 − 소각.", "note")
    hdr_row(ws, 3, ["Day", "NPC 판매(발행)", "출석(발행)", "퀘스트·이벤트(발행)", "발행 합계", "소각 성숙도", "소각 합계", "이동(유저 간 거래)", "순증감(발행−소각)", "총통화량", "1인당 보유", "1인당 일 발행", "보유/일 발행(배)", "소각/발행"])
    for t in range(0, 91):
        r = 4 + t
        put(ws, f"A{r}", t, "label", "0")
        if t == 0:
            put(ws, f"J{r}", f"={P['e_dau']}*{P['m0']}", "f", NUM)
            put(ws, f"K{r}", f"=J{r}/{P['e_dau']}", "f", NUM)
            continue
        put(ws, f"B{r}", f"=PriceSim!{CL(TOTC)}{r}", "link", NUM)
        put(ws, f"C{r}", f"={P['e_dau']}*{P['att_reward']}*{P['att_claim']}", "f", NUM)
        put(ws, f"D{r}", f"={P['e_dau']}*{P['quest']}", "f", NUM)
        put(ws, f"E{r}", f"=SUM(B{r}:D{r})", "f", NUM)
        put(ws, f"F{r}", f"=MIN(1,{P['sink_start']}+(1-{P['sink_start']})*A{r}/{P['sink_ramp']})", "f", PCT)
        put(ws, f"G{r}", f"={P['sink_total']}*F{r}", "f", NUM)
        put(ws, f"H{r}", f"={P['e_dau']}*{P['p2p']}", "f", NUM)
        put(ws, f"I{r}", f"=E{r}-G{r}", "f", NUM)
        put(ws, f"J{r}", f"=J{r-1}+I{r}", "f", NUM)
        put(ws, f"K{r}", f"=J{r}/{P['e_dau']}", "f", NUM)
        put(ws, f"L{r}", f"=E{r}/{P['e_dau']}", "f", NUM)
        put(ws, f"M{r}", f"=K{r}/L{r}", "f", NUM1)
        put(ws, f"N{r}", f"=G{r}/E{r}", "f", PCT)
    FB_LAST = 94
    put(ws, "A96", "※ 순증감이 오랫동안 크게 양수면 인플레이션, 음수면 디플레이션이다. 1:1 균형이 아니라 유저 구간별 균형을 본다(명세 18장).", "note")
    P["fb_net90"] = f"FlowBalance!$I${FB_LAST}"
    P["fb_money_ratio"] = f"FlowBalance!$M${FB_LAST}"
    P["fb_sink_ratio"] = f"FlowBalance!$N${FB_LAST}"
    P["fb_supply90"] = f"FlowBalance!$J${FB_LAST}"
    widths(ws, {"A": 6, **{CL(k): 15 for k in range(2, 15)}})
    ws.freeze_panes = "B4"

    # ===== MonteCarlo =====
    build_mc_sheet(S["MonteCarlo"], P, mc)
    build_gc_sheet(S["Gacha_Compare"], P, gc)
    build_em_sheet(S["Enhance_Mitigation"], P, em)
    build_live_sheet(S["Live_Sim"], P)

    # ===== Dashboard =====
    ws = S["Dashboard"]
    put(ws, "A1", "Dashboard — 합격 기준 판정 요약", "title")
    put(ws, "A2", "선택 시나리오", "bold")
    put(ws, "B2", "=Scenarios!B14", "link")
    hdr_row(ws, 4, ["지표", "목표(기준)", "현재 값", "판정", "설명"])
    rows = [
        ("직업 간 순수익 비율(중급) 최소", f'=">= "&TEXT({P["dev_min"]},"0.00")', f"=INDEX({P['jdev_min_rng']},2)", f'=IF(C{{r}}>={P["dev_min"]},"OK","검토")', RATIO, "4직업 평균 대비 최저 직업"),
        ("직업 간 순수익 비율(중급) 최대", f'="<= "&TEXT({P["dev_max"]},"0.00")', f"=INDEX({P['jdev_max_rng']},2)", f'=IF(C{{r}}<={P["dev_max"]},"OK","검토")', RATIO, "4직업 평균 대비 최고 직업"),
        ("직업 간 순수익 비율(전 구간) 최소", f'=">= "&TEXT({P["dev_min"]},"0.00")', f"=MIN({P['jdev_min_rng']})", f'=IF(C{{r}}>={P["dev_min"]},"OK","검토")', RATIO, "초급·중급·고급 모두"),
        ("직업 간 순수익 비율(전 구간) 최대", f'="<= "&TEXT({P["dev_max"]},"0.00")', f"=MAX({P['jdev_max_rng']})", f'=IF(C{{r}}<={P["dev_max"]},"OK","검토")', RATIO, "초급·중급·고급 모두"),
        ("요리 마진(90일 후 가격−재료비) 최소", '="> 0"', f'=MIN(Items!$N${I_FIRST+6}-Items!$K${I_FIRST+6},Items!$N${I_FIRST+7}-Items!$K${I_FIRST+7},Items!$N${I_FIRST+8}-Items!$K${I_FIRST+8})', '=IF(C{r}>0,"OK","검토")', NUM1, "요리 3품목 중 최저 마진"),
        ("가격 하한 고착 일수 최대(90일)", f'="<= "&{P["floor_max"]}', f"=MAX({P['items_floor']})", f'=IF(C{{r}}<={P["floor_max"]},"OK","검토")', NUM, "하한가에 붙어 있는 날 수가 많으면 수요 부족"),
        ("목표 강화 도달 일수", f'="설계 "&{P["design_days"]}&"일 ±"&TEXT({P["days_tol"]},"0%")', f"={P['enh_days']}", f'=IF(ABS({P["enh_dev"]})<={P["days_tol"]},"OK","검토")', NUM1, "중견 일 소득 × 강화 비중으로 소화하는 데 걸리는 일수"),
        ("가구 뽑기 확률 합계", '="= 100%"', "=Gacha!B9", f'={P["g_prob_ok"]}', PCT, "공개 확률표 합 검증"),
        ("영웅+ 실효 확률(천장 포함)", '="공개 10% 대비 상승"', f"={P['g_epic_eff']}", '=IF(C{r}>Gacha!D12,"OK","검토")', PCT, "천장 적용 시 공개 확률과의 차이 — 고지 문구 필요"),
        ("전설 1개 기대 비용 / 중견 월소득", f'="<= "&TEXT({P["legend_max"]},"0%")', f"={P['g_leg_ratio']}", f'=IF(C{{r}}<={P["legend_max"]},"OK","검토")', PCT, "뽑기 체감 부담"),
        ("90일차 순증감(발행−소각)", '="0 이상(완만한 증가)"', f"={P['fb_net90']}", '=IF(C{r}>=0,"OK","검토")', NUM, "음수면 디플레이션 신호"),
        ("90일차 1인당 보유 / 일 발행(배)", f'="<= "&{P["money_max"]}', f"={P['fb_money_ratio']}", f'=IF(C{{r}}<={P["money_max"]},"OK","검토")', NUM1, "과잉 축적 신호"),
        ("아키타입 DPS 비율 최대", f'="1 ±"&TEXT({P["dps_tol"]},"0%")', f"={P['dps_max']}", f'=IF(ABS(C{{r}}-1)<={P["dps_tol"]},"OK","검토")', RATIO, "Weapons_DPS"),
        ("아키타입 DPS 비율 최소", f'="1 ±"&TEXT({P["dps_tol"]},"0%")', f"={P['dps_min']}", f'=IF(ABS(C{{r}}-1)<={P["dps_tol"]},"OK","검토")', RATIO, "Weapons_DPS"),
        ("특수 효과 DPS 비중 최대(티어)", f'="<= "&TEXT({P["effect_cap"]},"0%")', f"={P['effect_max']}", f'=IF(C{{r}}<={P["effect_cap"]},"OK","검토")', PCT, "Weapons_DPS 티어 표"),
        ("유저 비율 합계", '="= 100%"', f"={P['mix_sum']}", '=IF(ABS(C{r}-1)<0.0001,"OK","검토")', PCT, "Params 입력 검증"),
        ("강화 비용 P90 / 평균(목표 단계, 난수 시뮬)", '="<= 2.0배"', f'=IF(Scenarios!$B$2=1,{P["mc_p90_ratio"]},"n/a")', '=IF(ISNUMBER(C{r}),IF(C{r}<=2,"OK","검토"),"n/a")', NUM2, "MonteCarlo(정적, 기본 시나리오만)"),
        ("전설 1개 P90 비용 / 중견 월소득(난수 시뮬)", f'="<= "&TEXT({P["legend_max"]}*2,"0%")', f'=IF(Scenarios!$B$2=1,{P["mc_leg_ratio"]},"n/a")', f'=IF(ISNUMBER(C{{r}}),IF(C{{r}}<={P["legend_max"]}*2,"OK","검토"),"n/a")', PCT, "MonteCarlo(정적, 기본 시나리오만). 기준은 평균 기준 상한의 2배"),
    ]
    D_FIRST = 5
    for i, (lab, tgt, cur, stat, fmt, desc) in enumerate(rows):
        r = D_FIRST + i
        put(ws, f"A{r}", lab, "label")
        put(ws, f"B{r}", tgt, "f")
        put(ws, f"C{r}", cur, "f", fmt)
        put(ws, f"D{r}", stat.replace("{r}", str(r)), "f")
        put(ws, f"E{r}", desc, "note")
    D_LAST = D_FIRST + len(rows) - 1
    status_format(ws, f"D{D_FIRST}:D{D_LAST}")
    put(ws, f"A{D_LAST+2}", "판정 요약", "bold")
    put(ws, f"C{D_LAST+2}", f'=COUNTIF(D{D_FIRST}:D{D_LAST},"OK")&" / "&(COUNTA(D{D_FIRST}:D{D_LAST})-COUNTIF(D{D_FIRST}:D{D_LAST},"n/a"))&" 통과"', "f")
    put(ws, f"A{D_LAST+4}", "※ 미구현: 방어력 상성, 우클릭 특수 공격 DPS, 효과 포함 실측 DPS, 유틸·회복 가치 환산 — G3 후속 과제. 난수 시뮬 판정 2행은 기본 시나리오에서만 계산한다(시나리오 변경 시 n/a).", "note")
    widths(ws, {"A": 42, "B": 26, "C": 16, "D": 10, "E": 52})
    DASH = {"first": D_FIRST, "last": D_LAST, "rows": [r[0] for r in rows]}

    # ===== Scenarios 스냅샷 표 자리 =====
    ws = S["Scenarios"]
    put(ws, "A17", "시나리오별 결과 스냅샷 (정적 값 — build_g3.py가 시나리오별로 재계산해 기록, 선택 시나리오와 무관)", "bold")
    SNAP_HEAD_ROW = 18

    # ===== Legend =====
    ws = S["Legend"]
    put(ws, "A1", "G3 경제·밸런스 시뮬레이션 워크북", "title")
    lines = [
        ("목적", "docs/G3-economy-simulation-sheet.md의 시트 구조를 수식으로 구현했다. 모든 수치는 [제안]이며 실측으로 교체한다."),
        ("색 규칙", "파란 글씨 = 입력(수정 가능) · 검정 = 수식 · 초록 = 다른 시트 값을 가져온 링크 · 노란 칸 = 핵심 가정"),
        ("수정 방법", "Params, Items, JobIncome(부대비용), Enhance(확률), Weapons_DPS(아키타입 입력), Housing_Sinks(단가·이용률)의 파란 칸만 고친다. 나머지는 자동 계산된다."),
        ("시나리오", "Scenarios!B2 에서 1~7 선택 → Params '시나리오 적용값' 반영. 비교 스냅샷 표는 정적 값이다."),
        ("시트 구성", "Params · Scenarios · Items · JobIncome · PriceSim · Enhance · Gacha · Housing_Sinks · FlowBalance · Weapons_DPS · Effect_Packs · MonteCarlo · Gacha_Compare · Enhance_Mitigation · Live_Sim · Dashboard"),
        ("읽는 순서", "Params → Items → PriceSim → JobIncome → Enhance/Gacha → Housing_Sinks → FlowBalance → Dashboard"),
        ("난수 시뮬", "MonteCarlo = 스크립트가 수만 회 시행한 정적 결과(시드 고정, 기본 시나리오). Live_Sim = 시트 안의 RAND() 수식으로 한 번씩 굴려 보는 체험(재계산 때마다 값이 바뀜: F9)."),
        ("한계", "방어력 상성·특수 효과 실측 DPS·유틸 가치 미반영. MonteCarlo는 입력을 바꾸면 스크립트로 다시 생성해야 한다. 90일 가격은 직업 생산성 증가(growth)와 시세 식만 반영."),
        ("출처", "명세서 v0.1 7장(시세), 6장(강화), 9.3장(뽑기), 18장(균형), weapon-archetypes-spec.md, special-effects-spec.md, combat-spec.md"),
        ("예시 행", "Items 시트 하단에 새 품목 입력 형식 예시를 적어 두었다."),
    ]
    for i, (k, v) in enumerate(lines):
        put(ws, f"A{3+i}", k, "bold")
        put(ws, f"B{3+i}", v, "f", wrap=True)
        ws.row_dimensions[3 + i].height = 32
    widths(ws, {"A": 14, "B": 120})

    return wb, DASH, SNAP_HEAD_ROW


def read_mc_inputs(path):
    wb = load_workbook(path, data_only=True)
    en = wb["Enhance"]
    pm = wb["Params"]
    ga = wb["Gacha"]

    def col(c):
        return [en[f"{c}{r}"].value for r in range(6, 26)]

    def param(label):
        for row in pm.iter_rows(min_row=4, max_col=2):
            if row[0].value == label:
                return row[1].value
        raise KeyError(label)
    return {
        "s": col("E"), "k": col("F"), "d": col("G"), "c": col("K"),
        "start_price": param("장비 구매가(강화 시작 장비)"),
        "target_lv": param("목표 강화 단계(보스 진입)"),
        "g_common": ga["B5"].value, "g_rare": ga["B6"].value, "g_epic": ga["B7"].value, "g_legend": ga["B8"].value,
        "n_common": ga["C5"].value, "n_rare": ga["C6"].value, "n_epic": ga["C7"].value, "n_legend": ga["C8"].value,
        "pity": param("천장(영웅 이상 보장)"),
    }


def recalc(path, recalc_py):
    r = subprocess.run([sys.executable, str(recalc_py), str(path), "120"], capture_output=True, text=True)
    try:
        return json.loads(r.stdout.strip())
    except Exception:
        return {"error": r.stdout + r.stderr}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--recalc", default=str(DEFAULT_RECALC))
    ap.add_argument("--no-snapshot", action="store_true")
    ap.add_argument("--quick", action="store_true", help="난수 시행 횟수를 줄여 빠르게 생성")
    args = ap.parse_args()
    OUT.parent.mkdir(parents=True, exist_ok=True)

    # 1) 기본 시나리오를 먼저 계산해 입력값을 읽고 난수 시뮬레이션을 돌린다
    wb0, _, _ = build(1)
    tmp0 = OUT.parent / "_tmp_base.xlsx"
    wb0.save(tmp0)
    res0 = recalc(tmp0, args.recalc)
    if "error" in res0 or res0.get("status") != "success":
        print("recalc 문제(기본):", res0)
    vals = read_mc_inputs(tmp0)
    tmp0.unlink()
    mc = run_mc(vals, **({"n_enh": 8000, "n_first": 20000, "n_spec": 4000, "n_full": 500} if args.quick else {}))
    print("MC 완료: 목표 +%d 평균 %.0f, P90 %.0f" % (mc["target_level"], mc["enh"][mc["target_level"]]["mean"], mc["enh"][mc["target_level"]]["p90"]))

    gc = run_gacha_compare(vals, **({"n_main": 2000, "n_sens": 800} if args.quick else {}))
    print("뽑기 천장 비교 완료:", ", ".join("%s 지정전설 평균 %.0f" % (r["id"], r["spec"]["mean"]) for r in gc["rows"]))

    em = run_enh_mitigation(vals, **({"n_main": 2000, "n_sens": 800} if args.quick else {}))
    print("강화 완화 비교 완료:", ", ".join("%s +12 평균 %.0f" % (r["st"]["id"], r["stats"][12]["mean"]) for r in em["rows"]))

    snap = []
    if not args.no_snapshot:
        for idx in range(1, len(SCENARIOS) + 1):
            wb, dash, head_row = build(idx, mc, gc, em)
            tmp = OUT.parent / f"_tmp_s{idx}.xlsx"
            wb.save(tmp)
            res = recalc(tmp, args.recalc)
            if "error" in res or res.get("status") != "success":
                print("recalc 문제:", res)
            v = load_workbook(tmp, data_only=True)["Dashboard"]
            vals = []
            for r in dash["rows"]:
                pass
            vals = [v.cell(row=dash["first"] + i, column=3).value for i in range(len(dash["rows"]))]
            stat = [v.cell(row=dash["first"] + i, column=4).value for i in range(len(dash["rows"]))]
            snap.append((SCENARIOS[idx - 1][0], vals, stat))
            tmp.unlink()

    wb, dash, head_row = build(1, mc, gc, em)
    if snap:
        ws = wb["Scenarios"]
        labels = []
        wsD = wb["Dashboard"]
        for i in range(len(dash["rows"])):
            labels.append(wsD.cell(row=dash["first"] + i, column=1).value)
        put(ws, f"A{head_row}", "지표", "hdr")
        for j, (nm, vals, stat) in enumerate(snap):
            put(ws, f"{CL(2 + j)}{head_row}", nm, "hdr")
        ws.row_dimensions[head_row].height = 44
        fmts = [RATIO, RATIO, RATIO, RATIO, NUM1, NUM, NUM1, PCT, PCT, PCT, NUM, NUM1, RATIO, RATIO, PCT, PCT, NUM2, PCT]
        for i, lab in enumerate(labels):
            r = head_row + 1 + i
            put(ws, f"A{r}", lab, "label")
            for j, (nm, vals, stat) in enumerate(snap):
                c = put(ws, f"{CL(2 + j)}{r}", vals[i], "label", fmts[i] if i < len(fmts) else None)
        rr = head_row + 1 + len(labels)
        put(ws, f"A{rr}", "통과 항목 수", "bold")
        for j, (nm, vals, stat) in enumerate(snap):
            put(ws, f"{CL(2 + j)}{rr}", sum(1 for s in stat if s == "OK"), "label", "0")
        put(ws, f"A{rr+1}", f"※ 위 값은 스크립트가 각 시나리오를 재계산해 붙인 정적 스냅샷이다. 입력을 바꾸면 `python3 tools/g3_sheet/build_g3.py`로 다시 생성한다.", "note")
        for j in range(len(snap)):
            ws.column_dimensions[CL(2 + j)].width = 16
    wb.save(OUT)
    res = recalc(OUT, args.recalc)
    print(json.dumps(res, ensure_ascii=False))


if __name__ == "__main__":
    main()
