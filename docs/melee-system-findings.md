# TaCZ·LR 근접 무기 시스템 분석 (1.21.1 브랜치, 2026-11-11)

> 대상: `MCModderAnchor/TACZ`(1.21.1) · `LesRaisins-Studios/LesRaisins-Tactical-Equipements`(1.21.1) 소스를 얕은 클론으로 읽은 결과.
> 이 문서는 **구조와 필드 이름**만 기록한다. 에셋(키프레임·모델) 값은 복사하지 않는다(TaCZ 에셋 CC BY-NC-ND, LR 에셋 ARR — `motion-authoring-guide.md` 0장).
> 한계: 코드 전체를 정독한 것이 아니라 근접 관련 파일을 선별해 읽었다. `[확인 필요]`는 후속 확인 대상.

## 1. 결론

1. **LR에 근접 무기 시스템이 실제로 있다.** 이전에 README만 보고 "근접 언급 없음"이라 한 것은 불완전했다. 단검·카람빗·야구방망이 3종이 데이터 기반 근접 무기로 들어 있다.
2. **TaCZ 본체의 "melee"는 총기의 근접 공격**(총구·개머리판 가격, `GunMeleeData`)이며, 검 같은 별도 근접 무기 타입이 아니다. 근접 무기는 LR이 제공한다.
3. 근접 무기는 **데이터(JSON) + 애니메이션(JSON) + 상태 머신(Lua) + 모델** 조합이라서, 새 무기를 만드는 데 **Java 코드가 필수가 아니다**(데이터 팩 방식).
4. **공격 속도·피해·쿨다운은 서버가 관리하고 애니메이션 길이와 독립**이다(`delay`·`cooldown`이 틱 단위 데이터). 앞서 걱정한 "모션 길이 = DPS" 문제가 구조적으로 분리되어 있다. **단, 타격 대상 선정은 클라이언트가 한다**(10장 정정 참고).
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
| 공격 속도·피해 | 쿨다운과 피해 적용은 서버가 처리하고 애니메이션과 독립 → G3 밸런스에서 모션 길이가 DPS를 바꾸지 않는다. 공격 속도는 `cooldown` 값으로 통제. **대상 선정은 클라이언트 신뢰**(10장), 코어 모드의 서버 재검증 필요. |
| 무한 내구도 | 데이터 값으로 가능(`max_durability: 0`). 코어 모드의 `guard.durability`는 보조 역할. |
| 콤보·차별화(무수정 에셋 범위) | `attack` 배열(콤보), `factor/knockback/cooldown/delay/hitbox/movement`, 무기별 `sounds`, 우리가 만든 새 Lua 상태 머신으로 기존 애니메이션의 **선택 순서**를 바꾸는 것은 에셋 파일을 수정하지 않는다(단, ARR/ND 해석상 "재배열" 여부는 저작자 확인 권장). |
| 신규 모션 | 우리가 만든 `.animation.json` + 우리 geo 모델 + 우리 상태 머신 → **자체 에셋**. 뼈 이름 규칙(`root/lefthand/righthand/weapon/camera` 등)을 맞춘다. |
| 레시피 | LR이 근접 무기 제작법(`recipe/melee`)과 대장간 블록(`smith_table`)을 포함 → **코어 레시피 필터(C1) 대상**. |
| 강화 연동 | 검의 강화 단계·시리얼을 어디에 저장할지(아이템 데이터 컴포넌트) 확인 필요. `[확인 필요]` |
| 3인칭 | 단검에는 3인칭 애니메이션이 없고 야구방망이에만 있다. 3인칭 모션 필요 여부는 별도 결정. |

## 9. 후속 확인 항목

- [x] 데이터 컴포넌트·아이템 식별 방식 확인 → 10장 (단일 아이템 + `CUSTOM_DATA`의 `MeleeWeaponId`/`DisplayId`)
- [ ] 우리 키(시리얼·강화 단계)를 `CUSTOM_DATA`에 추가했을 때 LR·TaCZ와 충돌 없는지 실기동 확인
- [ ] 서버 측 근접 공격 후킹 방식(포크/믹스인/이벤트) 결정과 `guard.melee` 규격
- [ ] `type`의 종류(`lrtactical:normal` 외)와 사용자 정의 타입 등록 가능성
- [ ] Lua 스크립트의 라이선스 범위(코드 vs 에셋)
- [ ] 3인칭 플레이어 애니메이터 사용 방식(`player_animator`)과 의존 라이브러리 버전
- [ ] LR이 요구하는 TaCZ 버전(빌드 파일이 TaCZ 1.2.0 NeoForge 빌드를 참조)과 의존 라이브러리(`simplebedrockmodel`, `player-animation-lib`, `cloth-config`) 호환
- [ ] 방패(`flash_shield`)·투척·소모품 스크립트의 재사용 가능성
- [ ] 실제 게임에서의 판정 확인(cone/obb 시각화, 서버 지연 허용)

## 10. 데이터 컴포넌트·아이템 식별·공격 흐름 (소스 확인, 2026-11-11)

### 10.1 아이템 식별 — 모든 근접 무기가 하나의 아이템 ID를 공유한다

- LR의 근접 무기는 **단일 아이템 `lrtactical:melee`**(`MeleeItem`)이며, 무기 종류는 아이템 스택의 `DataComponents.CUSTOM_DATA`(NBT 컴파운드) 안의 문자열 키로 구분한다.
  - `MeleeWeaponId`: 무기 종류 ID(`namespace:path`) — 어떤 무기인지(`getId`).
  - `DisplayId`(선택): **외형(모델·애니메이션·상태 머신·소리) 오버라이드 ID** — 없으면 `MeleeWeaponId`를 쓴다(`getDisplayId`).
  - 두 값은 `ICustomItem`/`IMeleeWeapon` 인터페이스(`getId`, `getDisplayId`, `setId`, `isSame`)로 노출된다. 동일 무기 여부(`isSame`)는 `MeleeWeaponId` 비교다.
- 개별 스택 고유 시리얼, 강화 단계 같은 **전용 데이터 컴포넌트는 없다.** LR이 직접 쓰는 컴포넌트는 `CUSTOM_DATA`와 바닐라 `MAX_DAMAGE`/`DAMAGE`/`MAX_STACK_SIZE`뿐이다.
- `CUSTOM_DATA`는 **자유 형식 컴파운드**라서 우리 키(시리얼, 강화 단계, 소유자 등)를 `MeleeWeaponId`와 나란히 추가해도 LR 로직과 충돌하지 않는 구조로 보인다(`setId`는 `CustomData.update`로 해당 키만 갱신). 실제 충돌 여부는 실기동으로 확인한다. `[확인 필요]`

### 10.2 설계에 주는 영향

| 항목 | 영향 |
|---|---|
| 상점·카탈로그 키 | 명세 14.2장의 "`namespace:path`로 아이템 식별"은 이 경우 **레지스트리 ID(`lrtactical:melee`)만으로는 부족**하다. 상점·거래·도감의 키는 **`(item id, MeleeWeaponId)`** 쌍이어야 한다. 코어 모드의 레시피 필터·발급 장부·`GearBridge.getItemIdentity`도 같은 규칙을 쓴다. |
| 시리얼·강화 저장 | `CUSTOM_DATA`에 우리 키를 두거나(기존 규칙 유지), 코어 모드가 **자체 데이터 컴포넌트**(`economycore:identity` 등)를 등록한다. 후자가 타 모드 데이터와 분리되어 안전하다. |
| **외형 치장** | `DisplayId` 오버라이드가 **스탯과 외형을 분리하는 기능을 이미 제공**한다. 같은 무기 종류에 다른 `display`(모델·소리·상태 머신 포함)를 씌울 수 있으므로, 검 외형 스킨(`cosmetics-social-spec.md`)은 새 아이템 없이 구현 가능하다. 단 `display`가 애니메이션과 상태 머신을 함께 지정하므로 외형을 바꾸면 모션도 바뀐다. |
| 진화 트리 | 진화 시 `MeleeWeaponId`(와 필요하면 `DisplayId`)만 교체하면 되고, 아이템 ID는 바뀌지 않는다. |
| 내구도 | 무한 내구도는 데이터(`max_durability: 0`)로 가능하고, 공용 설정 `MELEE_ITEM_CONSUME_DURABILITY`(공통 설정, 불리언)로 **내구도 소모 자체를 끌 수 있다**. 유한 내구도 무기는 `MAX_DAMAGE`/`DAMAGE` 컴포넌트를 설정한다. |
| 인챈트 | 바닐라 인챈트 시스템과 연동된다(`EnchantmentHelper.modifyDamage`, 불꽃 속성, 타격 후 효과). `isEnchantable`이 true이므로 우리 서버의 **별도 인챈트 서비스가 바닐라 인챈트 컴포넌트를 붙이면 효과가 적용된다.** 마법부여대·모루는 코어가 차단한다. |
| 피해 산식 | `기본 = 공격자의 ATTACK_DAMAGE 속성값 × factor`(+ 인챈트 보정, 점프 크리티컬 1.5배). 무기 `attributes`는 `id/amount/operation`(addition, percent, multiply) 목록이다. 속성값이 플레이어 상태에 의존하므로 **강화에 따른 피해 증가는 `factor` 또는 속성 수정자 방식 중 선택**해야 한다. `[확인 필요: 속성 수정자가 스택에 어떻게 적용되는지]` |

### 10.3 공격 처리 흐름 — 정정 및 보안 점검

앞서 "타격 판정은 서버가 처리한다"고 정리한 것은 **부분적으로 틀렸다.** 실제 흐름은 다음과 같다.

```text
[클라이언트] preAttack: 쿨다운 확인 → CPrepareMeleeAttack 전송
[서버]       preAttack: 쿨다운·상태 확인 후 preparingAttack = true, 쿨다운 틱 설정
[클라이언트] delay 틱 후: collectTargets(원뿔/OBB 필터로 대상 선정) → CMeleeAttackRequest(대상 엔티티 ID 배열) 전송
[서버]       postAttack: preparingAttack·actionCount 일치 확인 → weapon.attack(...)
             attack: 대상별로 "거리² ≤ 최대사거리²"만 확인하고 피해·넉백·내구도·소리 처리
```

| 서버가 하는 것 | 클라이언트를 신뢰하는 것 |
|---|---|
| 쿨다운(틱), 준비 상태, 동작 횟수(`actionCount`) 일치 검증 | **누가 맞았는지(대상 목록) 자체** |
| 패킷당 대상 수 상한(`MELEE_MAX_TARGET_PER_PACKET`) | 원뿔 각도·OBB 영역·시야 통과 여부(서버는 재계산하지 않음) |
| 피해 계산·적용, 내구도, 소리 | `delay` 경과 여부(서버가 대기 시간을 강제하지 않음, 준비 상태 + 쿨다운만 확인) |

- **위험:** 변조된 클라이언트는 사거리 안의 임의 엔티티를 대상으로 보낼 수 있다(원뿔 각도·벽 뒤 공격 등). PvE만 있는 서버에서는 영향이 제한적이지만, **PvP를 허용하거나 보스 기여도·랭킹을 쓰면 문제**가 된다(명세 11·12장, `cosmetics-social-spec.md` 4.2).
- **대응(코어 모드 `guard.melee`, 제안):** 서버가 `postAttack` 시점에 `filterTargets`를 **서버에서 재계산해 클라이언트 목록과 교집합만 처리**한다. 구현 방식은 ① LR을 포크해 `postAttack`을 수정(GPL 허용), ② 믹스인으로 후킹, ③ 데미지 이벤트에서 사후 검증 중 선택. 데이터가 아닌 코드 수정이므로 **GPL 소스 제공 의무**가 따른다(`G1-mod-verification-checklist.md` 3.1).
- 공격 쿨다운과 `delay` 검증, 대상 수 상한 설정도 운영 값으로 정리한다.

### 10.4 기타 확인한 API 지점

- `LrTacticalAPI.getMeleeIndex(stack)` / `getMeleeDisplay(stack)`: 인덱스·표시 정보 조회.
- 서버 이벤트: 근접 공격 전후에 걸 수 있는 서버 이벤트는 확인하지 못했다. `MeleePreAttackEvent`는 **클라이언트 전용**(`@OnlyIn(CLIENT)`)이고 서버 후킹 지점은 별도 구현이 필요하다. `[확인 필요]`
- 근접 무기 클래스: `MeleeItem`(Item 상속) + `IMeleeWeapon`. 새 유형은 `MeleeWeaponType`/`ModCustomTypes`로 등록(`type` 필드). `[확인 필요: 사용자 정의 유형의 등록 방식]`
- `CustomItemCoolDowns`(커스텀 쿨다운 저장), `CombatProperties`(플레이어별 공격 상태 — 쿨다운·준비·콤보 카운터).
