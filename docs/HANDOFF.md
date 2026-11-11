# 작업 인계 지시서 (HANDOFF)

> 목적: 컨텍스트가 소진되어 **새 세션이 이어받을 때** 이 문서만 읽고 같은 품질로 작업을 계속할 수 있게 한다.
> 마지막 갱신: 2026-11-11 · 브랜치 `claude/minecraft-server-planning-ce4wna` (저장소 `ikada1029/repo1`)
> 이 문서가 오래되면 `git log`와 `docs/spec/CHANGELOG-v0.2.md`가 정본이다.

## 0. 새 세션 시작 방법

1. 저장소를 확인한다: `git status && git log --oneline | head`. 작업 브랜치는 **`claude/minecraft-server-planning-ce4wna`** 이며 모든 커밋·푸시는 이 브랜치에만 한다(다른 브랜치·PR 금지, 사용자가 명시하지 않는 한).
2. 읽는 순서(약 30분): 이 문서 → `docs/spec/CHANGELOG-v0.2.md` → `docs/spec/minecraft-neoforge-spec-v0.2-draft.md`의 1·6·15·17장 → 관심 영역의 `docs/*-spec.md`.
3. 사용자의 이번 요청을 확인하고 **9장 "다음 작업 후보"** 와 대조한다. 8장의 "사용자 결정 대기" 항목은 임의로 확정하지 않는다.
4. 첫 응답 전에 `python3 -I tools/weapon_catalog/gen.py --check`로 카탈로그 검증이 통과하는지 확인하면 환경이 정상인지 알 수 있다.

**새 세션에 붙여 넣을 시작 프롬프트(예):**

```text
저장소 docs/HANDOFF.md를 먼저 읽고 이어서 작업해줘. 브랜치는 claude/minecraft-server-planning-ce4wna.
이번에 할 일: <여기에 요청>. 결정이 필요한 부분은 HANDOFF 8장 기준으로 물어보고, 권장안은 "제안"으로 표시해줘.
```

## 1. 프로젝트 한 장 요약

- **무엇:** Minecraft Java 1.21.1 + NeoForge **경제·장비강화 서버**. 장비 강화가 메인 콘텐츠, 생활 직업 4종(농부·광부·요리사·어부)은 재화·재료 공급, 수집·보스·주거·가구 뽑기·거래·시장경제가 재화 소비·순환을 만든다. 재화 `Coin`은 비현금(현금 과금 없음).
- **현재 단계:** **기획 단계**(코드 없음). 산출물은 `docs/`의 명세·규격 문서, `data/`의 데이터·시뮬레이션 워크북, `tools/`의 생성기. 다음 큰 단계는 코어 모드 C0(프로젝트 골격)·G1 모드 실기동 검증이다.
- **명세 정본:** `docs/spec/minecraft-neoforge-spec-v0.2-draft.md`(v0.1 업로드 원본의 사본 + v0.2 결정 반영). 원본 업로드 파일은 이전 세션의 임시 경로에만 있었으므로 **이 사본이 작업 기준**이다.
- **핵심 구조 결정:** 서드파티 모드(TaCZ·LR·요리·가구·낚시 등)는 콘텐츠 공급자, 통제(레시피 필터·내구도·복제 방지·피해 계산)는 **자체 코어 모드 `economycore`**가 담당한다. 장비는 우리가 등록한 신규 아이템 + **서버 권위 범위 공격**으로 구현한다(기존 자체 검 강화 모드는 폐기).

## 2. 저장소·작업 규칙

| 항목 | 규칙 |
|---|---|
| 브랜치 | `claude/minecraft-server-planning-ce4wna` 에 개발·푸시. `git push -u origin <브랜치>` |
| 커밋 메시지 | 한국어 간결 제목 + 본문은 필요 시. **끝에 다음 두 줄**(시스템 지시): `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>` / `Claude-Session: https://claude.ai/code/session_01S1xfVw6XYPwQ2ecSewZ6R9` (세션이 바뀌면 해당 세션의 지시를 따른다). 커밋·PR에 **모델 이름 등 식별자를 임의로 넣지 않는다**(시스템이 지정한 trailer만) |
| PR | **사용자가 요청하기 전에는 만들지 않는다.** 만들면 `.github/pull_request_template.md` 확인 |
| 푸시 실패 | 403이면 GitHub 앱 권한 문제(이전에 한 번 발생, 이후 해결). 네트워크 오류만 재시도 |
| 임시 파일 | 스크래치 디렉터리 사용. `__pycache__`·`data/g3/_tmp*.xlsx`는 `.gitignore` |
| 문서 위치 | 설계·규격은 `docs/`, 데이터는 `data/`, 생성 스크립트는 `tools/` |
| 에셋 | **TaCZ·LR 에셋의 키프레임·모델·텍스처를 복사·변형하지 않는다**(ND/ARR). 새 에셋은 자체 제작(`provenance: original`) |

## 3. 사용자 협업 방식(관찰된 선호)

- **한국어**로 답하고, 결론을 앞에 두며 **표·짧은 불릿**을 선호한다. 작업 후에는 "무엇을 만들었는지 / 알게 된 것 / 한계 / 다음 작업 선택지"를 제시한다.
- 요청이 "~해줘/반영해줘/그려줘"이면 **파일로 만들어 커밋·푸시**한다. 질문형("가능할까?")이면 먼저 답하고, 이전 패턴상 관련 문서까지 함께 갱신하는 경우가 많았다.
- **"요하는 부분들은 네가 이상적인 방향으로 글로 작성"** 처럼 결정을 위임하면 **권장안을 "제안"으로 표시**해 문서에 기록한다(언제든 변경 가능하다고 명시).
- **확인하지 못한 것은 확인하지 못했다고 쓴다**(라이선스 전문, 서식의 시각 확인, 소스 정독 범위, 2차 출처 등). 법률 자문 아님 단서를 유지한다.
- 수치는 모두 **[제안]** 표기. 시뮬레이션·워크북의 기본 입력은 임시값이며 실측으로 교체해야 한다고 항상 밝힌다.
- 불필요한 질문을 피한다. 정말 막힌 결정만 묻는다(예: 결정 대기 항목).

## 4. 결정 로그

**사용자 확정(변경 시 사용자 확인 필요)**

| # | 결정 | 근거 문서 |
|---|---|---|
| 1 | 가구 뽑기 **등급 폐지**(균등 풀 1/N) | `spec-9.3-revision.md` |
| 2 | 요리 **타이밍 판정 폐지** → 조리 시간 + **플레이어 단위 쿨타임**, 품질은 레벨·도구 티어의 **결정적 보정(B안)** | `server-core-mod-spec.md` D-001·D-003·D-004 |
| 3 | 조리 제어: 코어 제어 가능하면 모드 B, 불가 시 서드파티 블록 방식(모드 A) + 최소 방어층 | D-005 |
| 4 | 기존 자체 검 강화 모드 **폐기**. **신규 아이템 + 자체 서버 권위 범위 공격** | D-007, `combat-spec.md` |
| 5 | **이펙트 먼저 구현**, LR 이식은 가능하면 나중에(모션은 선택) | D-006, `fx-spec.md` |
| 6 | 쌍검 = **세트 1개 = 아이템 1개**(A안) | `combat-spec.md` 12장 |
| 7 | 현금 과금 **없음**(법적 검토 불필요, NC 조건 유지) | 명세 1.1 |
| 8 | 운영 정책(G6) **생략** | HANDOFF 7장 |
| 9 | 에셋 수정 대상은 TaCZ·LR뿐 → 수정물 배포 불가이므로 **자체 제작** | `mod-license-survey.md` |
| 10 | TaCZ·LR는 **공식 1.21.1 NeoForge 빌드 사용**(비공식 포트·직접 포팅 불필요) | `mod-license-survey.md` 0장 |
| 11 | 치장·소셜 **1순위 4종**(칭호 조건·이름 꾸미기·프로필·알림/랭킹) | `cosmetics-social-spec.md` |
| 12 | 시작 무기: 서버 시작 시 **목제 무기 중 1개 선택** | `starter-weapon-spec.md` |

**사용자가 "권장안으로 작성"을 위임한 항목(제안, 변경 가능)**: 크리티컬=점프 방식, 바닐라 보정 미적용, 블록 채굴 금지, PvP 기본 끔, 지연 보상은 허용 오차 우선, 진화 시 강화 이월 50%, 귀속 정책(T4~T5 귀속), 진화 트리 분기≤2, fx 스킨 귀속, 오라 +5부터 등.

**제안 상태(채택 미정)**: 강화 파괴 완화 추천 조합(안전 구간 8미만 + 보호권 10단계~1,500 + 환급 30%), 가구 풀 N=68·1회 560 Coin·선택 천장 K=1.5N·조각 X=0.5N, 특수 효과 해금 단계·DPS 15% 상한, 무기 카탈로그 361종(선별 전).

## 5. 산출물 인덱스

| 파일 | 내용 | 상태 |
|---|---|---|
| `docs/spec/minecraft-neoforge-spec-v0.2-draft.md` | **명세 정본(v0.2 초안)** | 결정 반영 완료, 정독 검토 미실시 |
| `docs/spec/CHANGELOG-v0.2.md` | v0.1→v0.2 변경 목록(절별) | 최신 |
| `docs/spec-9.3-revision.md` | 가구 뽑기 9.3 개정 요약 | 완료 |
| `docs/server-core-mod-spec.md` | 코어 모드 규격(guard.recipe/craft/durability/command/identity/melee, cooking, 결정 D-001~D-007, 단계 C0~C5) | 완료(구현 전) |
| `docs/combat-spec.md` | 신규 아이템·서버 권위 범위 공격·쌍검·결정(11장) | 완료 |
| `docs/gearbridge-spec.md` | 장비 계층↔경제 서비스 인터페이스, 강화 트랜잭션, GB-1~5 | 완료 |
| `docs/fx-spec.md` | 이펙트 시스템(트리거·액션·예산·LR 이식) | 완료 |
| `docs/special-effects-spec.md` | 특수 효과(해금·가드레일·테마 팩 6종 수치 12장) | 완료 |
| `docs/weapon-archetypes-spec.md` | 아키타입 6종 상세(+DPS 검산) | 완료(나머지 9종은 `data/`·`weapon-catalog.md`) |
| `docs/weapon-catalog.md`, `weapon-catalog-list.md` | 카탈로그 361종 구조·사용법·전체 목록(자동 생성) | 선별 전 |
| `docs/starter-weapon-spec.md` | 시작 무기 선택 규격 | 완료 |
| `docs/cosmetics-social-spec.md` | 치장·소셜 1순위 4종 규격 | 완료 |
| `docs/asset-requirements.md` | 시작 무기 모델·UI·아이콘 요구 목록 | 완료 |
| `docs/g5-wireframes.md`, `g5-wireframes-2.md` | 와이어프레임 약 50화면(W-01~W-116, W-61 개정) | 완료(직업별 월드 HUD·길드 제외) |
| `docs/c0-spike-plan.md`, `economycore/` | **C0 스파이크 계획**(Q1~Q12, S0~S13)과 Gradle 프로젝트 골격 초안 | 계획 완료, 골격 미컴파일 |
| `docs/G1-mod-verification-checklist.md` | **G1 모드 검증 체크리스트**(실기동 전 상태) | 체크박스 대부분 미수행 |
| `docs/G3-economy-simulation-sheet.md` | G3 시트 구조 + 구현 상태·결과(13장) | 완료 |
| `data/g3/G3-economy-simulation.xlsx` | G3 워크북(17시트, 수식 약 9천 개, 시나리오·난수 시뮬) | 임시 입력값 |
| `docs/mod-license-survey.md` | 후보 모드 라이선스 조사 | 2차 출처 중심, 전문 확인 필요 |
| `docs/melee-system-findings.md` | TaCZ·LR 소스 분석(근접·식별·공격 흐름·보안) | 분석 완료 |
| `docs/motion-authoring-guide.md` | 모션 제작 가이드(LR 이식 단계용, 선택) | 7장 발견 기록 일부 |
| `data/weapon_catalog/*.json`, `tools/weapon_catalog/gen.py` | 카탈로그 입력·생성기 | 361종, DPS ±0.1% |
| `tools/g3_sheet/build_g3.py` | G3 워크북 생성기(MC 포함) | 최신 |

## 6. 도구 사용법

```bash
# 무기 카탈로그 (표준 라이브러리만)
python3 -I tools/weapon_catalog/gen.py --check            # 검증만
python3 -I tools/weapon_catalog/gen.py                    # 검증 + weapons.json·목록 재생성
python3 -I tools/weapon_catalog/gen.py --expand one_hand_sword_flame   # 전체 gear_def 출력

# G3 워크북 (openpyxl + LibreOffice recalc 필요, 약 1분)
python3 -I tools/g3_sheet/build_g3.py                     # 7시나리오 스냅샷 + 난수 시뮬 포함
python3 -I tools/g3_sheet/build_g3.py --no-snapshot --quick   # 빠른 확인(~10초)
```

- `build_g3.py`는 xlsx 스킬의 `recalc.py`를 호출한다. 기본 경로는 스크립트 상단 `DEFAULT_RECALC`이며 환경이 다르면 `--recalc <경로>`로 지정한다. **재계산 결과의 `total_errors`가 0이어야** 한다.
- 워크북의 난수 시뮬레이션(`MonteCarlo`·`Gacha_Compare`·`Gacha_Flat`·`Enhance_Mitigation`)은 **정적 결과**다(시드 고정). 입력을 바꾸면 스크립트를 다시 실행한다. `Live_Sim`만 `RAND()` 수식이라 열 때마다 값이 바뀐다.
- 입력 수정 위치: Params·Items·JobIncome(부대비용)·Enhance(확률)·Weapons_DPS·Effect_Packs·Housing_Sinks의 **파란 칸**, 또는 스크립트 상단 상수. 생성 파일을 손으로 고치지 않는다.
- **환경 제약(이전 세션):** `modrinth.com`은 이 세션 환경에서 직접 접속 불가(WebSearch는 가능). GitHub 공개 저장소는 `web-fetch` 에이전트나 `add_repo`(읽기 전용 클론: `/home/user/mcmodderanchor/tacz`, `/home/user/lesraisins-studios/lesraisins-tactical-equipements`)로 읽을 수 있었다 — 새 세션에서는 다시 클론해야 한다. 클라우드 컨테이너라 **게임 실행·화면 확인은 불가**(사용자 PC 연결이 필요).

## 7. 현재 상태

| 영역 | 상태 |
|---|---|
| 기획 G0 목표·제약 | 일부(동시접속자 목표 등 미정) |
| **G1 모드 검증** | 체크리스트 작성 + 라이선스·공식 저장소 조사 완료. **실기동 검증 미수행**(서버+클라이언트 2대) |
| G2 정책 결정 | 대부분 완료(결정 로그), 일부 19장 미확정 |
| **G3 경제 시뮬** | **완료**(워크북+문서), 입력은 임시값 |
| G4 인터페이스·데이터 | `gearbridge-spec`·명세 14장 반영 완료 |
| **G5 UX** | **완료**(와이어프레임 약 50화면) |
| G6 운영 정책 | **생략(사용자 결정)** |
| G7 착수 승인 | 미진행(위험 등록부·컷라인·일정 확정 필요) |
| 코드(코어 모드 C0~) | **C0 계획·골격 초안 작성(미컴파일)**, 스파이크 미수행 |

## 8. 사용자 결정 대기 (임의 확정 금지)

1. **요리 모드 조합**(Farmer's Delight 단독 / Kaleidoscope Cookery 단독 / 병행)과 Kaledelights Compat의 1.21.1 빌드 존재 — G1 실기동 비교 후 결정.
2. **무기 카탈로그 선별**: 어떤 아키타입·테마 라인으로 시작할지(권장: 아키타입 3~4개 × 테마 2~3개, 전설 아키타입당 1~2개 + 고유 위주). `data/weapon_catalog/selection.json`에 승인 목록 기입.
3. **강화 파괴 완화 장치 채택**(보호권·안전 구간·환급)과 보호권 가격(단계별 차등 여부).
4. **가구 뽑기 파라미터**: 풀 크기 N, 1회 가격(560 후보), K·X 배수, 시즌 풀 종료 시 조각·목표 처리, 조각 획득 경로 확대.
5. **UI 구현 방식**: 서버 메뉴 vs 커스텀 화면+패킷, 3D 프리뷰.
6. 목표 접속자 수·월드 구조·DB 선택(G0), 직업 변경 쿨타임/수수료 등 명세 19장 항목.
7. **C0 스파이크 실행 위치**(사용자 PC / 컨테이너+호스트 허용)와 코어 모드 라이선스 방침(`mod_license`).
8. TaCZ·LR 저작자에게 **허락 문의**를 보낼지(수정 에셋 사용·무수정 배포 조건·1.21.1 지원 계획).

## 9. 다음 작업 후보 (권장 우선순위)

| 순위 | 작업 | 산출물/완료 조건 | 비고 |
|---|---|---|---|
| 1 | **명세 v0.2 정독 검토·정리** | 오탈자·표·용어·번호 점검, 중복·충돌 제거, 개발 인계용 요약 | 아직 전체 정독 안 함 |
| 2 | **C0 스파이크 실행** — 계획·골격은 작성됨(`docs/c0-spike-plan.md`, `economycore/` 미컴파일 초안) | S0~S13 수행, `docs/c0-spike-results.md` 기록, 가정이 틀린 설계 문서 수정 | **실행 위치 결정 필요**(사용자 PC 권장, 컨테이너는 네트워크 허용 호스트 필요). 허용 호스트: 계획서 2.1 |
| 3 | **G1 실기동 검증 계획서** | 사용자 PC 연결(Remote Control) 절차, 테스트 시나리오, 판정표 템플릿 | 사용자 PC 필요 |
| 4 | 카탈로그 선별 지원 | `selection.json` 초안, 필요 모델·효과 세트 목록, 제작 순서 | 결정 대기 #2 |
| 5 | 목제 한손검 **시험 모델 사양**(변환·해상도·`custom_model_data`) | 모델 제작 지시서 | `asset-requirements.md` 6장 |
| 6 | 직업별 월드 HUD·길드 와이어프레임 | 미작성 화면 보완 | 우선순위 낮음 |
| 7 | 저작자 문의 메일 초안(한/영) | 허락 범위 요청문 | 결정 대기 #7 |
| 8 | 시뮬레이션 확장 | 보호권 단계별 가격 차등, 쿠폰 조각 이벤트, 방어력 상성 | 선택 |

## 10. 알려진 한계·주의

- **모든 수치는 제안값**이다. G3 기본 입력은 기본 시나리오가 통과하도록 맞춘 임시값이며(직업 부대비용·소각 비중 등) 실측으로 교체해야 한다.
- **라이선스 정보는 2차 출처 + 일부 README/LICENSE 확인**이다. Another Furniture·Handcrafted(커스텀), Refurbished/Framework, FTB, Aquaculture 2 전문은 미확인. 법률 자문이 아니다.
- **TaCZ·LR 소스는 근접 관련 파일만 읽었다**(전체 정독 아님). 근접 무기 지원이 LR에 있고 TaCZ 본체 melee는 총기 부속 가격용이라는 결론은 소스 기준이지만, 컴포넌트 공존·속성 수정자 적용 등은 실기동 확인이 필요하다.
- `GearBridge`·`combat`의 NeoForge 클래스·이벤트 이름은 **후보**이다(정확한 API는 1.21.1 코드로 확인). 특히 공격 의도 수집, 바닐라 공격 취소·휩쓸기 차단, `custom_model_data` 모델 선택.
- 워크북·와이어프레임의 **시각적 서식/레이아웃을 눈으로 확인하지 못했다**(값·수식 오류만 검증).
- 이 세션에서 전체 문서를 일관성 검토하지 않았다 — 문서 간 숫자 불일치(예: 카탈로그 361종, 워크북 시트 17개/수식 수)는 최신 생성 결과를 정본으로 한다.
- 명세 사본의 6.1 등 신규 서술은 규격 문서의 **요약**이다. 충돌 시 개별 규격 문서(`docs/*-spec.md`)가 상세 정본이다.

## 11. 상태 확인 명령

```bash
git status --short && git log --oneline | head -5
python3 -I tools/weapon_catalog/gen.py --check                  # 361종, DPS 편차 ±0.1%
python3 - <<'PY'
from openpyxl import load_workbook
wb = load_workbook('data/g3/G3-economy-simulation.xlsx', data_only=True)
print(wb.sheetnames)               # 17개 시트
print(wb['Dashboard']['C23'].value) # 예: '17 / 18 통과'(전설 P90 비용 판정 1건 '검토')
PY
```

- 기대 상태: 워크북 Dashboard 기본 시나리오 **17/18 통과**(전설 첫 획득 P90 ÷ 월소득 판정은 등급 천장 구조 기준이라 "검토"로 남아 있음 — 가구 등급 폐지로 의미가 약해졌다).

## 12. 용어·약어

| 약어 | 뜻 |
|---|---|
| G0~G7 | 기획 단계(목표·모드 검증·정책·경제 시뮬·인터페이스·UX·운영·착수) |
| C0~C5 | 코어 모드 개발 단계 |
| CB0~CB5 / FX0~FX5 / SE0~SE4 / GB0~GB4 / S1~S5 | 전투 / 이펙트 / 특수 효과 / 장비 연동 / 치장·소셜 단계 |
| 모드 A / 모드 B | 조리 제어: A=서드파티 블록 방식 + 최소 방어층, B=코어 제어(연출 재사용) |
| T0~T5 | 장비 티어(목제=시작 … 전설) |
| `gear_key` | `(item_id, def_id)` — 장비 종류 키. `serial` = 개별 장비 UUID |
| F0~F7 (`Gacha_Flat`) | 균등 풀 가구 뽑기 구조 비교(F7=추천 후보: 선택 천장 1.5N + 조각 0.5N) |
| E0~E6 (`Enhance_Mitigation`) | 강화 파괴 완화 구조 비교(E6=추천 조합) |
| ND / ARR | CC BY-NC-ND(변경 금지) / All Rights Reserved |

## 13. 상위 리스크 (위험 등록부 초안)

| # | 리스크 | 영향 | 대응 |
|---|---|---|---|
| 1 | TaCZ·LR 1.21.1 조합이 실기동에서 충돌/성능 문제 | 총기 콘텐츠 | G1 최우선 검증, 컷라인(총기 제외 시에도 서버 성립) |
| 2 | TaCZ·LR 에셋 라이선스(ND/ARR)로 수정·재배포 불가 | 연출·치장 | 자체 제작 에셋, 저작자 허락 문의 |
| 3 | 코어의 레시피 필터가 믹스인 없이 불가능 | 제작 통제 | C0 스파이크로 조기 확인 |
| 4 | 서드파티 조리 블록의 연출을 코어 제어 아래 재사용 불가 | 요리 UX | 모드 A 폴백 설계 완료 |
| 5 | 임시 경제 수치가 실측과 크게 다름 | 밸런스 | P2 이후 실측으로 G3 입력 교체, 시나리오 점검 |
| 6 | 컴포넌트 공존/동기화 문제(`economycore:*`) | 장비 식별 | GB0 스파이크 |
| 7 | 포크·모드 유지보수 부담(TaCZ 2.x 전환 등) | 장기 | 버전 고정·locklist, 변경 모니터링 |
