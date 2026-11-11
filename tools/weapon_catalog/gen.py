#!/usr/bin/env python3
"""근접 무기 카탈로그 생성기 + DPS 균형 검증.

입력 : data/weapon_catalog/{archetypes,themes,uniques}.json
출력 : data/weapon_catalog/weapons.json   (압축 카탈로그: 아키타입+변형 참조)
       docs/weapon-catalog-list.md         (전체 목록 표)
옵션 : --expand <def_id>   해당 무기의 완전한 gear_def(공격 정의 전체)를 JSON으로 출력
       --check             생성 없이 검증만 수행
       --only-archetype X  해당 아키타입만 출력/검증
모든 수치는 [제안]. 표준 라이브러리만 사용.
"""
import argparse
import json
import math
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "weapon_catalog"
DOCS = ROOT / "docs"
DPS_TOLERANCE = 0.03  # 템플릿 대비 허용 오차(반올림 영향)


def load(name):
    with open(DATA / name, encoding="utf-8") as f:
        return json.load(f)


def sums(left, cooldown_scale=1.0):
    sf = sum(h["factor"] for h in left)
    sc = sum(max(4, round(h["cooldown"] * cooldown_scale)) for h in left)
    return sf, sc


def dps(base, left, cooldown_scale=1.0):
    sf, sc = sums(left, cooldown_scale)
    return base * sf / (sc / 20.0)


def template_base(arch, cfg):
    """base_damage가 null이면 target DPS에 맞춰 계산."""
    if arch.get("base_damage") is not None:
        return arch["base_damage"]
    target = cfg["target_dps_aoe"] if arch["aoe"] else cfg["target_dps"]
    sf, sc = sums(arch["left"])
    return round(target * (sc / 20.0) / sf, 2)


def variant_base(arch, tbase, scale):
    """변형(쿨다운 배율)에서 DPS가 유지되도록 base를 보정."""
    _, sc0 = sums(arch["left"], 1.0)
    _, sc1 = sums(arch["left"], scale)
    return round(tbase * (sc1 / sc0), 2)


def pick_variant(arch_id, theme_key, default):
    """테마 기본 변형을 따르되, 같은 테마 안에서 아키타입별로 일부 변형을 섞는다(결정적)."""
    h = zlib.crc32(f"{arch_id}:{theme_key}".encode()) % 5
    if h == 0:
        return {"balanced": "swift", "swift": "heavy", "heavy": "balanced"}[default]
    return default


def expand(arch, tbase, variant_name, variants):
    scale = variants[variant_name]["cooldown_scale"]
    base = variant_base(arch, tbase, scale)

    def scaled(hit):
        out = dict(hit)
        out["cooldown"] = max(4, round(hit["cooldown"] * scale))
        return out

    d = {
        "archetype": arch["id"],
        "hands": arch["hands"],
        "base_damage": base,
        "attack": {
            "attack_left": [scaled(h) for h in arch["left"]],
            "attack_right": scaled(arch["right"]),
        },
        "combo": {"reset_ticks": arch["combo_reset"]},
    }
    if arch.get("extras"):
        d.update(arch["extras"])
    return d


def build(cfg_a, cfg_t, cfg_u, only=None):
    archs = {a["id"]: a for a in cfg_a["archetypes"]}
    tiers = cfg_t["tiers"]
    variants = cfg_t["variants"]
    themes = cfg_t["themes"]
    weapons = []
    problems = []

    tbases = {aid: template_base(a, cfg_a) for aid, a in archs.items()}

    for aid, a in archs.items():
        if only and aid != only:
            continue
        for th in themes:
            vname = pick_variant(aid, th["key"], th["variant"])
            base = variant_base(a, tbases[aid], variants[vname]["cooldown_scale"])
            tier = th["tier"]
            def_id = f"{aid}_{th['key']}"
            parent = f"{aid}_{th['from']}" if th["from"] else None
            weapons.append({
                "def_id": def_id,
                "name_ko": f"{th['name']} {a['name_ko']}",
                "archetype": aid,
                "item": a["item"],
                "hands": a["hands"],
                "tier": tier,
                "rarity": tiers[str(tier)]["rarity"],
                "theme": th["key"],
                "variant": vname,
                "base_damage": base,
                "fx_set": [a["fx_base"], f"fx_theme_{th['overlay']}"],
                "bind_policy": tiers[str(tier)]["bind"],
                "evolves_from": parent,
                "acquire": th["acquire"],
                "unique": False,
                "status": "candidate",
            })

    for u in cfg_u["uniques"]:
        aid = u["archetype"]
        if only and aid != only:
            continue
        a = archs[aid]
        vname = u["variant"]
        base = variant_base(a, tbases[aid], variants[vname]["cooldown_scale"])
        tier = u["tier"]
        weapons.append({
            "def_id": f"{aid}_unique_{u['key']}",
            "name_ko": u["name"],
            "archetype": aid,
            "item": a["item"],
            "hands": a["hands"],
            "tier": tier,
            "rarity": tiers[str(tier)]["rarity"],
            "theme": f"unique:{u['key']}",
            "variant": vname,
            "base_damage": base,
            "fx_set": [a["fx_base"], f"fx_theme_{u['overlay']}", f"fx_unique_{u['key']}"],
            "bind_policy": "bind_on_acquire",
            "evolves_from": None,
            "acquire": u["acquire"],
            "unique": True,
            "flavor": u["flavor"],
            "status": "candidate",
        })

    # --- 검증 ---
    ids = set()
    for w in weapons:
        if w["def_id"] in ids:
            problems.append(f"중복 def_id: {w['def_id']}")
        ids.add(w["def_id"])
    for w in weapons:
        if w["evolves_from"] and w["evolves_from"] not in ids and not only:
            problems.append(f"진화 부모 없음: {w['def_id']} <- {w['evolves_from']}")
        a = archs[w["archetype"]]
        scale = variants[w["variant"]]["cooldown_scale"]
        actual = dps(w["base_damage"], a["left"], scale)
        ref = dps(tbases[w["archetype"]], a["left"], 1.0)
        w["_dps_ratio"] = actual / ref
        if abs(actual / ref - 1.0) > DPS_TOLERANCE:
            problems.append(f"DPS 편차 {actual/ref:.3f}: {w['def_id']}")

    # 진화 분기 수(노드당 자식 최대 2)
    children = {}
    for w in weapons:
        if w["evolves_from"]:
            children.setdefault(w["evolves_from"], []).append(w["def_id"])
    for p, c in children.items():
        if len(c) > 2:
            problems.append(f"진화 분기 초과({len(c)}): {p}")

    # 아키타입 간 DPS 범위
    summary = {}
    for aid, a in archs.items():
        if only and aid != only:
            continue
        summary[aid] = {
            "template_base": tbases[aid],
            "template_dps": round(dps(tbases[aid], a["left"]), 2),
            "aoe": a["aoe"],
        }
    return weapons, summary, problems


def apply_selection(weapons):
    """selection.json의 approved/rejected 목록으로 status를 갱신한다(없으면 전부 candidate)."""
    path = DATA / "selection.json"
    if not path.exists():
        return
    with open(path, encoding="utf-8") as f:
        sel = json.load(f)
    approved = set(sel.get("approved", []))
    rejected = set(sel.get("rejected", []))
    for w in weapons:
        if w["def_id"] in rejected:
            w["status"] = "rejected"
        elif w["def_id"] in approved:
            w["status"] = "approved"


def write_outputs(weapons, summary, cfg_t):
    apply_selection(weapons)
    approved = [w for w in weapons if w["status"] == "approved"]
    if approved:
        with open(DATA / "weapons_approved.json", "w", encoding="utf-8") as f:
            json.dump({"count": len(approved),
                       "weapons": [{k: v for k, v in w.items() if not k.startswith("_")} for w in approved]},
                      f, ensure_ascii=False, indent=1)
            f.write("\n")
    clean = []
    for w in weapons:
        c = {k: v for k, v in w.items() if not k.startswith("_")}
        clean.append(c)
    out = {
        "_comment": "자동 생성(tools/weapon_catalog/gen.py). 수정하지 말고 입력 JSON을 고친 뒤 다시 생성한다. 수치는 [제안].",
        "tier_multiplier": {k: v["multiplier"] for k, v in cfg_t["tiers"].items()},
        "count": len(clean),
        "weapons": clean,
    }
    with open(DATA / "weapons.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")

    lines = ["# 근접 무기 카탈로그 전체 목록 (자동 생성)", "",
             "> `tools/weapon_catalog/gen.py`가 생성. 직접 수정하지 말 것. 수치는 [제안], 모든 항목은 `candidate`(후보)이다.",
             f"> 총 {len(clean)}종.", "",
             "| def_id | 이름 | 아키타입 | 티어 | 등급 | 변형 | base_damage | 진화 부모 | 획득 | 귀속 |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for w in clean:
        lines.append("| {def_id} | {name_ko} | {archetype} | T{tier} | {rarity} | {variant} | {base_damage} | {evolves_from} | {acquire} | {bind_policy} |".format(
            **{**w, "evolves_from": w["evolves_from"] or "-"}))
    (DOCS / "weapon-catalog-list.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--expand")
    ap.add_argument("--only-archetype")
    args = ap.parse_args()

    cfg_a, cfg_t, cfg_u = load("archetypes.json"), load("themes.json"), load("uniques.json")
    weapons, summary, problems = build(cfg_a, cfg_t, cfg_u, args.only_archetype)

    if args.expand:
        w = next((x for x in weapons if x["def_id"] == args.expand), None)
        if not w:
            print(f"def_id 없음: {args.expand}", file=sys.stderr)
            return 2
        archs = {a["id"]: a for a in cfg_a["archetypes"]}
        a = archs[w["archetype"]]
        tb = template_base(a, cfg_a)
        d = expand(a, tb, w["variant"], cfg_t["variants"])
        d.update({"def_id": w["def_id"], "name_ko": w["name_ko"], "tier": w["tier"], "fx_set": w["fx_set"],
                  "bind_policy": w["bind_policy"], "provenance": "original"})
        print(json.dumps(d, ensure_ascii=False, indent=2))
        return 0

    ratios = [w["_dps_ratio"] for w in weapons]
    print(f"무기 {len(weapons)}종 / 아키타입 {len(summary)}종")
    for aid, s in summary.items():
        print(f"  {aid:16s} base={s['template_base']:<6} template_dps={s['template_dps']:<5} aoe={s['aoe']}")
    print(f"템플릿 대비 DPS 비율: min={min(ratios):.3f} max={max(ratios):.3f} (허용 ±{DPS_TOLERANCE})")
    if problems:
        print("문제 발견:")
        for p in problems:
            print("  -", p)
        return 1
    print("검증 통과")
    if not args.check:
        write_outputs(weapons, summary, cfg_t)
        print("생성: data/weapon_catalog/weapons.json, docs/weapon-catalog-list.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
