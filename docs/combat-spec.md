# 자체 근접 전투(`combat`) 규격 v0.1 — 신규 아이템 + 서버 권위 범위 공격

> 결정(2026-11-11): ① 검은 **우리가 등록하는 새 아이템**으로 만든다(바닐라 아이템에 컴포넌트를 붙이는 방식 폐기). ② **범위 공격을 직접 구현**한다. 바닐라 백엔드(GB-5)의 실체가 이 문서다.
> 연관: `gearbridge-spec.md`(식별·강화), `fx-spec.md`(연출), `server-core-mod-spec.md`(코어), `melee-system-findings.md`(LR 분석, 필드 호환 참고).
> 상태: **[제안]**. 클래스·이벤트 이름은 후보이며 NeoForge 1.21.1 실제 코드로 확인한다. `[확인 필요]`는 후속 검증 항목.

## 1. 목표와 원칙

1. **서버 권위**: 대상 선정·피해·쿨다운을 서버가 계산한다. 클라이언트는 **"공격 의도"만** 보낸다(대상 목록 전송 없음) → LR의 클라이언트 신뢰 문제(`guard.melee` T1~T6)가 구조적으로 사라진다.
2. **LR 이식 호환 스키마**: 공격 정의 필드를 LR 근접 데이터와 같은 이름·의미로 맞춘다(`factor`, `knockback`, `cooldown`, `delay`, `hitbox`, `movement`). 정의 데이터를 변환해 LR 백엔드로 옮길 수 있다. **LR 코드는 복사하지 않고 구현은 직접 작성**한다.
3. **바닐라 피해 파이프라인 사용**: 피해는 바닐라 `hurt` 경로를 거쳐 방어구·인챈트·피해 이벤트·무적 시간과 호환된다.
4. **데이터 기반**: 무기 정의는 JSON(핫리로드). 새 무기를 코드 없이 추가한다.
5. **이펙트 연동**: `SWING/HIT/CRIT/KILL`을 `GearActionEvent`로 발행해 `fx`가 소비한다(`fx-spec.md`).

## 2. 신규 아이템

### 2.1 구조

- 카테고리별 **새 아이템을 등록**한다. 1차: `economycore:gear_sword`(근접 무기). 무기 종류(정의)는 데이터 컴포넌트 `economycore:gear`의 `def_id`로 구분한다 — 새 무기를 추가할 때 코드·재시작 없이 데이터만 추가하기 위함.
- 식별 키: **`gear_key = (item_id, def_id)`**. 개별 식별: `serial`(코어 `guard.identity`, 컴포넌트 `economycore:identity`).
- 레지스트리 수는 카테고리 수만큼만 늘어난다(무기마다 아이템을 등록하지 않음). 무기마다 아이템을 등록하는 방식은 키가 더 단순하지만 정의 추가에 코드 배포가 필요해 채택하지 않는다. `[GB0에서 재확인]`

### 2.2 컴포넌트 (제안)

| 컴포넌트 | 내용 |
|---|---|
| `economycore:gear` | `def_id`, `tier`, `enhance_level`, `evolution_id` (표시·캐시, 정본은 DB) |
| `economycore:identity` | `serial`, `owner`, `issued_event`, `issued_at` (코어) |
| 바닐라 `unbreakable` | 무한 내구도 |

### 2.3 외형

- 무기 모델·텍스처는 우리 에셋이다. `def_id`·강화 단계에 따라 모델이 달라지게 하려면 아이템 모델 오버라이드(1.21.1의 `custom_model_data` 컴포넌트 predicate 또는 클라이언트 동적 모델) 중 하나를 쓴다. `[확인 필요: 어느 쪽이 정의 추가에 코드가 필요 없는지]`
- 에셋은 모두 `provenance` 기록. TaCZ·LR 에셋은 사용하지 않는다.

### 2.4 바닐라 동작 차단

- 이 아이템을 든 상태의 **바닐라 공격은 취소**한다(서버: 공격 이벤트 취소, 피해는 우리 모듈만 발생). 바닐라 휩쓸기·기본 공격 쿨다운·블록 파괴 보너스가 중복되지 않게 한다.
- **블록 좌클릭(채굴)**: 기본은 무기로 블록을 부수지 않는다(`combat.block_break: false`). 건축·채굴 정책(명세 3.1장 화이트리스트)과 맞춘다. `[정책 결정]`
- 제작·수리·인챈트는 코어(`guard.recipe`, `guard.craft`)가 차단한다. 우리 아이템은 레시피가 없고 **상점·보상·강화 서비스로만 발급**한다(명세 1.1장).

## 3. 공격 정의 (데이터)

```yaml
gear_def:
  def_id: "sword_iron_01"
  category: "sword"
  provenance: "original"
  base_damage: 6.0            # 기본 피해 (강화·티어가 가산/배율 적용)
  draw_time: 10               # tick
  put_away_time: 6
  attack:
    attack_left:              # 객체 1개 또는 배열(콤보 순환)
      - { factor: 1.0, knockback: 0.05, cooldown: 12, delay: 0,
          hitbox: { type: cone, max_range: 3.5, max_angle: 40 }, max_targets: 4 }
      - { factor: 0.8, knockback: 0.05, cooldown: 10, delay: 0,
          hitbox: { type: cone, max_range: 3.5, max_angle: 50 }, max_targets: 4 }
    attack_right:
      factor: 1.5
      knockback: 0.10
      cooldown: 26
      delay: 2
      hitbox: { type: cone, max_range: 3.5, max_angle: 85 }
      movement: { delay: 0, speed: 0.5 }     # 돌진(선택)
      max_targets: 6
  combo:
    reset_ticks: 30           # 마지막 공격 후 이 시간이 지나면 콤보 인덱스 초기화
  fx_set: "fx_iron_basic"     # fx-spec.md
```

- 필드 이름은 LR 근접 데이터와 호환되게 유지한다(이식 변환 용이). `hitbox.type`은 `cone`, `obb`, `arc`(부채꼴 호 — 이펙트 호와 같은 기하)를 지원한다.
- `max_targets`, `combo.reset_ticks`, `fx_set`은 우리 확장 필드다.
- 수치는 모두 [제안]이며 G3 시뮬레이션과 실측으로 확정한다.

## 4. 공격 흐름 (서버 권위)

```text
[클라이언트] 좌/우 클릭 입력 → C2SAttackIntent{action, seq}  (대상·위치·시선 값은 보내지 않음)
[서버] 수신:
   1. 플레이어가 GearItem을 메인핸드에 들고 있고, 꺼내기(draw) 중이 아니며 serial 상태가 active인가
   2. 서버 쿨다운(cooldown_tick)이 0인가, seq가 중복·역행이 아닌가
   3. action/combo_index 결정 (콤보 배열 인덱스, reset_ticks 반영)
   4. 쿨다운 설정, delay 틱 예약 → GearActionEvent(SWING) 발행 (fx)
[서버] delay 경과 시점(틱):
   5. 서버 값(눈 위치·시선)으로 대상 후보 계산: hitbox 필터(cone/obb/arc) + 시야(LOS) 검사 + 팀/무적 필터
   6. 대상 정렬(거리/각도) 후 max_targets 적용
   7. 피해 계산·적용 → HIT/CRIT/KILL 이벤트 발행
   8. 돌진(movement)이 있으면 delay 후 이동 적용
```

- **클라이언트 입력 위조 시 최대 영향**은 "공격 의도를 더 자주 보내는 것"뿐이며 서버 쿨다운이 막는다. 대상은 항상 서버가 정한다.
- 서버 틱 단위로 처리되므로 `delay`는 서버가 강제한다(LR과 달리 클라이언트에 의존하지 않음).

### 4.1 피해 계산

```text
damage = base_damage(def, tier, enhance_level) × action.factor × combo_multiplier(선택)
       + 인챈트 보정(EnchantmentHelper.modifyDamage 계열)
       × crit_multiplier (조건 충족 시)
```

- **피해를 공격자의 공격력 속성에 의존시키지 않는다**(LR의 `ATTACK_DAMAGE × factor` 방식과 다름). 강화 단계는 `base_damage` 계산식(`GearBridge.applyStats` 대체)에서 직접 반영하므로, 강화→스탯 반영 방식에 대한 LR 속성 수정자 불확실성이 사라진다. 힘 효과 등 바닐라 보정을 허용할지는 설정(`combat.apply_player_attributes`).
- `base_damage(def, tier, enhance_level)`의 산식과 강화 곡선은 G3와 `gearbridge-spec.md`에서 확정한다.
- 크리티컬: 바닐라 점프 크리티컬 조건을 재사용하거나 정의별 확률형으로 선택(`[결정 필요]`). 서버가 판정한다.
- 피해 적용: 바닐라 `hurt`(공격자 피해원)를 통해 방어구·피해 이벤트·무적 시간과 호환. 다단 히트가 무적 시간에 막히지 않도록 **무적 시간 임계 설정**(`combat.ignore_invulnerable_below_ticks`)을 둔다(LR 방식 참고, 직접 구현).
- 넉백: 공격 방향 기준 바닐라 넉백 API 사용, `knockback` 값 반영.
- 내구도: 무한(소모 없음).

### 4.2 범위 판정 기하

- **cone**: 눈 위치에서 시선 방향으로 `max_range` 거리·`max_angle` 반각 안의 엔티티(바운딩 박스 중심 또는 가장 가까운 점 기준 `[확인 필요]`).
- **obb**: 시선 방향으로 늘린 직육면체(`max_range`, `half_width`, `half_height`, `roll`).
- **arc**: 수평 부채꼴(원뿔과 유사하나 상하 두께 제한) — 이펙트의 `particle_arc`와 **같은 기하 함수**를 공유해 시각과 판정을 일치시킨다.
- **시야 검사(LOS)**: 눈 → 대상 사이 블록 차폐 레이캐스트로 벽 뒤 공격 차단(`combat.require_los`).
- **필터**: 공격자 자신 제외, 관전/크리에이티브(설정), 아군/파티(PvP 정책에 따름), 마커 방어대 등.
- 대상 수는 `max_targets`, 거리순.

### 4.3 지연 보상 (선택)

- 서버가 delay 시점에 판정하므로, 핑이 높은 플레이어는 화면상 맞았는데 서버에서는 빗나가는 일이 생길 수 있다.
- 1차: **허용 오차**(`range_tolerance`, `angle_tolerance_deg`)로 흡수. 2차(필요 시): 대상 위치 이력(최근 N틱)으로 재판정(lag compensation). 실측 후 결정한다. `[확인 필요]`

## 5. 이벤트·모듈 연동

| 방향 | 내용 |
|---|---|
| 발행 | `GearActionEvent`(SWING/HIT/CRIT/KILL/DRAW/PUT_AWAY, `fx-spec.md` 2장) |
| 발행 | 서버 검증을 거친 타격 `ValidatedMeleeHit`(코어 규격의 이름 재사용, 보스 기여도·랭킹·도감·칭호의 입력) — **자체 전투는 모든 타격이 서버 검증이므로 항상 이 이벤트로 발행**한다 |
| 소비 | `GearBridge`의 `applyStats`/`gear_def` 조회(강화 단계→`base_damage`) |
| 소비 | 코어 `guard.identity`(serial 상태), 쿨다운·PvP 정책 설정 |

- `event_id`를 부여해 중복 처리를 막는다(14.2장). 보상·기여도는 `ValidatedMeleeHit.event_id`로 멱등 처리.

## 6. LR 이식 경로

- 자체 `combat`의 정의 스키마는 LR와 호환되므로 `gear_def → LR index/display` 변환 도구로 이식 가능하다(`gearbridge-spec.md` 5.1, `fx-spec.md` 5.2).
- 이식 시 달라지는 점: LR은 클라이언트 대상 선정 → `guard.melee` 활성화 필요, 모션은 LR 애니메이션/상태 머신을 사용(자체 에셋 필요).
- **이식하지 않아도 되는 구성**을 기본값으로 한다. 이식 여부는 FX5 평가에서 결정.

## 7. 설정

```yaml
combat:
  enabled: true
  block_break: false
  require_los: true
  range_tolerance: 0.3         # 블록
  angle_tolerance_deg: 5
  latency_comp_ticks: 0        # 0=끔
  ignore_invulnerable_below_ticks: 10
  apply_player_attributes: false
  crit_mode: vanilla_jump      # vanilla_jump | chance
  pvp: false                   # PvP 허용 여부(정책)
  max_targets_cap: 8
  intent_rate_limit: 20        # 초당 의도 패킷 상한
```

## 8. 단계 (제안)

| 단계 | 내용 | 완료 조건 |
|---|---|---|
| CB0 | 신규 아이템 등록(`GearItem`), 컴포넌트, 바닐라 공격 차단, `C2SAttackIntent` 수신·쿨다운 | 의도 패킷만으로 공격 시작, 위조 패킷이 쿨다운을 우회 못 함 |
| CB1 | 범위 판정(cone/obb/arc, LOS, 필터)과 피해·넉백 적용 | 정의 값대로 대상·피해가 정해짐 |
| CB2 | 콤보·돌진·크리티컬·`GearActionEvent` 발행 → `fx` 연동 | 이펙트가 서버 값으로 발동 |
| CB3 | `ValidatedMeleeHit` 발행과 보스 기여도·도감 연동 | 보상 멱등성 |
| CB4 | 지연 보상·허용 오차 튜닝, PvP 정책 | 정상 핑 환경 오탐 기준 이하 |
| CB5 | LR 이식 평가(FX5와 병행) | 변환 도구와 동일 정의 동작 확인 |

## 9. 검수 시나리오

- [ ] 변조 클라이언트가 대상 목록·위치를 보낼 수단이 없고, 의도 패킷 남발이 쿨다운·레이트 제한으로 막힌다.
- [ ] 벽 뒤·원뿔 밖 대상이 맞지 않는다(`require_los`).
- [ ] 콤보 인덱스가 순환하고 `reset_ticks` 후 초기화된다.
- [ ] 다수 대상이 `max_targets`까지만 맞고 거리순으로 처리된다.
- [ ] 다단 히트가 무적 시간 설정에 따라 의도대로 들어가며, 방어구·인챈트 감소가 바닐라와 호환된다.
- [ ] 무기 정의 핫리로드 후 재시작 없이 값이 바뀐다.
- [ ] 정상 핑(100~150ms)에서 경계 타격 오탐이 기준 이하다.
- [ ] 이 아이템으로 바닐라 휩쓸기·기본 공격이 중복 발동하지 않는다.
- [ ] 아이템 복제·거래·보관함 이동 중에도 `serial` 상태에 따라 공격 가능 여부가 일관된다.
- [ ] 다수 플레이어 동시 공격 시 TPS가 유지된다.

## 10. 미확정·확인 필요

1. 모델 변형 방식(컴포넌트 predicate vs 클라이언트 동적 모델)과 정의 추가 시 코드 필요 여부
2. 서버 측 공격 의도 수집 지점(`InputEvent` → 커스텀 패킷) 구현 세부와 NeoForge 1.21.1 API
3. 바닐라 공격 취소 방법(이벤트 취소/아이템 `hurtEnemy` 오버라이드 등)과 휩쓸기 차단
4. 크리티컬 방식, 힘 효과 등 바닐라 보정 허용 여부
5. 블록 좌클릭(채굴) 정책
6. 대상 거리·각도 계산 기준(바운딩 박스 중심 vs 가장 가까운 점)
7. 지연 보상 필요성(실측 후)
8. PvP 허용 여부와 팀/아군 필터 정책
9. `base_damage` 산식과 강화 곡선(G3)

## 11. 결정 사항 (권장안, 2026-11-11 — 사용자 위임으로 작성, 언제든 변경 가능)

10장의 미확정 항목을 "가장 이상적인 방향"으로 정리했다. 근거는 ① 장비 강화가 유일한 성장 축(명세 1.1장) ② 서버 권위·검증 용이성 ③ 경제·밸런스 단순성이다. 수치는 [제안]이며 G3와 실측으로 조정한다.

| # | 항목 | 결정 | 근거 |
|---|---|---|---|
| 1 | 크리티컬 | **바닐라 점프 크리티컬 조건 재사용**(낙하 중·지면·사다리·물·실명·탑승 아님), 배율 ×1.5. 서버가 판정. `crit_mode: vanilla_jump`. 확률형 크리티컬은 강화 보너스 후속 확장 후보 | 예측 가능, 기존 플레이어 습관, 검증 쉬움 |
| 2 | 바닐라 보정(힘·나약함 등) | **기본 미적용**(`apply_player_attributes: false`). 장비 강화가 유일한 성장 축. 이벤트 버프가 필요하면 별도 `combat_modifier` 훅으로 운영자가 명시적으로 부여 | 포션·속성이 장비 밸런스를 우회하지 않게 |
| 3 | 블록 좌클릭 | **무기로 블록을 부수지 않는다**(`block_break: false`, 관리자 예외). 우클릭 상호작용은 정상 | 채굴·건축 통제(명세 3.1장 화이트리스트)와 무기 역할 분리 |
| 4 | PvP | **기본 끔**(`pvp: false`). 필요하면 지정 아레나/이벤트 구역(`pvp_zones`)에서만 켜고, 구역 안에서만 장비 파괴·드롭 정책을 별도 적용. 파티·길드 아군 필터는 PvP를 켤 때 도입 | 경제 서버의 괴롭힘·장비 손실 방지, 보스는 PvE(명세 11장) |
| 5 | 지연 보상 | **1차는 허용 오차**(`range_tolerance 0.3`, `angle_tolerance_deg 5`)로 흡수. 목표: 핑 150ms에서 경계 타격 불인정 비율 ≤ 3%. 초과 시 2차로 대상 위치 이력(최근 20틱) 재판정 도입(`latency_comp_ticks`) | 단순한 것부터, 실측 후 확장 |
| 6 | 대상 거리·각도 기준 | **대상 바운딩 박스에서 눈 위치와 가장 가까운 점** 기준. 중심점 기준은 큰 몹·보스에 불리해 채택하지 않음 | 보스·대형 몹 공정성 |
| 7 | 모델 변형 방식 | **`custom_model_data` 컴포넌트 predicate + 리소스 모델 JSON**(무기 정의 추가 = 리소스 + 데이터, 코드 불필요). 클라이언트 동적 모델은 이후 필요 시 도입 | 바닐라 메커니즘, 구현 단순 `[1.21.1 동작 확인]` |
| 8 | 공격 의도 수집 | 클라이언트 `InteractionKeyMappingTriggered`(좌/우 클릭)에서 `GearItem`을 들고 있으면 **바닐라 입력 취소 + `C2SAttackIntent{action, seq}` 전송**. 서버는 `seq` 단조 증가·레이트 제한(`intent_rate_limit`) 검증 | 클라이언트는 의도만, 서버 권위 |
| 9 | 바닐라 공격 차단 | `GearItem`은 `SwordItem`이 아니고 휩쓸기 능력(`SWORD_SWEEP`)을 부여하지 않는다. 서버 공격 이벤트(`AttackEntityEvent`)도 **이중 취소**. 피해는 우리 모듈만 발생 | 중복 피해·휩쓸기 방지 |
| 10 | `base_damage` 산식 | `base_damage(def, tier, level) = def.base_damage × tier_multiplier[tier] × (1 + k × level)`. 초기 `k = 0.06`(선형, 예측성 우선), 고강화 구간에서 체감 증가·감소는 구간별 `k`로 조정. 확정은 G3 시뮬레이션 | 단순한 곡선으로 시작해 데이터로 조정 |
| 11 | 다단 히트·무적 시간 | `ignore_invulnerable_below_ticks: 10`(10틱 미만 무적이면 해제) 기본, 보스는 정의별 오버라이드 | 콤보 체감, 보스 어뷰징 방지 |
| 12 | 콤보 | 좌공격은 배열 순환, `combo.reset_ticks: 30`. 우공격은 단발 고정. 콤보 단계별 `factor` 감소·증가는 정의별 | 단순·데이터화 |

### 11.1 결정 후 남는 확인 항목

- `custom_model_data` predicate가 우리 아이템 모델 오버라이드에서 의도대로 동작하는지(1.21.1)
- `InteractionKeyMappingTriggered` 취소와 의도 패킷 전송의 충돌 여부, 우클릭 사용(`Use`)과의 분리
- NeoForge 1.21.1에서 `GearItem`이 휩쓸기·기본 공격 쿨다운 UI(공격 속도 표시)를 일으키지 않는지
- 지연 보상 실측(정상 핑에서 오탐 비율)
- PvP 구역 정책의 구체 규칙(PvP를 켜는 시점에 별도 문서로 정리)

## 12. 쌍검(dual blade) 규격 (2026-11-11 제안)

### 12.1 방식 결정: **쌍검 1세트 = 아이템 1개** (A안, 2026-11-11 사용자 승인으로 우선 적용)

| 방식 | 내용 | 판단 |
|---|---|---|
| **A. 1세트 = 아이템 1개 (채택)** | 메인핸드의 아이템 1개가 두 자루를 나타내고 콤보가 좌·우 손을 번갈아 공격 | 시리얼·강화·도감이 1개라 GearBridge 구조를 그대로 재사용, 복제·짝 분실 문제 없음 |
| B. 실제 양손 아이템 | 메인/오프핸드에 각각 아이템(시리얼 2개) | 강화·거래·귀속이 둘로 갈라지고 밸런스·검증이 복잡해 **채택하지 않음** |
| C. 유령 오프핸드 | 서버가 오프핸드에 가짜 아이템을 채움 | 인벤토리 복제·손실 위험으로 **채택하지 않음** |

### 12.2 데이터 확장

```yaml
gear_def:
  def_id: "dual_iron_01"
  category: "sword"
  archetype: "dual_blade"
  hands: 2                    # 오프핸드 슬롯 점유(사용 금지)
  base_damage: 4.0            # 타당 피해는 낮게, 타수로 보상 (아키타입 DPS 검산 보정값, weapon-archetypes-spec.md 3.2)
  attack:
    attack_left:              # 4연타 콤보 (hand가 번갈아 적용)
      - { hand: right, factor: 1.0, knockback: 0.03, cooldown: 7,  delay: 0,
          hitbox: { type: arc, max_range: 3.0, max_angle: 35 }, max_targets: 3 }
      - { hand: left,  factor: 1.0, knockback: 0.03, cooldown: 7,  delay: 0,
          hitbox: { type: arc, max_range: 3.0, max_angle: 35 }, max_targets: 3 }
      - { hand: right, factor: 1.1, knockback: 0.05, cooldown: 8,  delay: 0,
          hitbox: { type: arc, max_range: 3.0, max_angle: 45 }, max_targets: 3 }
      - { hand: both,  factor: 1.5, knockback: 0.12, cooldown: 16, delay: 1,
          hitbox: { type: arc, max_range: 3.2, max_angle: 80 }, max_targets: 4 }   # 마무리 교차 베기
    attack_right:             # 교차 베기 + 돌진
      hand: both
      factor: 1.6
      knockback: 0.10
      cooldown: 24
      delay: 2
      hitbox: { type: arc, max_range: 3.5, max_angle: 110 }
      movement: { delay: 0, speed: 0.6 }
      max_targets: 6
  combo: { reset_ticks: 24 }
  fx_set: "fx_dual_basic"
```

- 새 필드: `archetype`, `hands`, 공격 항목의 `hand`(`left|right|both`). LR 이식 시 `hand` 필드는 변환 도구가 무시하거나 LR 쪽 두 동작에 매핑한다.
- 쌍검은 **타수가 많고 타당 피해가 낮은** 밸런스(같은 티어에서 초당 피해량이 다른 아키타입과 비슷해야 함). 광역은 약하고 단일 대상에 강한 방향으로 차별화한다. 수치는 [제안], G3로 확정.

### 12.3 오프핸드 규칙 (서버 검증)

- `hands: 2` 무기를 들려면 **오프핸드가 비어 있어야** 한다. 오프핸드에 아이템이 있으면 장착(메인핸드로 선택)을 거부하고 안내 메시지를 보낸다(또는 오프핸드 아이템을 인벤토리로 자동 이동, 설정 `combat.dual_offhand_policy: reject|auto_move`, 기본 `reject`).
- 쌍검을 든 동안 **오프핸드로의 이동(F 키 교체, 드래그, 단축키, 자동 이동)을 서버가 차단**한다. 인벤토리 클릭 이벤트·핫바 교체에서 검증한다. `[확인 필요: 우회 경로 전수 점검]`
- 쌍검을 다른 슬롯으로 옮겨 메인핸드를 벗어나면 정상 상태로 복귀한다.

### 12.4 이펙트·렌더링

- **손 위치 오프셋**: 눈 위치 기준 좌우 약 ±0.4블록(설정)에서 호를 그린다. `hand`가 `left/right`면 해당 손 쪽, `both`면 양쪽에서 동시에 그린다(`fx-spec.md`의 `particle_arc`에 `hand` 파라미터 추가, 호의 좌우 반전).
- **1인칭**: 한 모델에 두 자루가 들어간 쌍검 모델(교차 배치 등)을 메인핸드에 렌더한다. 바닐라 휘두르기 애니메이션은 메인 팔만 움직이므로 연출은 이펙트가 보완한다.
- **3인칭(선택, 클라이언트 렌더러)**: 플레이어 렌더에서 쌍검을 든 경우 반대 손에 두 번째 모델을 그린다. 우선순위는 낮다(FX3 이후).
- **양팔 모션**: 플레이어 애니메이션 라이브러리와 자체 제작 모션이 필요하므로 **후순위 확장**(`motion-authoring-guide.md`). 바닐라 백엔드 1차 범위에서는 하지 않는다.

### 12.5 GearBridge·치장과의 관계

- 쌍검은 **1개의 `serial`**을 가지며 강화·진화·도감·거래·귀속은 일반 무기와 동일하다.
- 외형 스킨 교체는 같은 `category` 안에서 자유(`gearbridge-spec.md` 13장). 쌍검 스킨을 단검류에 씌우는 것은 `hands` 값이 다르므로 **같은 `archetype`끼리만** 허용(렌더·오프핸드 규칙이 달라서).

### 12.6 검수 항목

- [ ] 오프핸드에 아이템이 있을 때 쌍검 장착이 정책(`reject`/`auto_move`)대로 처리된다.
- [ ] 쌍검을 든 상태에서 F 키·드래그·핫바 교체·자동 이동으로 오프핸드를 채울 수 없다.
- [ ] 콤보가 4단 순환하고 `hand`에 따라 이펙트 호가 좌·우로 반전된다.
- [ ] 마무리와 우클릭의 `both` 공격이 양쪽 호 이펙트와 넓은 판정을 낸다.
- [ ] 같은 티어에서 쌍검 초당 피해량이 다른 아키타입 기준 범위 안이다(G3 지표).
- [ ] 쌍검이 한 개의 `serial`로 강화·진화·거래 흐름을 통과한다.

### 12.7 미확정

1. 3인칭 두 번째 검 렌더와 양팔 모션을 도입할지, 시기
2. `dual_offhand_policy` 기본값(`reject` 권장)과 인벤토리 우회 경로 점검 결과
3. 쌍검의 콤보 단계 수·`factor` 분배와 밸런스 수치(G3)
4. 쌍단검처럼 다른 `hands: 2` 아키타입을 추가할지
