# 근접 무기 아키타입 규격 v0.1

> 대상: 우리가 등록한 근접 무기 아이템(`combat-spec.md`)의 아키타입 6종. 쌍검(12장)과 같은 방식으로 정의한다.
> 연관: `combat-spec.md`(공격 정의 스키마), `fx-spec.md`(연출), `gearbridge-spec.md`(식별·강화), `G3-economy-simulation-sheet.md`(밸런스).
> 상태: **[제안]**. 모든 수치는 G3 시뮬레이션과 실측으로 확정한다. 이 문서의 목적은 아키타입별 **역할 차이와 데이터 골격**을 먼저 잡는 것이다.

## 1. 설계 원칙

1. **같은 티어에서 단일 대상 지속 피해량(DPS)을 비슷하게 맞춘다.** 차이는 **사거리·광역·기동·유틸·연출**에서 만든다(어떤 아키타입이 "정답"이 되지 않게).
2. **광역 능력이 큰 아키타입은 단일 대상 DPS를 약 10% 낮춘다**(광역 페널티).
3. **모션 없이 이펙트·판정 모양·템포로 정체성을 만든다**(`fx-spec.md`). 아키타입마다 호 모양, 소리 톤, 타격 효과가 다르다.
4. 강화(`k`)와 티어 배율은 **모든 아키타입에 동일**하게 적용해 아키타입 간 격차가 강화 단계에서 벌어지지 않게 한다(`combat-spec.md` 11장 `base_damage` 산식).
5. 새 메커니즘은 최소화한다. 1차는 `factor`, `knockback`, `cooldown`, `delay`, `hitbox`, `movement`, `max_targets`만 쓰고, 확장 필드는 `crit_multiplier`(도끼)와 `backstab_multiplier`(단검, 선택) 두 가지만 추가한다.
6. 직업 도구(곡괭이·낚싯대·식칼 등)와 농부의 낫은 **이 체계에 포함하지 않는다**(직업 장비, 명세 4.2·5.1장).

## 2. 한눈에 보기

| 아키타입 | `archetype` | 아이템(안) | 손 | 역할 | 사거리 | 판정 | 대상 수 | 템포 |
|---|---|---|---|---|---|---|---|---|
| 한손검 | `one_hand_sword` | `economycore:gear_sword` | 1 | 만능, 기준점 | 3.5 | 원뿔 40° | 4 | 중간 |
| 단검 | `dagger` | `economycore:gear_sword` | 1 | 빠른 연타, 후방 공격 | 2.6 | 원뿔 35° | 2 | 매우 빠름 |
| 쌍검 | `dual_blade` | `economycore:gear_sword` | 2 | 연타, 교차 마무리 | 3.0 | 부채꼴 35~80° | 3~4 | 빠름(4연타) |
| 대검 | `greatsword` | `economycore:gear_sword` | 1 | 광역·넉백, 느림 | 4.0 | 원뿔 70° | 8 | 느림 |
| 창 | `spear` | `economycore:gear_polearm` | 1 | 긴 사거리 직선 관통 | 4.5 | 직선(OBB) | 3 | 중간 |
| 도끼 | `axe` | `economycore:gear_axe` | 1 | 높은 한 방, 치명타 | 3.2 | 원뿔 45° | 2 | 중간~느림 |

- 아이템은 카테고리별로 등록한다(`combat-spec.md` 2.1): 검 계열 4종은 `gear_sword`, 창은 `gear_polearm`, 도끼는 `gear_axe`. 구분은 `def_id`와 `archetype`으로 한다. **아이템 분할은 모델·렌더 차이와 도감 분류 때문이며, 필요하면 GB0에서 합칠 수 있다.**
- 도감 범위(명세 6.3장)에서는 검 계열(한손검·대검·단검·쌍검)을 "검"으로, 창·도끼를 "기타 근접"으로 둘지 별도 범주로 둘지 결정한다(8장 미확정).

## 3. 밸런스 기준

### 3.1 지속 단일 대상 DPS 지표

```text
DPS_single = base_damage × Σ(factor_i) / (Σ(cooldown_i) / 20)      # 좌공격 콤보 1사이클 기준
```

- 기준: **티어 1·강화 0에서 DPS_single ≈ 9.7 ± 5%** (광역 아키타입은 -10%).
- 우클릭 특수 공격은 **쿨다운이 길고 DPS가 아니라 상황 대응용**(돌진, 광역, 넉백)이라 지표에서 제외한다. 특수 공격이 지속 DPS를 앞지르지 않게 `factor/cooldown`이 좌콤보 평균보다 높지 않도록 점검한다.
- `tier_multiplier`와 `k`는 공통이므로 같은 티어·강화에서 비율이 유지된다.

### 3.2 초기 수치 후보와 검산

| 아키타입 | `base_damage` | 좌콤보 `factor` | 좌콤보 `cooldown`(tick) | Σfactor | Σcooldown | DPS_single |
|---|---|---|---|---|---|---|
| 한손검 | 6.0 | 1.0, 0.8 | 12, 10 | 1.8 | 22 | 9.82 |
| 단검 | 3.0 | 1.0, 1.0, 1.3 | 6, 6, 8 | 3.3 | 20 | 9.90 |
| 쌍검 | 4.0 | 1.0, 1.0, 1.1, 1.5 | 7, 7, 8, 16 | 4.6 | 38 | 9.68 |
| 창 | 6.8 | 1.0, 1.0 | 14, 14 | 2.0 | 28 | 9.71 |
| 도끼 | 8.8 | 1.0, 1.1 | 18, 20 | 2.1 | 38 | 9.73 |
| 대검 (광역 -10%) | 10.0 | 1.0, 1.2 | 22, 28 | 2.2 | 50 | 8.80 |

(계산: `DPS = base × Σfactor ÷ (Σcooldown ÷ 20)`. 모두 제안값이며 크리티컬·콤보 리셋·시전 지연(`delay`)·이동은 반영하지 않은 단순 지표다. 실측 후 보정.)

## 4. 아키타입별 정의

공통 스키마는 `combat-spec.md` 3장·12장. 아래 YAML은 핵심 필드만 보인다.

### 4.1 한손검 (`one_hand_sword`) — 기준점

- **역할:** 모든 무기의 기준. 특별한 약점도 강점도 없는 균형형. 입문용.
- **판정:** 원뿔, 사거리 3.5, 반각 40°(좌) / 85°(우).
- **연출 정체성:** 사선 베기 호(약간 위에서 아래로), 금속성 가벼운 소리, 흰색·푸른 불꽃 튀김.

```yaml
gear_def:
  archetype: one_hand_sword
  hands: 1
  base_damage: 6.0
  attack:
    attack_left:
      - { factor: 1.0, knockback: 0.05, cooldown: 12, delay: 0, hitbox: { type: cone, max_range: 3.5, max_angle: 40 }, max_targets: 4 }
      - { factor: 0.8, knockback: 0.05, cooldown: 10, delay: 0, hitbox: { type: cone, max_range: 3.5, max_angle: 50 }, max_targets: 4 }
    attack_right: { factor: 1.5, knockback: 0.10, cooldown: 26, delay: 2, hitbox: { type: cone, max_range: 3.5, max_angle: 85 }, movement: { delay: 0, speed: 0.5 }, max_targets: 6 }
  combo: { reset_ticks: 30 }
```

### 4.2 단검 (`dagger`) — 속도와 후방 공격

- **역할:** 가장 빠른 연타, 짧은 사거리, 이동 중 접근전. 후방 공격 보너스(선택 확장)로 위치 선정 보상.
- **판정:** 원뿔, 사거리 2.6, 반각 35°. 대상 수 2.
- **특수:** `backstab_multiplier`(선택): 서버가 공격자가 대상의 **뒤쪽 반구**에 있음을 계산해(대상 시선과 공격 방향의 각도) 피해를 가중(예: ×1.3). 보스·특정 대상은 정의별로 예외 가능. `[결정 필요: 도입 여부, PvP 정책과 연동]`
- **우클릭:** 짧은 돌진 찌르기(차오름 기동기).
- **연출 정체성:** 짧은 직선 번쩍임, 높고 빠른 소리, 작고 선명한 불꽃.

```yaml
gear_def:
  archetype: dagger
  hands: 1
  base_damage: 3.0
  backstab_multiplier: 1.3         # 선택
  attack:
    attack_left:
      - { factor: 1.0, knockback: 0.02, cooldown: 6, delay: 0, hitbox: { type: cone, max_range: 2.6, max_angle: 35 }, max_targets: 2 }
      - { factor: 1.0, knockback: 0.02, cooldown: 6, delay: 0, hitbox: { type: cone, max_range: 2.6, max_angle: 35 }, max_targets: 2 }
      - { factor: 1.3, knockback: 0.05, cooldown: 8, delay: 0, hitbox: { type: cone, max_range: 2.6, max_angle: 45 }, max_targets: 2 }
    attack_right: { factor: 1.6, knockback: 0.04, cooldown: 22, delay: 1, hitbox: { type: cone, max_range: 2.8, max_angle: 30 }, movement: { delay: 0, speed: 0.7 }, max_targets: 1 }
  combo: { reset_ticks: 18 }
```

### 4.3 쌍검 (`dual_blade`) — 4연타와 교차 마무리

- 정의는 `combat-spec.md` 12장(1세트=아이템 1개, `hands: 2`, 오프핸드 점유 금지). **`base_damage`는 이 문서의 검산에 맞춰 4.0으로 보정**한다(12장 예시의 3.2는 보정 전 값).
- **연출 정체성:** 좌우 손에서 번갈아 시작하는 호, 마무리는 X자 교차, 가벼운 연속 금속음.

### 4.3.1 쌍검 정의 (요약)

```yaml
gear_def:
  archetype: dual_blade
  hands: 2
  base_damage: 4.0
  attack:
    attack_left:     # hand 번갈아, 4번째는 both (combat-spec.md 12.2 참조)
      - { hand: right, factor: 1.0, cooldown: 7 }
      - { hand: left,  factor: 1.0, cooldown: 7 }
      - { hand: right, factor: 1.1, cooldown: 8 }
      - { hand: both,  factor: 1.5, cooldown: 16, delay: 1 }
    attack_right: { hand: both, factor: 1.6, cooldown: 24, delay: 2, movement: { delay: 0, speed: 0.6 } }
```

### 4.4 대검 (`greatsword`) — 광역과 넉백

- **역할:** 느리지만 넓은 광역과 큰 넉백. 다수 대상에 강하고 단일 대상 DPS는 광역 페널티(-10%). 접근을 허용하면 위험한 대신 군중 제어에 강하다.
- **판정:** 원뿔, 사거리 4.0, 반각 70°. 대상 수 8.
- **우클릭:** 내려찍기. 지연이 길고(8틱) 넉백이 크다. 아군 오사(PvP 구역) 시 주의.
- **연출 정체성:** 넓은 반원 호, 묵직한 낮은 소리, 타격 시 먼지·충격파 파티클.

```yaml
gear_def:
  archetype: greatsword
  hands: 1
  base_damage: 10.0
  attack:
    attack_left:
      - { factor: 1.0, knockback: 0.20, cooldown: 22, delay: 3, hitbox: { type: cone, max_range: 4.0, max_angle: 70 }, max_targets: 8 }
      - { factor: 1.2, knockback: 0.25, cooldown: 28, delay: 4, hitbox: { type: cone, max_range: 4.0, max_angle: 80 }, max_targets: 8 }
    attack_right: { factor: 2.4, knockback: 0.45, cooldown: 40, delay: 8, hitbox: { type: cone, max_range: 4.5, max_angle: 120 }, max_targets: 8 }
  combo: { reset_ticks: 40 }
```

### 4.5 창 (`spear`) — 사거리와 직선 관통

- **역할:** 가장 긴 사거리(4.5), 직선 위의 여러 대상을 관통. 근접전 회피에 유리하고 측면 대응이 약하다.
- **판정:** OBB(직선 폭 0.4, 높이 0.5). 대상 수 3(직선상 거리순).
- **우클릭:** 돌진 찌르기(긴 사거리 돌진, 지연 3틱).
- **연출 정체성:** 직선 관통 파티클, 바람 가르는 낮은 소리, 타격점에서 가느다란 잔광.

```yaml
gear_def:
  archetype: spear
  hands: 1
  base_damage: 6.8
  attack:
    attack_left:
      - { factor: 1.0, knockback: 0.05, cooldown: 14, delay: 1, hitbox: { type: obb, max_range: 4.5, half_width: 0.4, half_height: 0.5 }, max_targets: 3 }
      - { factor: 1.0, knockback: 0.05, cooldown: 14, delay: 1, hitbox: { type: obb, max_range: 4.5, half_width: 0.4, half_height: 0.5 }, max_targets: 3 }
    attack_right: { factor: 1.6, knockback: 0.12, cooldown: 30, delay: 3, hitbox: { type: obb, max_range: 5.0, half_width: 0.5, half_height: 0.5 }, movement: { delay: 0, speed: 0.9 }, max_targets: 3 }
  combo: { reset_ticks: 28 }
```

### 4.6 도끼 (`axe`) — 한 방과 치명타

- **역할:** 한 방이 강하고 치명타 배율이 높다(`crit_multiplier` 1.8, 기본 1.5). 연타·사거리·광역은 보통 이하. 점프 크리티컬 조건(`combat-spec.md` 11장 1번)을 활용하는 플레이가 보상받는다.
- **판정:** 원뿔, 사거리 3.2, 반각 45°. 대상 수 2.
- **우클릭:** 내려치기(넉백, 짧은 시전). 
- **연출 정체성:** 위에서 아래로 내려찍는 호, 둔탁한 소리, 타격 시 파편·먼지 파티클.

```yaml
gear_def:
  archetype: axe
  hands: 1
  base_damage: 8.8
  crit_multiplier: 1.8             # 확장 필드 (기본 1.5)
  attack:
    attack_left:
      - { factor: 1.0, knockback: 0.10, cooldown: 18, delay: 2, hitbox: { type: cone, max_range: 3.2, max_angle: 45 }, max_targets: 2 }
      - { factor: 1.1, knockback: 0.12, cooldown: 20, delay: 2, hitbox: { type: cone, max_range: 3.2, max_angle: 50 }, max_targets: 2 }
    attack_right: { factor: 1.9, knockback: 0.30, cooldown: 32, delay: 4, hitbox: { type: cone, max_range: 3.4, max_angle: 60 }, max_targets: 3 }
  combo: { reset_ticks: 32 }
```

## 5. 이펙트 세트 매핑 (`fx-spec.md`)

| 아키타입 | 기본 `fx_set` | 호 모양 | 핵심 파티클/소리 톤 |
|---|---|---|---|
| 한손검 | `fx_sword_basic` | 사선 베기 | 금속성 가벼움, 불꽃 |
| 단검 | `fx_dagger_basic` | 짧은 직선 | 높고 빠름, 작은 불꽃 |
| 쌍검 | `fx_dual_basic` | 좌/우 번갈아 + X 교차 | 연속 금속음 |
| 대검 | `fx_greatsword_basic` | 넓은 반원 | 낮고 묵직, 먼지·충격파 |
| 창 | `fx_spear_basic` | 직선 관통 | 바람 소리, 잔광 |
| 도끼 | `fx_axe_basic` | 위→아래 내려찍기 | 둔탁함, 파편 |

- 티어·강화 단계에 따라 효과 세트가 확장된다(오라는 `enhance_level ≥ 5`, `fx-spec.md` 11장 8번).

## 6. 상성과 약점 요약

| 아키타입 | 강점 | 약점 |
|---|---|---|
| 한손검 | 균형, 약점 없음 | 특화 부재 |
| 단검 | 속도, 후방 공격, 이동성 | 짧은 사거리, 낮은 광역 |
| 쌍검 | 연타, 마무리 광역 | 타당 피해 낮음(방어력 높은 대상에 약함) |
| 대검 | 광역, 넉백 | 느림, 단일 DPS 낮음 |
| 창 | 사거리, 직선 관통 | 측면·근접 대응 약함 |
| 도끼 | 한 방, 치명타 | 사거리·연타 보통 이하 |

- **방어력이 높은 대상에는 타당 피해가 큰 도끼·대검이 유리하고, 타당 피해가 낮은 단검·쌍검은 방어 감소폭이 커진다.** 이 상성은 바닐라 방어 공식에 따라 자연스럽게 생기며, 보스 방어력 설계(명세 11장)와 함께 G3에서 확인한다.

## 7. 구현·검수 항목

- [ ] 같은 티어·강화 0에서 지속 단일 DPS 지표가 3.2의 허용 범위 안이다(광역은 -10%).
- [ ] 강화 단계가 올라가도 아키타입 간 DPS 비율이 유지된다(공통 `k`).
- [ ] 각 아키타입의 판정 모양이 정의와 일치한다(원뿔/OBB/부채꼴, 사거리·각도).
- [ ] 대검의 대상 수 8, 창의 직선 관통(거리순 3), 단검의 2가 상한을 지킨다.
- [ ] 도끼 `crit_multiplier`가 점프 크리티컬에서만 적용된다.
- [ ] 단검 `backstab_multiplier`(도입 시)가 서버 계산이며 위조할 수 없다.
- [ ] 아키타입별 효과 세트가 데이터만으로 교체되고 `hand`/호 모양이 정의대로 나온다.
- [ ] 방어력 높은 대상에서 아키타입 간 실효 DPS 차이가 허용 범위 안이다(G3).
- [ ] 쌍검의 오프핸드 규칙이 다른 아키타입에는 영향이 없다.

## 8. 미확정

1. `backstab_multiplier` 도입 여부와 PvP 정책 연동
2. 도감 분류(검 계열 vs 창·도끼를 어디에 둘지)
3. 아이템 분할(`gear_sword`/`gear_polearm`/`gear_axe`)을 유지할지 하나로 합칠지(GB0)
4. 추가 후보 아키타입: 곡도, 레이피어, 해머, 지팡이류(원거리·마법은 범위 밖). 필요 시 같은 스키마로 추가
5. 우클릭 특수 공격의 쿨다운·위력(상황 대응용 상한 설정)
6. 방어력 높은 대상 상성(G3 시뮬레이션과 보스 설계)
7. 아키타입별 `tier_multiplier` 차등 여부(1차는 공통)
