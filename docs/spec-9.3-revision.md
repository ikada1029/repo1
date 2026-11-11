# 명세 9.3 개정 요약 — 가구 뽑기 (등급 없는 균등 풀)

> 결정(2026-11-11): **가구에 등급(희귀도)을 두지 않는다.** 이에 따라 명세서 9.3과 연관 장을 개정했다.
> 전체 반영본: `docs/spec/minecraft-neoforge-spec-v0.2-draft.md` (업로드 원본의 초안 사본, 9.3 관련 부분만 수정)
> 근거: `docs/G3-economy-simulation-sheet.md` 13.7~13.8, `data/g3/G3-economy-simulation.xlsx`의 `Gacha_Flat` 시트.

## 1. 변경 요약

| 항목 | 기존(v0.1) | 개정(v0.2) |
|---|---|---|
| 등급 | 일반 65% / 희귀 25% / 영웅 9% / 전설 1% (예시) | **등급 없음**, 풀 안 모든 가구 1/N |
| 가구 구분 | 등급(희귀도) | **풀(상시·테마·시즌)과 획득 경로** |
| 천장 | 영웅 이상 50회 보장 | **선택 천장**: 목표 가구를 K=1.5N회 안에 보장, 목표 변경 시 초기화 |
| 중복 | 가구 조각으로 분해, 지정 교환 | 1개당 1조각, **X=0.5N조각**이면 미보유 가구 지정 교환 |
| 확정 경로 | 조각으로 지정 교환 | 선택 천장 + 조각 교환(항상 존재) |
| 거래 | 일반·희귀 거래 가능, 한정·전설 운영 선택 | 상시·테마 풀 거래 가능, **시즌 한정 운영 선택** |
| 가격 | 미정 | 1회 고정(초기 560 Coin), 난이도는 풀 크기로 조절 |
| 데이터 | `furniture_catalog.rarity`, `gacha_rolls`(천장 카운터) | `rarity` 삭제, `gacha_pools`·`gacha_state` 추가, `gacha_rolls`에 `pool_id/guaranteed/shards_gained` |

## 2. 수정한 위치

| 장 | 내용 |
|---|---|
| 9.2 | `furniture_catalog` 관리 항목에서 희귀도 제거(획득 경로 대체), 희귀 가구 → 뽑기 전용·시즌 한정 가구 |
| **9.3** | **전면 개정** (풀·균등 확률·선택 천장·조각·거래·가격 원칙·설계 근거 표) |
| 9.3.1 | 가구 풀 구성 예시를 등급 없는 풀 표(상시/테마/시즌, 풀 크기, 평균 비용)로 교체 |
| 14.1 | `furniture_catalog`(rarity 삭제·source 추가), `gacha_pools`(신규), `gacha_rolls`(필드 변경), `gacha_state`(신규) |
| 14.3 | 가챠 의사코드 개정 + `EXCHANGE_SHARDS`, `SET_WISH` 추가 |
| 16 | `gacha:` 설정 블록 교체(`rarity_tiers: false`, 풀·선택 천장·조각) |
| 17.1 | 검수 항목 개정(균등 확률·선택 천장·조각, 목표 변경 시 카운터 초기화) |
| 19 | 미확정 10번 개정(풀 목록·N·가격·K·X·시즌 풀 정책) |

수정하지 않은 곳: 9.4·9.5(직접 구매·Coin 소각/이동 구분은 그대로 유효), 6.3 도감 보상의 "가구 뽑기권"(풀 지정 뽑기권으로 해석), 1.2 루프의 "중복 조각 교환".

## 3. 설계 근거 요약 (G3 시뮬레이션, N=68·1회 600 Coin·중견 월소득 약 13.3만 Coin, [제안])

| 구조 | 지정 가구 평균 | P90 | 상한 | 평균 비용 |
|---|---|---|---|---|
| 균등·천장 없음 | 67.6회 | 154회 | 없음(P99 300) | 1.00 |
| 선택 천장 1.5N | 52.9회 | 102회 | 102 | 0.78 |
| 조각 교환 X=N | 56.9회 | 124회 | 없음 | 0.84 |
| **선택 천장 1.5N + 조각 0.5N (채택 제안)** | **47.9회** | **83회** | 102 | **0.71** |

- 조각은 교환 비용이 낮아야 효과가 있다: X=0.25N → 평균 37회, 0.5N → 48회, N → 57회, 1.5N → 62회.
- 풀 크기 30~150 전 범위에서 같은 구조가 평균 비용 약 30%, P90 약 45% 감소.
- 경제 영향: 지정 가구를 노리는 유저의 평균 소각이 약 29% 감소 → 가격 인상 또는 풀 크기 확대로 보정.

## 4. 개정된 9.3 전문

> 아래는 초안 사본에 반영된 9.3 본문이다.

### 9.3 가구 뽑기 [확정 기획 / 세부 수치 제안] — v0.2 개정(등급 없는 균등 풀)

**구매 단위:** `Coin → 가구 뽑기(1회/10회) → 균등 확률 결과 → 가구 인벤토리 → 주택 배치/거래/중복 조각 교환`.

- 뽑기는 **게임 내 Coin만 사용**. 실제 화폐/외부 현금 거래·재판매·환전 금지.
- **[확정 기획] 가구에 등급(희귀도)을 두지 않는다.** 한 풀 안의 모든 가구는 **같은 확률(1/N)** 로 나온다. 가구의 구분은 등급이 아니라 **풀(상시·테마·시즌 한정)과 획득 경로**로 한다.
- **풀(pool):** `pool_id`, `pool_version`, 가구 목록(N종), 1회 가격, 선택 천장 K, 조각 교환 비용 X, 종류(상시/테마/시즌), 유효 기간. **풀 크기 N과 1회 가격이 난이도를 정한다.** 풀 크기는 30~100종 범위를 권장한다 [제안].
- **확률은 UI에 공개**한다: 풀 구성(가구 목록), `각 가구 1/N`, 풀 버전, 선택 천장·조각 규칙, 시행 시점·결과·지급 ID 기록.
- **선택 천장 [제안]:** 유저는 풀에서 **목표 가구(찜) 1개**를 지정할 수 있다. 목표 가구를 얻지 못한 채 누적 뽑기가 `K`회(기본 `K = round(1.5 × N)`)에 도달하면 **목표 가구를 보장 지급**한다. 뽑기로 목표를 얻거나 보장 지급이 일어나면 카운터를 초기화하고, **목표를 바꾸면 카운터가 초기화**된다(확인 팝업으로 고지). 카운터와 남은 횟수는 UI에 항상 표시한다.
- **중복 → 가구 조각 [제안]:** 중복 가구 1개당 **1조각**(풀별 조각). `X`조각(기본 `X = round(0.5 × N)`)을 모으면 **풀 안의 미보유 가구 1개를 지정 교환**할 수 있다. 조각은 거래·외부 현금화 불가.
- **확정 경로 보장:** 선택 천장과 조각 교환으로 **원하는 가구를 얻는 경로가 항상 존재**한다(뽑기 운에만 의존하지 않음). 기본 가구는 9.4의 직접 구매로 항상 얻을 수 있다.
- 10회 구매 할인은 경제 정책으로만 조절(기본 10%); 무한 재구매를 강요하는 미끼형 연출 지양.
- 기능성/성능 가구는 확률상자 전용 보상으로 만들지 않는 것을 권장. **가구는 기본적으로 외형 목적**.
- 뽑기 중 서버 종료, 더블 클릭, 재시도, 인벤토리 꽉 참에도 **Coin 1회 차감 ↔ 결과 1회 지급** 일치. 지급 실패 시 보관함으로 이전.
- **거래:** 상시·테마 풀 가구는 거래 가능, **시즌 한정 가구는 운영 선택**. 거래 시 소유·획득 경로(`source`)를 추적한다.
- **가격 설계 원칙:** 1회 가격은 **고정**하고(초기 후보 560 Coin [제안]) 난이도는 풀 크기로 조절한다. 지정 가구 1종의 기대 비용은 대략 `0.7 × N × 1회 가격`(선택 천장 1.5N + 조각 0.5N 적용 시)이다.

**설계 근거(G3 `Gacha_Flat` 시뮬레이션, N=68·1회 600 Coin·중견 월소득 약 13.3만 Coin 기준, 모든 수치 [제안])**

| 구조 | 지정 가구 평균 | P90 | 최악(상한) | 평균 비용(균등 대비) |
|---|---|---|---|---|
| 균등·천장 없음 | 67.6회 | 154회 | 없음(P99 300) | 1.00 |
| **선택 천장 1.5N + 조각 0.5N (기본 제안)** | **47.9회** | **83회** | 102회 | **0.71** |

- 조각 교환 비용을 낮출수록 꼬리(P90)가 크게 줄어든다(X=0.25N → 평균 37회, X=N → 57회).
- 풀 크기 30~150에서 같은 구조가 평균 비용을 약 30%, P90을 약 45% 줄인다.

#### 9.3.1 가구 풀 구성 예시 [제안]

| 풀 | 구성 예시 | 크기 N(예) | 획득 경로 | 평균 비용(560 Coin, 선택 1.5N+조각 0.5N) | 경제 효과 |
|---|---|---|---|---|---|
| 기본 생활(상점) | 의자·책상·침실 장식 | — | **직접 구매(뽑기 없음)** | 고정가 | 진입용 소액 소각 |
| 상시 풀 | 생활·장식 혼합 | 68 | 뽑기·조각 교환 | 약 2.7만 Coin | 장기 Coin 소각 |
| 농장 테마 풀 | 허수아비·나무 선반·농가 소품 | 30 | 뽑기·조각 | 약 1.2만 Coin | 농부 테마 수요 |
| 광산 테마 풀 | 광물 전시대·광부 램프·작업 소품 | 30 | 뽑기·업적 | 약 1.2만 Coin | 광부 테마 수요 |
| 주방 테마 풀 | 테이블·냄비 장식·조리 가구 | 30 | 뽑기·조각 | 약 1.2만 Coin | 요리사 테마 수요 |
| 바다 테마 풀 | 수족관 장식·그물·항해 소품 | 30 | 뽑기·어부 업적 | 약 1.2만 Coin | 어부 테마 수요 |
| 시즌 한정 풀 | 계절 한정 장식·기념품 | 12~30 | 시즌 뽑기·이벤트 | 약 0.5~1.2만 Coin | 주기적 수요 생성 |

(평균 비용 = 0.7 × N × 560 Coin. 직접 구매 가구와 풀 가구의 가격 관계, 시즌 풀 복각 정책은 운영 결정.)

**중요:** 이 표는 *보상 기획 예시*이며 개별 가구가 해당 모드에 실제로 존재한다는 뜻은 아니다. 개발자는 선택한 가구 모드의 실제 **블록 ID와 사용 가능한 모델**을 확인하여 목록을 확정해야 한다.


## 5. 개정된 14.3 의사코드와 16장 설정

```text
ROLL_FURNITURE(player_uuid, pool_id, request_id, count):          # count = 1 | 10
  assert player.allowed and pool.active and now in [valid_from, valid_to]
  if request_id already processed: return saved result
  BEGIN TRANSACTION
    lock(wallet[player_uuid]); lock(gacha_state[player_uuid, pool_id])
    price = (count == 10) ? pool.price_10 : pool.price
    assert balance >= price
    debit(wallet, price, ledger_event=request_id)
    for i in 1..count:
      state.pity_counter += 1
      if state.wish_item != null and state.pity_counter >= pool.pity_k:
        item = state.wish_item; guaranteed = true                 # 선택 천장
      else:
        item = uniform_draw(server_rng, pool.items)               # 1/N, 등급 없음
      if owned(player, item): shards_gained = 1; state.shards += 1
      else: shards_gained = 0
      if item == state.wish_item: state.pity_counter = 0
      insert gacha_roll(request_id, i, pool_id, pool_version, item, guaranteed, shards_gained)
      grant_item_or_mailbox(item, grant_event=request_id + "#" + i)
    update gacha_state(version+1)
  COMMIT
  sync_client_result()

EXCHANGE_SHARDS(player_uuid, pool_id, item, request_id):          # 조각 교환
  BEGIN TRANSACTION
    lock(gacha_state[player_uuid, pool_id])
    assert state.shards >= pool.shard_cost and not owned(player, item) and item in pool.items
    state.shards -= pool.shard_cost
    grant_item_or_mailbox(item, grant_event=request_id)
  COMMIT

SET_WISH(player_uuid, pool_id, item, request_id):                 # 목표 변경 → 카운터 초기화
  state.wish_item = item; state.pity_counter = 0
```

```yaml
gacha:
  enabled: true
  currency: "Coin"
  real_money_enabled: false
  publish_rates: true
  rarity_tiers: false              # v0.2: 가구에 등급을 두지 않는다(균등 확률)
  # 다음 값은 G3 시뮬레이션 기반 제안이며 운영 확정치가 아님
  default_pool: "standard_s1"
  pools:
    standard_s1:
      kind: "standard"             # standard | theme | season
      pool_version: "furniture_s1"
      price: 560                   # 1회 가격(Coin)
      price_10: 5040               # 10회(10% 할인)
      pity:
        mode: "wish"               # 목표 가구 선택 천장
        k_multiplier: 1.5          # K = round(1.5 × N)
        reset_on_wish_change: true
      shards:
        per_duplicate: 1
        exchange_cost_multiplier: 0.5   # X = round(0.5 × N)
        tradable: false
  duplicate_shards_enabled: true
```

## 6. 후속 확인

- UI(`g5-wireframes.md` W-61)는 등급 확률표 대신 풀 구성·선택 천장 남은 횟수·조각 보유량을 표시하도록 이미 메모해 두었다. 와이어프레임을 개정 본문에 맞춰 다시 그린다.
- 위 수치(N, 1회 가격 560, K=1.5N, X=0.5N, 조각 1개/중복)는 모두 [제안]이며 G3 입력으로 조정할 수 있다.
- **조각 획득 경로 확대**(이벤트·가구 분해)와 **직접 구매 가구와 풀 가구의 가격 관계**는 별도 결정이 필요하다.
- 9.3 외의 결정 사항(요리 판정 폐지, 장비·전투·치장 구조, 라이선스, G3 기준값 등)도 초안 사본(v0.2)에 반영했다. 변경 목록은 `docs/spec/CHANGELOG-v0.2.md` 참고.
