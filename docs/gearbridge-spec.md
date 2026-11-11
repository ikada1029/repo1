# GearBridge 규격 v0.1 — 새 검 시스템 연동 구조

> 대상: 명세서 6장(장비 강화·인챈트·도감), 14.2장(데이터 규약), 15장 `gearbridge/`, 코어 규격(`server-core-mod-spec.md`), 근접 분석(`melee-system-findings.md`).
> 배경: 기존 자체 검 강화 모드는 폐기한다. 새 검 시스템은 **LR 근접 무기 체계(데이터 기반) 위에 구성**한다. 따라서 명세 6.1장의 "검 모드 내부는 범위 밖, 인터페이스만 정의"를 **"장비 시스템과 경제 서비스 사이의 경계"** 로 다시 정의한다.
> 상태: **[제안]**. 클래스·이벤트 이름은 후보이며 실제 API 확인 후 확정한다. `[확인 필요]`는 후속 검증 항목.

## 0. 먼저 정할 구조 결정

| ID | 결정 사항 | 선택지 | 권장 |
|---|---|---|---|
| GB-1 | 강화·진화 로직의 소유 | **A.** `economycore` 안의 `gearbridge`/`gear` 모듈 / **B.** 별도 "검 모드" | **A**(모드 1개 + 패키지 분리). 별도 모드는 배포·버전 관리 부담이 늘고, LR 의존과 코어 의존이 겹친다 |
| GB-2 | 강화 단계의 스탯 반영 | **a.** 단계마다 별도 `MeleeWeaponId` / **b.** 스택에 `enhance_level` 저장 + 속성 수정자 계산 | **b**(단계 폭증 방지). 진화(티어 변경)는 `MeleeWeaponId` 교체 |
| GB-3 | 시리얼·강화 저장 위치 | `CUSTOM_DATA` 키 / 코어의 자체 데이터 컴포넌트 | 자체 컴포넌트 `economycore:identity`(타 모드와 분리) |
| GB-4 | 진화 시 강화 단계 처리 | 유지 / 초기화 / 일부 감소 | 미확정(밸런스 결정, 6.2장) |
| **GB-5** | **장비 백엔드 (2026-11-11 결정)** | 바닐라 기반 + 이펙트 / LR 근접 체계 | **바닐라 백엔드를 먼저 구현하고 이펙트(`fx-spec.md`)를 붙인 뒤, 가능하면 LR 백엔드로 이식.** GearBridge는 백엔드를 추상화(`GearBackend`)해 식별·강화·진화·이벤트 구조를 공통으로 쓴다 |

> **GB-5 세부 결정(2026-11-11):** 바닐라 백엔드는 **우리가 등록한 새 아이템**(`economycore:gear_sword` 등 카테고리별 아이템 + `economycore:gear`의 `def_id`)과 **자체 서버 권위 범위 공격**(`combat-spec.md`)으로 구현한다. 피해는 공격자 속성이 아니라 `base_damage(def, tier, enhance_level)` 산식으로 직접 계산하므로, 아래 5장의 "속성 수정자" 방식은 **LR 백엔드 이식 시에만 검토**한다.

> **GB-5의 영향:** 이 문서에서 `(item_id, MeleeWeaponId)` 키, `DisplayId` 치장, LR의 `CUSTOM_DATA` 충돌 확인, LR 속성 수정자 확인(5장), 카탈로그→LR 데이터 팩 생성(5.1)은 **LR 백엔드 전용 항목**이다. 바닐라 백엔드에서는 `gear_key`가 단순히 `(item_id, def_id)`이며 `def_id`를 우리 컴포넌트(`economycore:gear`)에 저장하고, 공격력·공격 속도는 바닐라 속성 수정자 컴포넌트로, 내구도는 무적 컴포넌트로 처리한다. 아이템을 우리가 등록할지 바닐라 아이템에 컴포넌트를 붙일지는 GB0 스파이크에서 결정한다. 백엔드 어댑터 인터페이스는 `GearBackend { identifyDef(stack), setDef(stack, def_id), applyStats(stack, state), emitActionEvents(...) }`(제안)로 두며, 이펙트에는 `GearActionEvent`로 전달한다(`fx-spec.md` 2장).

## 1. 역할 경계

```text
 [경제 서비스]  economy/ enchant/ collection/ (Coin·강화석·확률·도감)
        │  GearBridge (이 문서)
        ▼
 [장비 계층]    gear/ : 카탈로그, 인스턴스, 스택 적용   ──► [LR 근접 체계] (MeleeWeaponId/DisplayId, 데이터 팩)
        ▲
 [코어]         guard.identity (시리얼·장부), guard.recipe, guard.melee(ValidatedMeleeHit)
```

- **경제 서비스**가 확률·비용·재화를 결정하고, **장비 계층**이 스택에 결과를 적용한다. 둘은 `GearBridge`로만 대화한다.
- 클라이언트는 "강화 요청"만 보낸다. 판정·재화·적용은 서버 권위(명세 1.3장).

## 2. 장비 식별 모델

### 2.1 카탈로그와 인스턴스

- **카탈로그(`gear_defs`)**: 어떤 종류의 장비인가. 키 = **`gear_key = (item_id, def_id)`**. LR 근접 무기는 `item_id = lrtactical:melee`, `def_id = MeleeWeaponId`(`melee-system-findings.md` 10.1~10.2).
- **인스턴스**: 플레이어가 가진 개별 장비. 키 = **`serial`(UUID)**, 코어 `guard.identity`가 발급·장부 기록.

```text
GearIdentity = {
  gear_key: { item_id, def_id },        // 종류 (LR: lrtactical:melee + MeleeWeaponId)
  serial: uuid,                          // 개별 식별 (economycore:identity)
  category: "sword" | ...,               // 도감 범위
  tier: int,                             // 진화 트리 위치
  evolution_id: string|null,
  enhance_level: int,
  display_id: string|null,               // LR DisplayId 오버라이드 (치장)
  owner: uuid|null,                      // 귀속
  status: "active" | "escrow" | "destroyed"
}
```

### 2.2 저장

- `economycore:identity`(코어)와 `economycore:gear`(이 모듈) 두 데이터 컴포넌트에 나눠 저장한다(`GB-3`). `serial`, `owner`는 identity, `enhance_level`, `evolution_id`, `tier`는 gear.
- 정본은 **DB(`gear_instances`)** 이고 스택 컴포넌트는 **캐시/표시용**이다. 불일치 시 DB 기준으로 복구한다(복제·변조 방어).
- 우리 키가 LR의 `CUSTOM_DATA`(`MeleeWeaponId`, `DisplayId`)와 충돌하지 않는지 실기동 확인. `[확인 필요]`

## 3. GearBridge 인터페이스 (명세 6.1장 개정)

```text
GearBridge.identify(stack) -> GearIdentity | null
GearBridge.locate(player, serial) -> stack_ref | null          // 인벤토리/장착/보관함 탐색
GearBridge.canEnhance(player, stack, ctx) -> {ok, reason, preview{rates_version, cost, rates}}
GearBridge.beginEnhance(event_id, player_uuid, serial, cost)   // serial 잠금 + 비용 예약
GearBridge.commitEnhance(event_id, result: SUCCESS|FAIL_KEEP|DESTROY, new_state)  // 적용
GearBridge.abortEnhance(event_id, reason)                      // 잠금 해제 + 예약 환급
GearBridge.evolve(event_id, serial, to_def_id, cost)           // 진화(def_id 교체)
GearBridge.applyStats(stack)                                   // 단계→속성 수정자·표시 재계산
GearBridge.issue(def_id, owner, source_event_id) -> stack      // 신규 발급(guard.identity 경유)
```

### 3.1 발행 이벤트 (모듈 간 공용 이벤트, 15장)

| 이벤트 | 시점 | 소비자 |
|---|---|---|
| `GearEnhanced(event_id, serial, from_level, to_level, rates_version)` | 강화 성공 확정 | 도감, 칭호, 알림, 랭킹 |
| `GearEnhanceFailed(event_id, serial, kept: bool)` | 실패(유지/파괴) | 통계, 본인 알림 |
| `GearDestroyed(event_id, serial, cause)` | 파괴 | 인벤토리 제거, 도감(업적 유지), 통계 |
| `GearEvolved(event_id, serial, old_def, new_def)` | 진화 확정 | 도감, 칭호 |
| `CollectionUnlocked(...)` | 도감 최초 달성 | 칭호 조건 엔진 |

- 이벤트에는 항상 `event_id`와 `source_system`을 넣는다(멱등성, 14.2장).
- **소비자는 이벤트가 중복 도착해도 한 번만 처리**해야 한다.

### 3.2 입력 이벤트(선택)

- 코어 `ValidatedMeleeHit`(검증된 타격): 스킬·콤보 보너스, 보스 기여도 계산용. 미검증 타격은 입력으로 쓰지 않는다(`server-core-mod-spec.md` 2.6.5.1).

## 4. 강화 트랜잭션

`reserve → resolve → apply` 3단계. 크래시·재접속·중복 클릭에도 **재화 1회 차감 ↔ 결과 1회 반영**을 보장한다.

```text
ENHANCE(player_uuid, serial, request_id):
  if request_id already processed: return saved result            # 멱등성
  BEGIN TRANSACTION
    lock(gear_instance[serial]); lock(wallet[player_uuid]); lock(stone stock)
    assert instance.owner == player and status == active
    assert locate(player, serial) found                           # 실물 존재 확인
    rates = rates_for(tier, level, rates_version)                 # 서버가 확률표 선택
    assert balance/stones >= cost
    debit(wallet, coin, ledger_event=request_id); consume(stones)
    result = server_rng.draw(rates)                               # SUCCESS | FAIL_KEEP | DESTROY
    insert gear_history(request_id, serial, old_state, new_state, rates_version)
    update gear_instance(level / status)
    insert outbox(op = apply_to_stack, serial, new_state, request_id)
  COMMIT
  apply_outbox(request_id)        # 스택 적용: 성공 시 컴포넌트 갱신, 파괴 시 스택 제거
  emit events                     # GearEnhanced / GearEnhanceFailed / GearDestroyed
  sync_client_result()
```

- **outbox**: DB 커밋 후 서버가 죽어도 `apply_to_stack`을 다음 접속/기동 시 재실행한다. 재실행은 `request_id`로 한 번만 적용된다.
- **`gear_serial` 잠금**: 강화 진행 중 같은 장비의 이동·거래·드롭·진화 요청을 거부한다.
- **실물 적용 실패**(스택이 없어졌거나 다른 위치로 이동): 정책 필요. 제안 — 커밋 전에 `locate`로 확인하고, 커밋 후 적용 시 스택이 없으면 보관함에 정본 상태로 재발급하고 로그를 남긴다. `[결정 필요]`
- **확률·비용**은 `rates_version`과 함께 기록해 사후 감사 가능(명세 6.2장). 성공·실패·파괴율 합 = 100% 검증.
- **도감 등록**은 `GearEnhanced`/`GearEvolved` 소비자가 `(gear_id, enhance_level, evolution_id)` 최초 달성만 영구 기록(6.3장).

## 5. 스탯 반영 (GB-2의 b안)

- LR의 피해 산식: `기본 = 공격자의 ATTACK_DAMAGE 속성 × factor`(+ 인챈트). 따라서 강화 단계는 **스택의 속성 수정자**(바닐라 `ATTRIBUTE_MODIFIERS` 컴포넌트)로 공격력 가감을 부여하는 방식이 LR 코드를 건드리지 않는 방법이다. `[확인 필요: 메인핸드 속성 수정자가 LR 공격 계산에 반영되는지, LR 자체의 `attributes` 데이터와 중복 적용되지 않는지]`
- `applyStats(stack)`은 `enhance_level`·`tier`로 수정자를 **전체 재계산**(누적 적용이 아니라 매번 덮어쓰기)해 중복 적용을 막는다.
- 대안(단계별 `MeleeWeaponId`)은 스탯이 JSON에 고정되어 확실하지만 단계 수 × 종류 수만큼 정의가 생긴다. b안이 막히면 **데이터 생성 도구**로 정의를 자동 생성한다(5.1).
- 강화가 영향을 주는 값: 공격력(필수), 그 외(공격 속도 `cooldown`, 사거리 등)는 설계 결정. 공격 속도·히트박스는 데이터 값이므로 단계별 변경 시 `guard.melee` 허용 오차와 정합을 맞춘다.

### 5.1 카탈로그 → LR 데이터 팩 생성 (제안)

- `gear_defs`(우리 카탈로그)를 정본으로 두고, 빌드 도구가 LR용 `index/melee/<id>.json`, `display/melee/<id>.json`을 **생성**한다(`motion-authoring-guide.md`의 파라미터 모델과 연결).
- 모든 생성 결과에 `provenance`(자체 제작 / 허락받음)를 기록한다. TaCZ·LR 에셋을 복사·변형한 결과는 만들지 않는다.

## 6. 진화와 치장

- **진화**: 진화 트리(`evolution_tree`: `from_def`, `to_def`, 조건, 비용)에 따라 `MeleeWeaponId`를 교체한다. `serial`은 유지하고 `gear_history`에 `GearEvolved`를 남긴다. 진화 시 `enhance_level` 처리는 `GB-4`로 결정한다.
- **치장(외형)**: LR `DisplayId` 오버라이드로 구현한다(`cosmetics-social-spec.md`). 치장은 `GearIdentity.display_id`에 두고 스탯에는 영향이 없다. 단 `display`가 모션·상태 머신도 지정하므로 외형 스킨의 애니메이션 호환 규칙(같은 유형끼리만 교체 허용 등)을 정한다.

## 7. 귀속·거래·사망

- 장비 `owner` 귀속 여부는 카탈로그 정책(`gear_defs.bind_policy`)으로 지정(명세 19장 8번 미확정).
- 거래·의뢰·보관함 이동 시 `serial`·`status` 검증, `escrow` 상태 중 사용 불가.
- 사망 드롭·회수는 별도 정책. 파괴된 장비는 `status=destroyed`로 영구 보존하며 재발급하지 않는다(도감 업적은 유지, 실물만 소멸 — 6.2장).
- 같은 `serial`이 둘 이상 관측되면(복제 의심) 코어 `guard.identity`가 플래그를 올린다.

## 8. 데이터 모델 (명세 14.1장 보강)

| 테이블 | 주요 필드 | 무결성 |
|---|---|---|
| `gear_defs` | `def_id, item_id, category, tier, base_stats_json, bind_policy, active` | `(item_id, def_id)` 유니크 |
| `gear_instances` | `serial PK, def_id, owner_uuid, enhance_level, evolution_id, display_id, status, version` | 낙관적 락 |
| `gear_history` | `id, serial, request_id UNIQUE, old_state, new_state, rates_version, created_at` | 강화·진화 감사 |
| `enhance_rates` | `tier, level, success, keep, destroy, coin_cost, stone_cost, rates_version` | 합 100% 검증 |
| `evolution_tree` | `from_def, to_def, conditions_json, cost_json` | 순환 방지 검사 |
| `pending_gear_ops` | `request_id PK, serial, op, payload, status` | outbox, 재실행 안전 |

## 9. 범위

- **포함**: 검(근접 무기) 강화·진화·도감 연동·치장 연동.
- **제외(확장 후보)**: 방어구·활 강화(명세 7.4장), 총기 강화(총기는 강화·스킬 대상 제외, 10.1장), 직업 도구(별도 시스템, 4.2장).
- 스킬(`onSkillUsed`)은 선택 사항으로 보류.

## 10. 단계와 선행 조건

| 단계 | 내용 | 선행 |
|---|---|---|
| GB0 | 식별·저장 스파이크: `(item_id, MeleeWeaponId)` + `economycore:identity` 부여, 스택 직렬화·복구, LR 충돌 확인 | 코어 C0, C3(identity) |
| GB1 | 카탈로그·인스턴스·`applyStats`(속성 수정자 반영 검증) | GB0 |
| GB2 | 강화 트랜잭션(reserve→resolve→apply, outbox, 잠금) + 이벤트 | 코어 persistence, 지갑·원장(P1) |
| GB3 | 진화 트리, 도감·칭호 연동 | GB2, `cosmetics-social-spec.md` S1 |
| GB4 | 카탈로그→LR 데이터 팩 생성 도구, 치장(DisplayId) | GB1 |

## 11. 검수 시나리오 (명세 17.1장 보강)

- [ ] 강화 도중 중복 클릭·재접속·서버 재시작이 있어도 Coin·강화석·장비 변화가 **정확히 1회**.
- [ ] 같은 `serial` 동시 강화 요청 중 하나만 처리되고 나머지는 거부.
- [ ] 파괴 시 스택이 **한 번만** 제거되고 도감 업적은 유지, 재발급 불가.
- [ ] 강화 단계가 공격력에 반영되고 `applyStats`를 반복 호출해도 중복 증가가 없다.
- [ ] 진화 후 `serial` 유지, 이력 기록, 도감 등록 1회.
- [ ] 스택을 복제하려는 시도(드롭·상자·호퍼·크래시 재접속)에서 `serial` 중복이 탐지된다.
- [ ] `rates_version`이 모든 강화 기록에 남고 합계 100% 검증이 통과한다.
- [ ] `DisplayId` 치장 변경이 스탯과 도감 키를 바꾸지 않는다.
- [ ] outbox 재실행이 서버 강제 종료 후에도 한 번만 적용된다.

## 12. 미확정·확인 필요

1. GB-1~GB-4 결정(소유 모듈, 스탯 반영 방식, 저장 위치, 진화 시 단계 처리)
2. LR에서 메인핸드 속성 수정자가 피해 계산에 반영되는지, 무기 `attributes`와의 중복 여부
3. `economycore:identity`/`economycore:gear` 컴포넌트와 LR `CUSTOM_DATA`의 공존 시 직렬화·클라이언트 동기화 동작
4. 커밋 후 스택 적용 실패 시 복구 정책(보관함 재발급 vs 롤백)
5. 외형 스킨 교체 시 모션 호환 규칙
6. 강화가 영향을 주는 스탯 범위(공격력 외)
7. 귀속·거래 정책(명세 19장 8번)과 `bind_policy` 기본값
8. 진화 트리 구조(분기 수, 조건)와 도감 키 정의

## 13. 결정 사항 (권장안, 2026-11-11 — 사용자 위임으로 작성, 언제든 변경 가능)

`combat-spec.md` 11장과 같은 기준(① 장비 강화가 유일한 성장 축 ② 서버 권위 ③ 단순성)으로 정리했다. 수치는 [제안].

| # | 항목 | 결정 | 근거 |
|---|---|---|---|
| GB-1 | 강화·진화 로직 소유 | **`economycore` 모드 안의 `gear`/`gearbridge` 패키지**(별도 모드 만들지 않음) | 배포·버전 관리 단순, 코어 서비스(원장·장부)와 같은 트랜잭션 경계 |
| GB-2 | 스탯 반영 | **`enhance_level`을 컴포넌트에 저장하고 서버가 `base_damage` 산식으로 계산**(공격자 속성·속성 수정자에 의존하지 않음, `combat-spec.md` 4.1). 진화는 `def_id` 교체 | LR 속성 수정자 불확실성 제거, 전 구간 서버 권위 |
| GB-3 | 시리얼·강화 저장 | 자체 컴포넌트 `economycore:identity` + `economycore:gear`, **정본은 DB**(컴포넌트는 캐시) | 타 모드와 분리, 복구 가능 |
| GB-4 | 진화 시 강화 단계 | **일부 이월**: `carry_over_ratio`(기본 0.5, 내림)만큼 이월, 진화 노드별로 조정 가능 | 진행 손실의 좌절감은 줄이고 상위 단계 도전 동기 유지, 파괴 위험 구간을 통째로 건너뛰는 것 방지 |
| 적용 실패 복구 | 커밋 후 스택 적용 실패(스택이 없거나 이동) | **계정 보관함에 정본 상태로 재발급**하고 로그 기록(롤백하지 않음: 이미 확정된 재화·결과 보존) | 재화 1회 차감 ↔ 결과 1회 반영 보존 |
| 강화 영향 범위 | 강화가 바꾸는 스탯 | **공격력(`base_damage`)만**. 쿨다운·히트박스·사거리는 강화로 바꾸지 않고 **티어(진화)에서만** 변경 | 밸런스·판정 단순화 |
| 귀속·거래 | `bind_policy` 기본값 | **일반·희귀 장비는 거래 가능**(시리얼 유지, 거래 수수료로 소각), **영웅 이상·진화 최종형·보스 재료 장비는 획득 시 귀속**(`bind_on_acquire`). 귀속 장비도 강화·진화는 가능 | 경제 순환과 상급 장비 가치 보호의 균형 |
| 외형 스킨 교체 | 교체 규칙 | **같은 `category` 안에서 자유 교체**(바닐라 백엔드는 모델만 교체, 모션 호환 문제 없음). LR 이식 시에는 같은 유형끼리만 | 단순 |
| 진화 트리 구조 | 분기 수·깊이 | **분기 최대 2, 깊이 3~4단계**. 도감 키는 `(gear_id, enhance_level, evolution_id)`. 순환 방지 검사 필수 | 도감 항목 폭증 방지, 콘텐츠 관리 가능 |
| 도감 대상 | 범위 | 검(근접 무기)만 1차 포함. 방어구·활은 확장 | 명세 6.1·7.4장 |

### 13.1 결정 후 남는 확인 항목

- `economycore:identity`/`economycore:gear` 컴포넌트의 직렬화·클라이언트 동기화(다른 모드와의 공존)
- 귀속 장비 거래·보관함·사망 드롭 흐름의 세부 규칙(명세 19장 8번)
- `carry_over_ratio`와 진화 비용의 균형(G3 시뮬레이션)
