# economycore — C0 스파이크용 프로젝트 골격 (미컴파일 초안)

> 상태: **이 컨테이너에서는 NeoForge 저장소(`maven.neoforged.net`)와 Mojang 호스트가 막혀 컴파일하지 못했다.** 파일은 `docs/c0-spike-plan.md`의 스파이크 항목(S0~S13)을 시작하기 위한 **미검증 템플릿**이다. NeoForge 1.21.1 API 이름은 실제 컴파일로 확인한다. 각 TODO는 스파이크 ID로 표시했다.

## 버전(참고용: LR·TaCZ 1.21.1 공식 저장소가 쓰는 값)

| 항목 | 값 |
|---|---|
| Minecraft | 1.21.1 |
| NeoForge | 21.1.233 |
| ModDev Gradle 플러그인 | `net.neoforged.moddev` 2.0.74 |
| Parchment | 2024.11.17 |
| Gradle | 8.12 (`gradle wrapper --gradle-version 8.12`로 래퍼 생성) |
| Java | 21 |

## 시작하기 (사용자 PC 또는 허용 호스트가 열린 환경)

```bash
cd economycore
gradle wrapper --gradle-version 8.12      # 래퍼가 없으면 한 번만
./gradlew build                           # S0: 컴파일 확인
./gradlew runServer                       # S0: 전용 서버 기동(--nogui)
./gradlew runClient                       # 클라이언트(2대 시험은 runClient2)
```

## 구성

- `src/main/java/dev/economycore/EconomyCore.java` — 모드 진입점(등록·이벤트 연결)
- `item/GearItem.java`, `component/GearData.java`, `component/ModComponents.java` — 신규 아이템·데이터 컴포넌트(S3)
- `net/AttackIntentPayload.java`, `client/ClientInput.java` — 공격 의도 패킷과 클라이언트 입력(S4)
- `guard/RecipeGuard.java` — 레시피 필터 스텁(S1)
- `command/EconomyCommands.java` — `/economycore reload|status`(S10)
- `config/ConfigService.java` — JSON 설정 로더(S10)
- 라이선스: **미정**(`mod_license=LicenseRef-TBD`). 코어를 TaCZ/LR 코드에 직접 의존시키지 않는 설계(명세 2.2)를 유지하며, 직접 의존이 필요해지면 GPL 적용 범위를 결정한다.
