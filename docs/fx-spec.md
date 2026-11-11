# 이펙트(fx) 규격 v0.1 — 모션 없는 연출 시스템 (LR 이식 가능 설계)

> 방침(2026-11-11): **이펙트를 먼저 구현**하고, 가능하면 나중에 LR 근접 체계 백엔드로 **이식**한다. 모션(애니메이션) 제작은 이식 단계의 선택 사항으로 미룬다.
> 연관 문서: `gearbridge-spec.md`(장비 백엔드), `server-core-mod-spec.md`(코어), `cosmetics-social-spec.md`(치장), `melee-system-findings.md`(LR 분석), `motion-authoring-guide.md`(모션, 선택).
> 상태: **[제안]**. 이벤트·API 이름은 후보이며 NeoForge 1.21.1 실제 코드로 확인한다. `[확인 필요]`는 후속 검증 항목.

## 1. 목표와 원칙

- **목표:** 무기마다·강화 단계마다 다르게 느껴지는 연출(궤적, 타격 효과, 소리, 오라, 강화·진화 연출)을 **데이터로 정의**하고 서버가 구동한다.
- **원칙**
  1. **전투 판정 불변**: 이펙트는 피해·명중·이동에 영향을 주지 않는다(순수 표시).
  2. **서버 권위 트리거**: 연출 발동은 서버가 확인한 사건(`GearActionEvent`)에서만 한다. 클라이언트가 임의로 발동 요청할 수 없다.
  3. **백엔드 독립**: 이펙트 정의는 장비가 바닐라 기반이든 LR 기반이든 **같은 데이터**로 동작한다(트리거 어댑터만 교체).
  4. **데이터 기반**: JSON 정의 + 핫리로드. 코드 수정 없이 무기·단계별 연출을 추가한다.
  5. **성능 상한**: 플레이어·서버 단위 예산을 두고 초과 시 단계적으로 축소한다.
  6. **접근성**: 클라이언트 옵션(`이펙트 상세도`: 끔/낮음/보통/높음)으로 파티클·화면 흔들림을 줄일 수 있다(광과민성 고려).
  7. **에셋 출처**: 모든 파티클 텍스처·소리·모델은 자체 제작 또는 허락받은 것만 쓰고 `provenance`를 기록한다. TaCZ·LR 에셋은 복사·변형하지 않는다.

## 2. 구조

```text
 [트리거 소스]                [fx 코어]                         [출력]
 바닐라 백엔드 어댑터 ─┐                                   ┌─► 서버 전송: 파티클, 소리, 타이틀
 (공격/크리티컬/처치)   ├─► GearActionEvent ─► FxDispatcher ─┼─► 클라이언트 모듈(선택): 화면 흔들림, 궤적 리본, 오라 렌더
 LR 백엔드 어댑터(이식) ┤        │               │          └─► 상태 표시: 액션바(선택)
 GearBridge 이벤트 ────┘        │          (조건 평가·예산·쿨다운)
 (GearEnhanced 등)              └─ 효과 세트 선택(장비 정의 + 강화 단계 + 플레이어 치장)
```

- **`GearActionEvent`(백엔드 공용 입력)**

```text
GearActionEvent {
  event_id, tick,
  actor: uuid, serial, def_id, tier, enhance_level, evolution_id,
  action: SWING | HIT | CRIT | KILL | DRAW | PUT_AWAY | HOLD_TICK | BLOCK ...,
  combo_index: int,
  origin: Vec3, direction: Vec3,        // 서버 값(플레이어 눈 위치·시선)
  targets: [ {entity_id, pos, hit_point} ]   // HIT/KILL/CRIT일 때
}
```

- 이펙트는 **이 이벤트와 GearBridge 이벤트**(`GearEnhanced`, `GearEnhanceFailed`, `GearDestroyed`, `GearEvolved`)만 입력으로 쓴다. 백엔드 세부는 알지 못한다.

## 3. 이펙트 정의 (데이터)

### 3.1 효과 세트와 효과

```yaml
fx_set:
  id: "fx_flame_blade"
  provenance: "original"
  applies_to:                       # 조건 (모두 AND)
    def_id: ["sword_flame_01"]      # 또는 tag, tier 범위
    enhance_level: { min: 0 }
  effects:
    - id: "swing_arc"
      on: SWING
      conditions: { combo_index: [0, 2] }
      cooldown_ticks: 0
      audience: nearby              # self | nearby | others
      radius: 48
      actions:
        - type: particle_arc
          particle: "economycore:flame_slash"    # 자체 등록 또는 바닐라 파티클
          radius: 2.2               # 팔 길이
          angle_start_deg: -60
          angle_end_deg: 60
          count: 18
          plane: "horizontal|diagonal_down"
        - type: sound
          sound: "economycore:fx.flame_swing"
          volume: 1.0
          pitch_range: [0.95, 1.05]
    - id: "hit_spark"
      on: HIT
      actions:
        - { type: particle_burst, particle: "minecraft:flame", count: 12, spread: 0.3, at: hit_point }
        - { type: sound, sound: "economycore:fx.flame_hit" }
    - id: "aura_lv10"
      on: HOLD_TICK
      conditions: { enhance_level: { min: 10 } }
      interval_ticks: 10
      actions:
        - { type: particle_aura, particle: "minecraft:small_flame", count: 2, around: weapon }
```

### 3.2 트리거 종류와 매핑

| 트리거 | 의미 | 입력 이벤트 |
|---|---|---|
| `SWING` | 휘두르는 순간 | 백엔드 어댑터 |
| `HIT` / `CRIT` / `KILL` | 타격·치명타·처치 | 백엔드 어댑터 |
| `DRAW` / `PUT_AWAY` | 꺼내기·집어넣기 | 백엔드 어댑터 |
| `HOLD_TICK` | 손에 든 동안 주기 발동(오라) | 서버 틱(범위·주기 제한) |
| `ENHANCE_SUCCESS` / `ENHANCE_FAIL` / `DESTROY` / `EVOLVE` | 강화·진화 연출 | GearBridge 이벤트 |

### 3.3 액션 종류

| 액션 | 구현 계층 | 클라이언트 모드 필요 |
|---|---|---|
| `particle`, `particle_burst`, `particle_arc`, `particle_aura` | 서버가 바닐라 파티클 패킷 전송(자체 파티클 타입은 클라이언트 등록 필요) | 바닐라 파티클만: 불필요 / 자체 파티클: 필요 |
| `sound` | 서버가 소리 재생(자체 소리는 리소스 필요) | 자체 소리: 리소스 |
| `title` / `actionbar` | 강화 결과 메시지 | 불필요 |
| `camera_shake` | 클라이언트 모듈이 수신해 화면 흔들림 | 필요 |
| `trail_ribbon` | 클라이언트 모듈이 검 궤적 리본 렌더 | 필요 |
| `hit_stop` | 클라이언트 모듈이 짧은 프레임 정지 연출 | 필요 |
| `glow` / `overlay` | 아이템 광택·오버레이(렌더러) | 필요 |

- `economycore`는 메뉴 UI(명세 3.3장)를 위해 어차피 **클라이언트 구성요소를 가진다.** 따라서 클라이언트 전용 액션은 "있으면 더 좋은" 2단계 기능으로 두고, 1단계는 서버 전송 가능한 액션만으로 완결하게 만든다.

### 3.4 기하 계산 (궤적 호)

- 호는 서버가 `origin`(눈 위치), `direction`(시선), 플레이어 키·팔 길이 기준으로 계산한 **점 목록**으로 만든다. 평면(수평, 사선 내려치기 등)과 각도 범위, 밀도를 데이터로 받는다.
- LR 백엔드에서는 **LR 무기 데이터의 히트박스(원뿔 `max_range`·`max_angle`)에서 호의 반지름·각도를 자동으로 도출**해 시각과 판정을 맞춘다(5장 이식).

## 4. 예산과 성능

| 항목 | 기본값(제안) | 목적 |
|---|---|---|
| 효과당 최대 파티클 수 | 40 | 폭주 방지 |
| 플레이어당 초당 파티클 예산 | 400 | 한 사람이 서버를 점유하지 않게 |
| 서버 전체 초당 파티클 예산 | 설정 | TPS 보호, 초과 시 낮은 우선순위부터 축소 |
| `HOLD_TICK` 오라 | 주기 ≥ 5틱, 시야 거리 컬링 | 상시 발동 비용 제한 |
| 전송 반경 | 48블록(효과별 조정) | 대역폭 |
| 우선순위 | 강화·진화 연출 > 타격 > 휘두르기 > 오라 | 초과 시 하위 생략 |

- 서버 부하가 임계를 넘으면 `quality`를 자동으로 한 단계 낮춘다(설정, 로그 기록).
- 클라이언트 `이펙트 상세도` 옵션을 존중해 서버가 보내는 양을 줄이거나 클라이언트가 렌더를 생략한다.

## 5. 백엔드 어댑터와 LR 이식

### 5.1 1차: 바닐라 백엔드 어댑터

> **2026-11-11 결정:** 검은 새 아이템 + 자체 서버 권위 범위 공격(`combat-spec.md`)이다. 따라서 `SWING/HIT/CRIT/KILL`은 바닐라 이벤트를 우회해 감지할 필요 없이 **`combat` 모듈이 서버에서 직접 `GearActionEvent`를 발행**한다(클라이언트의 공격 의도 패킷이 휘두르기 시작점). 아래 "입력 후보"는 `combat`이 없는 경우의 참고이며, 10장의 1번(휘두르기 감지 지점)과 6번(범위 공격 도입 여부)은 이 결정으로 해소되었다. 호의 기하는 `combat`의 `arc` 판정과 같은 함수를 공유한다.

- 입력 후보(`[확인 필요]`): 공격(`AttackEntityEvent`), 치명타(`CriticalHitEvent`), 피해(`LivingIncomingDamageEvent`), 처치(`LivingDeathEvent`), 휘두르기 감지(클릭 입력은 클라이언트 → 서버 패킷 또는 팔 휘두르기 패킷). **정확한 서버 측 휘두르기 감지 지점은 C0 스파이크에서 확인한다.**
- 어댑터가 서버 값(눈 위치·시선·대상)으로 `GearActionEvent`를 만든다. 클라이언트 값은 사용하지 않는다.
- 범위 공격이 필요하면 서버에서 직접 계산한다(이펙트 범위와 같은 기하를 재사용 가능).

### 5.2 이식 단계: LR 백엔드 어댑터

| 항목 | 이식 방식 |
|---|---|
| 트리거 입력 | `guard.melee`의 `ValidatedMeleeHit`(타격), LR 공격 준비/지연 정보(`delay`, `cooldown`), (휘두르기) 클라이언트 `MeleePreAttackEvent`를 서버 패킷으로 중계 `[확인 필요]` |
| 타이밍 | LR의 `delay`(틱)에 맞춰 `HIT` 연출 시점을 정렬 |
| 기하 | LR 히트박스(원뿔/OBB) 값에서 호 반지름·각도 도출 |
| 소리 | LR `display.sounds` 키(`attack_left/right`, `*_hit`, `crit`, `kill`)와 충돌하지 않게 fx 소리는 서버 전송, 필요 시 LR 키에 매핑 |
| 모션 동기 | 이식 단계에서만 해당. 우리 자체 애니메이션을 만들면 `animation.sound_effects` 키프레임을 fx 트리거로 연결 가능 |
| 보안 | 대상 선정은 `guard.melee` 재검증 결과만 사용(미검증 타격으로 연출·보상 발동 금지) |

- **이식 가능성 판단 기준(FX5):** ① 이펙트 정의 파일을 수정하지 않고 어댑터만 교체해 동일 효과가 나오는가 ② 타이밍 오차(휘두르기 ↔ 연출)가 허용 범위인가 ③ 라이선스(LR 코드 의존 범위, GPL 소스 제공) 충족 ④ TaCZ/LR 업데이트에 대한 유지보수 부담.
- 이식 비용이 크면 **바닐라 백엔드를 최종 구성**으로 유지한다(이식은 선택 사항).

## 6. GearBridge·치장·도감과의 연결

- **강화·진화 연출:** `GearEnhanced`/`GearEnhanceFailed`/`GearDestroyed`/`GearEvolved`가 직접 `ENHANCE_*`/`EVOLVE` 트리거가 된다. 결과 확정(커밋) **후** 연출이 나가므로 연출만 보고 결과가 바뀌지 않는다.
- **강화 단계별 외관:** `enhance_level` 구간(예: 5/10/15)에 따라 효과 세트의 조건이 달라진다 → 오라·궤적 강도 변화. 단계 간 진행감을 데이터만으로 만든다.
- **치장(`cosmetics-social-spec.md`):** 플레이어가 장착한 **fx 스킨**(궤적 색, 타격 효과 변형)은 효과 세트의 파라미터를 덮어쓰는 방식이며 스탯에 영향이 없다. 구매·보유 관리는 이름 스타일과 같은 구조(`player_fx_skins`).
- **서버 알림:** 높은 강화 성공 연출은 서버 공지(4.1장)와 같은 이벤트를 소비하되 옵트아웃을 존중한다.
- **총기:** 총기 연출(발사음·궤적)은 TaCZ 건팩 자체 에셋을 그대로 쓰며 이 모듈의 대상이 아니다.

## 7. 데이터·설정

- **정의 파일(정본):** `config/economycore/fx/*.json`(또는 데이터 팩). 핫리로드 `/economycore reload fx`. 변경 이력은 버전·해시로 기록.
- **플레이어 데이터(DB):** `player_fx_skins(uuid, skin_id, acquired_at, source_event_id UNIQUE)`, `player_fx_equipped(uuid, slot, skin_id)`, 클라이언트 옵션은 클라이언트 설정.
- **설정:**

```yaml
fx:
  enabled: true
  quality: normal            # off | low | normal | high (서버 기본)
  auto_degrade: true         # 부하 시 자동 축소
  budget:
    per_effect_particles: 40
    per_player_per_sec: 400
    server_per_sec: 12000
  hold_tick:
    min_interval_ticks: 5
    cull_distance: 32
  log_level: info
```

## 8. 단계 (제안)

| 단계 | 내용 | 완료 조건 |
|---|---|---|
| FX0 | 디스패처·정의 로더·핫리로드·파티클/소리 액션·예산, 테스트 명령(`/fx test <세트>`) | 정의 변경 후 재시작 없이 반영, 예산 초과 시 축소 로그 |
| FX1 | 바닐라 백엔드 어댑터(`SWING/HIT/CRIT/KILL`) + 예시 효과 세트 3종 | 서버 값만 사용, 클라이언트 위조로 발동 불가 |
| FX2 | `HOLD_TICK` 오라, 강화·진화 연출(GearBridge 이벤트), 단계별 세트 | 강화 결과 확정 후에만 연출, 중복 이벤트에도 1회 |
| FX3 | 클라이언트 모듈: 화면 흔들림·궤적 리본·상세도 옵션 | 옵션 `끔`에서 렌더 없음, 접근성 점검 |
| FX4 | fx 스킨(치장) 연동 | 스킨이 스탯·도감 키를 바꾸지 않음 |
| FX5 | **LR 백엔드 어댑터 이식 평가 → 가능하면 이식** | 5.2의 판단 기준 4개 충족 여부 보고서 |

## 9. 검수 시나리오

- [ ] 정의 파일 수정 후 핫리로드로 연출이 바뀌고, 잘못된 정의는 로드를 거부하고 로그를 남긴다.
- [ ] 변조 클라이언트가 연출 발동을 요청할 수단이 없다(서버 이벤트에서만 발동).
- [ ] 같은 강화 이벤트가 중복 도착해도 연출은 1회.
- [ ] 한 플레이어가 연속 휘두르기·다수 대상 타격을 해도 예산을 넘지 않고, 서버 TPS가 유지된다.
- [ ] 다수 플레이어 오라(`HOLD_TICK`)가 동시에 켜져도 서버 예산 안에서 우선순위대로 축소된다.
- [ ] 강화 단계가 바뀌면 효과 세트가 구간에 맞게 전환된다.
- [ ] 이펙트 상세도 `끔`에서 파티클·화면 흔들림이 나오지 않는다.
- [ ] 자체 파티클·소리 리소스가 없을 때(리소스 미적용 클라이언트) 오류 없이 대체 연출로 동작한다.
- [ ] 이식 평가(FX5): 어댑터만 교체해 같은 정의 파일로 LR 백엔드에서 동일 연출이 나온다.

## 10. 미확정·확인 필요

1. 서버에서 휘두르기(`SWING`)를 신뢰성 있게 감지하는 지점(이벤트/패킷)
2. 자체 파티클 타입 등록·리소스 배포 방식과 미적용 클라이언트의 대체 동작
3. 클라이언트 전용 액션(화면 흔들림, 궤적 리본, 히트스톱) 구현 범위와 우선순위
4. 파티클·소리 예산 기본값(실측), 오라 허용 범위
5. fx 스킨의 거래 가능 여부와 획득 경로(`cosmetics-social-spec.md`와 정합)
6. 바닐라 백엔드에서의 범위(원뿔) 공격 도입 여부(이펙트 기하와 판정 일치 문제)
7. LR 이식 시 `MeleePreAttackEvent`(클라이언트 전용)를 서버 연출로 연결하는 방법

## 11. 결정 사항 (권장안, 2026-11-11 — 사용자 위임으로 작성, 언제든 변경 가능)

10장의 미확정 항목을 이상적인 방향으로 정리했다. 기준: 서버 권위·성능 안정·모드팩 일치 전제.

| # | 항목 | 결정 | 근거 |
|---|---|---|---|
| 1 | 휘두르기 감지 | `combat`이 서버에서 직접 `SWING`을 발행(`combat-spec.md`) — 별도 감지 불필요 | 이미 해소 |
| 2 | 파티클·소리 리소스 | **바닐라 파티클·소리를 기본**으로 쓰고, **자체 파티클 타입은 5종 이내**로 제한. 리소스는 `economycore` 모드 jar에 포함. 모드팩 일치가 접속 조건이므로 미적용 클라이언트 대체 동작은 별도 구현하지 않고 `quality: off`로만 처리 | 배포 단순, 리소스 관리 부담 최소화 |
| 3 | 클라이언트 전용 액션 범위 | **FX3에서 화면 흔들림 + 상세도 옵션부터** 구현. 궤적 리본·히트스톱은 FX3 후반/후순위(효과 대비 구현 비용이 큼) | 단계적 투자, 접근성 먼저 |
| 4 | 예산 기본값 | 문서 4장의 값(효과당 40, 플레이어당 400/초, 서버 12,000/초)을 시작값으로 확정하고 실측 후 조정. 부하 시 자동 축소는 **켬** | 시작값 명확화 |
| 5 | fx 스킨 | **계정 귀속(거래 불가)**, 획득은 Coin 구매·업적·이벤트. 한정 스킨 복각 정책은 운영 방침(`cosmetics-social-spec.md` 8번 미확정)에서 결정 | 거래 시장 복잡도 회피, 치장 가치 보호 |
| 6 | 범위(원뿔) 공격 | **도입 확정**(`combat-spec.md`). 호 이펙트와 판정이 같은 기하 함수를 공유 | 시각·판정 일치 |
| 7 | LR 이식 시 클라이언트 전용 이벤트 | 이식 단계(FX5)에서 클라이언트 `MeleePreAttackEvent`를 **서버로 중계하는 커스텀 패킷**으로 연결하되, 서버가 검증한 `ValidatedMeleeHit`을 우선 신뢰하고 중계 이벤트는 **연출용**으로만 쓴다 | 보상·판정은 서버 검증 데이터만 |
| 8 | 오라(`HOLD_TICK`) | **`enhance_level ≥ 5`부터** 활성, 주기 ≥ 5틱, 시야 32블록 컬링, 한 화면 동시 오라 수 상한(예: 8명) 초과 시 먼 순으로 생략 | 상시 비용 통제, 강화 진행감 |

### 11.1 결정 후 남는 확인 항목

- 자체 파티클 5종의 구체 목록과 텍스처 제작
- 상세도 옵션의 클라이언트 UI 위치(메인 메뉴 설정)
- 실측으로 예산 기본값 재조정
