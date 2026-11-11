# TaCZ·LR 근접 무기 시스템 분석 (1.21.1 브랜치, 2026-11-11)

> 대상: `MCModderAnchor/TACZ`(1.21.1) · `LesRaisins-Studios/LesRaisins-Tactical-Equipements`(1.21.1) 소스를 얕은 클론으로 읽은 결과.
> 이 문서는 **구조와 필드 이름**만 기록한다. 에셋(키프레임·모델) 값은 복사하지 않는다(TaCZ 에셋 CC BY-NC-ND, LR 에셋 ARR — `motion-authoring-guide.md` 0장).
> 한계: 코드 전체를 정독한 것이 아니라 근접 관련 파일을 선별해 읽었다. `[확인 필요]`는 후속 확인 대상.

## 1. 결론

1. **LR에 근접 무기 시스템이 실제로 있다.** 이전에 README만 보고 "근접 언급 없음"이라 한 것은 불완전했다. 단검·카람빗·야구방망이 3종이 데이터 기반 근접 무기로 들어 있다.
2. **TaCZ 본체의 "melee"는 총기의 근접 공격**(총구·개머리판 가격, `GunMeleeData`)이며, 검 같은 별도 근접 무기 타입이 아니다. 근접 무기는 LR이 제공한다.
3. 근접 무기는 **데이터(JSON) + 애니메이션(JSON) + 상태 머신(Lua) + 모델** 조합이라서, 새 무기를 만드는 데 **Java 코드가 필수가 아니다**(데이터 팩 방식).
4. **타격 판정은 서버가 처리하고 애니메이션 길이와 독립**이다(`delay`·`cooldown`이 틱 단위 데이터). 앞서 걱정한 "모션 길이 = DPS" 문제가 구조적으로 분리되어 있다.
5. **무한 내구도가 기본 지원**된다(`max_durability: 0` = 무한, 파일 주석 기준).

## 2. 파일 구조 (LR 근접 무기 1종 = 아래 5종 파일)

| 역할 | 경로(LR 저장소 기준) | 내용 |
|---|---|---|
| 무기 데이터 | `data/lrtactical/index/melee/<id>.json` | 이름, 툴팁, `type`, `base_item`, `data{...}` |
| 표시 설정 | `assets/lrtactical/display/melee/<id>.json` | 모델·애니메이션·**상태 머신**·텍스처·슬롯 텍스처·소리·변환 |
| 애니메이션 | `assets/lrtactical/animations/melee/<id>.animation.json` | Bedrock 방식 애니메이션 모음 |
| 모델 | `assets/lrtactical/geo_models/melee/<id>_geo.json` | 뼈 구조 모델 |
| 3인칭 | `assets/lrtactical/player_animator/melee/<id>.json` | 3인칭 플레이어 동작(야구방망이에만 존재, 단검은 없음) |
| 상태 머신 | `assets/lrtactical/scripts/default_melee_state_machine.lua` | 입력 → 애니메이션 전환 로직(공용) |
| 제작법 | `data/lrtactical/recipe/melee/<id>.json` | **코어 레시피 필터의 통제 대상** |

## 3. 무기 데이터(`index/melee`) 필드

- 공통: `sort`, `name`, `tooltip`, `type`(예: `lrtactical:normal`), `base_item`(`lrtactical:melee`).
- `data`:
  - `attributes`: 속성 수정자(공격력 `generic.attack_damage`, 이동속도 등, 비율형 지원).
  - `draw_time`, `put_away_time`: 틱.
  - `max_durability`: **0 = 무한 내구도**.
  - `enchantment_value`: 마법 부여 능력(바닐라 인챈트 연동, 우리 서버는 별도 인챈트 서비스라 차단 대상).
  - `attack.attack_left` / `attack.attack_right`: **객체 1개 또는 배열**. 배열이면 공격할 때마다 목록을 순환 → **콤보 체인**.
    - `factor`(피해 배율), `knockback`, `cooldown`(틱), `delay`(출수 지연 틱), `durability_damage`
    - `hitbox`: `cone`(`max_range`, `max_angle`, `exclude_self`) 또는 `obb`(`max_range`, `half_width`, `half_height`, `roll`)
    - `movement`: 돌진(`delay`, `speed`) — 선택
  - 기본값(코드): 쿨다운 20틱, 지연 0, 기본 히트박스 원뿔(거리 3.5, 각도 60), 내구도 피해 1.

관련 Java: `MeleeWeaponData`, `CombatData`(좌/우 공격별 `MeleeAttackInfo` 리스트와 인덱스 순환), 네트워크 `CMeleeAttackRequest`, `CPrepareMeleeAttack`, `SMeleeAnimationSync`.

## 4. 표시 설정(`display/melee`) 필드

`model`, `animation`, **`state_machine`**, `texture`, `slot_texture`, `sounds`(키: `attack_left`, `attack_right`, `attack_left_hit`, `attack_right_hit`, `crit` 등 — 일부는 주석 처리된 예시), `transforms`(`thirdperson_righthand/lefthand`, `ground`, `gui`, `head`, `fixed` 각각 `rotation/translation/scale`).

## 5. 애니메이션 파일 구조

- 형식: `format_version` + `animations{이름: {...}}` (Blockbench/Bedrock 계열).
- 필수 이름(단검 기준 확인): `static_idle`(루프), `draw`, `put_away`, `inspect`, 공격 `melee_1`, `melee_2`, `melee_3`, 이동 `run_start/run/run_end`, `walk_forward/backward/sideway`, `idle`, `put_away_forbidden`.
- 각 애니메이션 항목: `animation_length`, `loop`(`true`/`hold_on_last_frame`/생략=1회), `bones{뼈 이름: 위치·회전 키프레임}`, **`sound_effects`** 키프레임(소리 시점 지정).
- 확인된 뼈 이름: `root`, `lefthand`, `righthand`, `gun_and_righthand`, `weapon`, `camera`, `constraint`, `bullet_new_mag`(총기 규격 잔재) 등 → **모델(geo)의 뼈와 일치해야 한다**.
- 무기마다 파일이 따로 있다(단검·카람빗·야구방망이 각각).

## 6. 상태 머신(Lua)

- `display`의 `state_machine`으로 지정하며 **여러 무기가 공유 가능**(현재 기본 스크립트 1개).
- 구조: **트랙 행**(정적 행: 기본 트랙·메인 트랙 / 혼합 행: 이동 트랙) 위에서 상태(`start`, `idle`, `inspect`, `final`)가 입력(`INPUT_DRAW`, `INPUT_PUT_AWAY`, `INPUT_INSPECT`, `attack_left`, `attack_right`)에 따라 전환하며 `runAnimation(이름, 트랙, 블렌딩, 재생모드, 전환시간)`을 호출한다.
- 공격 입력 처리: 좌공격은 `context:getActionCount("attack_left")`의 홀짝으로 `melee_1`/`melee_2`를 번갈아 재생하고, 우공격은 `melee_3` 고정. → **콤보 순서와 애니메이션 선택은 Lua에서 바꿀 수 있다.**
- 이동 트랙은 정지/달리기/걷기/전술 질주에 따라 별도 애니메이션을 섞는다.
- `[확인 필요]` Lua 스크립트가 `assets/` 아래에 있어 라이선스상 "Art Assets(ARR)"에 포함되는지 코드(GPL)로 보는지 모호하다. 저작자에게 확인한다.

## 7. TaCZ 본체의 근접(참고)

- `GunMeleeData`: `distance`, `cooldown`, `default{...}`(`GunDefaultMeleeData`). 부착물(총구/개머리판)의 `MeleeData`가 우선 적용된다.
- 서버 `LivingEntityMelee`: 총 교체·노리쇠 작동 중에는 불가, `GunMeleeEvent`(취소 가능 이벤트)를 발생시키고, 준비 시간(`prepTime`) 후 `melee()`를 실행, 쿨다운은 5ms 지연 허용 창으로 계산.
- 이 경로는 **총기 부속 가격**용이라 검 시스템의 기반이 아니다.

## 8. 우리 계획에 주는 의미

| 항목 | 의미 |
|---|---|
| 검의 기반 | **LR 근접 시스템을 기반으로 삼는 것이 가능**하다. 데이터 기반이라 신규 검 추가가 쉽다. |
| 서버 판정 | 타격은 서버에서 `delay`/`cooldown`/`hitbox`로 처리되고 애니메이션과 독립 → G3 밸런스에서 모션 길이가 DPS를 바꾸지 않는다. 공격 속도는 `cooldown` 값으로 통제. |
| 무한 내구도 | 데이터 값으로 가능(`max_durability: 0`). 코어 모드의 `guard.durability`는 보조 역할. |
| 콤보·차별화(무수정 에셋 범위) | `attack` 배열(콤보), `factor/knockback/cooldown/delay/hitbox/movement`, 무기별 `sounds`, 우리가 만든 새 Lua 상태 머신으로 기존 애니메이션의 **선택 순서**를 바꾸는 것은 에셋 파일을 수정하지 않는다(단, ARR/ND 해석상 "재배열" 여부는 저작자 확인 권장). |
| 신규 모션 | 우리가 만든 `.animation.json` + 우리 geo 모델 + 우리 상태 머신 → **자체 에셋**. 뼈 이름 규칙(`root/lefthand/righthand/weapon/camera` 등)을 맞춘다. |
| 레시피 | LR이 근접 무기 제작법(`recipe/melee`)과 대장간 블록(`smith_table`)을 포함 → **코어 레시피 필터(C1) 대상**. |
| 강화 연동 | 검의 강화 단계·시리얼을 어디에 저장할지(아이템 데이터 컴포넌트) 확인 필요. `[확인 필요]` |
| 3인칭 | 단검에는 3인칭 애니메이션이 없고 야구방망이에만 있다. 3인칭 모션 필요 여부는 별도 결정. |

## 9. 후속 확인 항목

- [ ] LR 근접 무기 아이템이 가지는 데이터 컴포넌트(시리얼·강화 저장 가능성), `lrtactical:melee` 단일 기반 아이템의 개별 아이템 식별 방식
- [ ] `type`의 종류(`lrtactical:normal` 외)와 사용자 정의 타입 등록 가능성
- [ ] Lua 스크립트의 라이선스 범위(코드 vs 에셋)
- [ ] 3인칭 플레이어 애니메이터 사용 방식(`player_animator`)과 의존 라이브러리 버전
- [ ] LR이 요구하는 TaCZ 버전(빌드 파일이 TaCZ 1.2.0 NeoForge 빌드를 참조)과 의존 라이브러리(`simplebedrockmodel`, `player-animation-lib`, `cloth-config`) 호환
- [ ] 방패(`flash_shield`)·투척·소모품 스크립트의 재사용 가능성
- [ ] 실제 게임에서의 판정 확인(cone/obb 시각화, 서버 지연 허용)
