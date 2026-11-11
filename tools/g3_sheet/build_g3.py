#!/usr/bin/env python3
"""G3 경제·밸런스 시뮬레이션 워크북 생성기 (docs/G3-economy-simulation-sheet.md 구현).

출력 : data/g3/G3-economy-simulation.xlsx
사용 : python3 -I tools/g3_sheet/build_g3.py [--recalc /path/to/recalc.py] [--no-snapshot]

- 모든 계산은 엑셀 수식이다(결과값 하드코딩 없음). 입력은 파란 글씨.
- 시나리오 비교표(Scenarios의 스냅샷)만 스크립트가 시나리오별로 재계산해 붙인 **정적 값**이다.
- 모든 수치는 [제안]이며 실측으로 교체한다.
"""
import argparse
import json
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


# ---------- 빌드 ----------
def build(scenario_index=1):
    wb = Workbook()
    ws_leg = wb.active
    ws_leg.title = "Legend"
    names = ["Params", "Scenarios", "Items", "JobIncome", "PriceSim", "Enhance", "Gacha", "Housing_Sinks", "FlowBalance", "Weapons_DPS", "Effect_Packs", "Dashboard"]
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
    put(ws, f"C{D_LAST+2}", f'=COUNTIF(D{D_FIRST}:D{D_LAST},"OK")&" / "&COUNTA(D{D_FIRST}:D{D_LAST})&" 통과"', "f")
    put(ws, f"A{D_LAST+4}", "※ 미구현: 강화 비용 90% 분위(몬테카를로), 방어력 상성, 우클릭 특수 공격 DPS, 효과 포함 실측 DPS — G3 후속 과제.", "note")
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
        ("시트 구성", "Params · Scenarios · Items · JobIncome · PriceSim · Enhance · Gacha · Housing_Sinks · FlowBalance · Weapons_DPS · Effect_Packs · Dashboard"),
        ("읽는 순서", "Params → Items → PriceSim → JobIncome → Enhance/Gacha → Housing_Sinks → FlowBalance → Dashboard"),
        ("한계", "난수 시뮬레이션(강화 90% 분위, 뽑기 분포)은 미구현. 방어력 상성·특수 효과 실측 DPS 미반영. 90일 가격은 직업 생산성 증가(growth)와 시세 식만 반영."),
        ("출처", "명세서 v0.1 7장(시세), 6장(강화), 9.3장(뽑기), 18장(균형), weapon-archetypes-spec.md, special-effects-spec.md, combat-spec.md"),
        ("예시 행", "Items 시트 하단에 새 품목 입력 형식 예시를 적어 두었다."),
    ]
    for i, (k, v) in enumerate(lines):
        put(ws, f"A{3+i}", k, "bold")
        put(ws, f"B{3+i}", v, "f", wrap=True)
        ws.row_dimensions[3 + i].height = 32
    widths(ws, {"A": 14, "B": 120})

    return wb, DASH, SNAP_HEAD_ROW


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
    args = ap.parse_args()
    OUT.parent.mkdir(parents=True, exist_ok=True)

    snap = []
    if not args.no_snapshot:
        for idx in range(1, len(SCENARIOS) + 1):
            wb, dash, head_row = build(idx)
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

    wb, dash, head_row = build(1)
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
        fmts = [RATIO, RATIO, RATIO, RATIO, NUM1, NUM, NUM1, PCT, PCT, PCT, NUM, NUM1, RATIO, RATIO, PCT, PCT]
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
