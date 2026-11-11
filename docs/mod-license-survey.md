# 후보 모드 라이선스 조사 (2026-11-11 웹 검색 기준)

> **신뢰도 주의:** 대부분 모드 호스팅·집계 사이트(Modrinth/CurseForge 목록 미러, moddex, mado-hosting 등)의 2차 정보다. 프로젝트 페이지 원문을 직접 읽지 못했다(이 세션은 modrinth.com 접속 불가). **채택 전에 각 모드의 `LICENSE` 파일과 프로젝트 페이지 라이선스 필드를 직접 확인**하고 이 표를 갱신한다. 법률 자문이 아니다.
> 전제: 현금 과금 없음, 후보 모드는 **수정하지 않고** 사용(설정·데이터팩·이벤트 연동만).

## 1. 요약표

| 모드 | 라이선스(코드) | 에셋 / 비고 | 모드팩 포함·재배포 | 신뢰도 |
|---|---|---|---|---|
| TaCZ 1.21.1 NeoForge 포트 | GPL-3.0-only (집계 사이트) | **에셋 CC BY-NC-ND 4.0 (사용자 확인)**. 원작 TaCZ 라이선스는 이번 검색에서 확인 못 함 | 코드는 GPL 조건(소스 제공). 에셋은 **무수정 배포만**(ND) + 표시(BY) + 비영리(NC) | 중 |
| LR Tactical 1.21.1 NeoForge 포트 | GPL-3.0-only (집계 사이트, 사용자 확인) | **에셋 All Rights Reserved (사용자 확인)** — 코드(GPL)와 에셋 라이선스가 다름 | 코드는 GPL 조건. **에셋은 수정·재배포에 권리자 허락 필요**(무수정 모드팩 포함 가능 여부도 저작자 조건 확인) | 중 |
| Farmer's Delight | MIT (Modrinth·GitHub 목록) | 텍스처/모델 별도 표기 못 찾음 | 코드는 자유. 에셋 표기 확인 필요 | 중 |
| Kaleidoscope Cookery | **CC BY-NC-SA 4.0** | 수정물에는 SA(동일조건) 적용 | 무수정 포함 + 표시, 비영리 | 중 |
| Kaledelights Compat | MIT (CurseForge 페이지) | "에셋은 원저작자 소유" | 코드는 자유 | 중 |
| Aquaculture 2 | **All Rights Reserved** (Modrinth 목록) | 모드 페이지 요약: 모드팩 포함은 출처 표기·링크 조건으로 허용, 단독 재배포·디컴파일·아트워크 재사용 금지 | 모드팩 포함 가능(조건부). 수정·재사용 불가 | 중 |
| Another Furniture | **커스텀 라이선스** (LicenseRef-Custom) | 모드 페이지 FAQ: 모드팩·영상 포함 가능, 저작자 표기, 자기 제작물 주장 금지. 전문 확인 못 함 | 모드팩 포함 가능(표기). 수정 허용 여부는 전문 확인 | 중하 |
| Handcrafted | **커스텀 라이선스** (Terrarium Licence) | 전문 확인 못 함 | 전문 확인 후 판단 | 하 |
| MrCrayfish's Furniture: Refurbished | 코드 MIT (GitHub 미러) | **에셋 권리 유보** (미러 기준), 무수정 빌드는 모드팩 포함 가능 | 무수정 포함 가능. 에셋 수정 불가 | 중하 |
| Framework (Refurbished 의존) | 확인 못 함 | | GitHub `MrCrayfish/Framework`의 LICENSE 직접 확인 | 하 |
| L_Ender's Cataclysm | **CC BY-NC-ND 4.0** | 부가 모드들은 "원 에셋은 저작자 소유"로 표기 | 무수정 포함 + 표시, 비영리. **수정물 배포 불가** | 중 |
| FTB Chunks (NeoForge) | **All Rights Reserved** (FTB 문서의 일괄 정책) | 소스는 GitHub에 공개되나 권리는 유보 | 무수정 사용. 모드팩 조건은 FTB 정책 확인 | 중 |
| Sprinkler (참고) | MIT | 자체 구현 우선 방침이므로 참고만 | 자유 | 중 |
| Better Farming ++ (참고/보류) | **확인 못 함** (비슷한 이름의 다른 모드와 혼동 주의) | | 프로젝트 페이지에서 확인 | 하 |
| Regions Unexplored (보류) | **출처 간 불일치** (Modrinth: MIT / moddex: ARR) | Modrinth 필드가 더 권위 있음 | 채택 시 LICENSE 파일 직접 확인 | 중하 |

## 2. 이 서버 계획에 주는 영향

> **운영 방침(사용자 확인):** 에셋을 수정할 가능성이 있는 모드는 **TaCZ와 LR 둘뿐**이고, 나머지 모드는 에셋을 수정하지 않는다. 따라서 아래 2번의 가구 리폼·Cataclysm 에셋 수정 항목은 **수정하지 않는 한 해당 없음**이며, 라이선스 쟁점은 TaCZ(에셋 CC BY-NC-ND)와 LR(에셋 All Rights Reserved)의 수정 범위로 집중된다. **두 모드 모두 에셋 수정물은 허락 없이 배포할 수 없으므로**, 수정이 필요한 모델·모션은 자체 제작 에셋으로 만들거나 저작자 허락을 받는다.

1. **수정하지 않는 사용은 대체로 가능하다.** 설정·데이터팩·이벤트·명령 수준의 연동(코어 모드 규격의 방식)은 에셋을 변형·재배포하는 것이 아니므로 ND/ARR 모드에도 적용할 수 있다. 다만 "변형해서 배포"에 해당하는지 애매한 방식(런타임 모델 변경, 에셋 오버라이드 리소스팩)은 저작자 확인 후에 쓴다.
2. **ND/ARR 에셋을 수정해야 하는 기능은 막힌다.**
   - 가구 **색상·장식 리폼**(명세 9.4장): Another Furniture·Handcrafted·Refurbished의 모델·텍스처를 변형하는 방식은 허락 없이는 배포 불가. 대안: 이미 존재하는 다른 가구 ID 사용 / 자체 제작 가구 / 저작자 허락.
   - **보스 외형·전리품 에셋 수정**(Cataclysm, ND): 전리품·스폰 제어는 데이터팩·설정으로만 하고 에셋은 건드리지 않는다.
   - **TaCZ 모션 변형·재조합**: 이전 논의대로 자체 제작 에셋으로 대체.
3. **Aquaculture 2(ARR)와 FTB Chunks(ARR)** 는 모드팩 포함 조건(출처 표기·링크)을 지키되 디컴파일·코드 재사용을 하지 않는다. 코어 모드가 내부 클래스에 의존해야 한다면 공개 API·이벤트·데이터 파일 수준으로 제한하고, 필요 시 저작자에게 문의한다.
4. **GPL 계열(TaCZ·LR 코드)**: 클라이언트에 jar를 내려받게 하면 배포에 해당하므로 소스 제공 방법(원본 링크, 수정 시 수정 소스)을 갖춘다. 코어 모드는 이 코드에 직접 의존하지 않는 설계를 우선한다.
5. **CC BY-NC-SA(Kaleidoscope Cookery)** 와 GPL 코드를 한 코드베이스에서 결합하지 않는다(코어 모드 독립 설계 유지).
6. **비영리 전제(NC)**: Kaleidoscope, Cataclysm, TaCZ 에셋 모두 NC. 후원·광고·판매가 생기면 전부 재검토한다.
7. 가구 조합은 **Another Furniture 1종 고정**(명세 권고) 방침이 라이선스 면에서도 유리하다. Handcrafted·Refurbished는 전문 확인 후 도입한다.

## 3. 확인이 남은 항목

- [ ] 원작 TaCZ의 코드·에셋 라이선스(원 저장소) 및 포트 저장소의 라이선스 파일
- [ ] LR 에셋 라이선스
- [ ] Farmer's Delight 에셋 라이선스 표기
- [ ] Another Furniture, Handcrafted 커스텀 라이선스 **전문**
- [ ] Refurbished의 `LICENSE` / `ASSETS_LICENSE`, Framework 라이선스
- [ ] FTB Chunks의 모드팩 포함 조건(FTB 정책 원문)
- [ ] Aquaculture 2 라이선스 전문(디컴파일·API 사용 범위)
- [ ] Better Farming ++, Regions Unexplored (채택 시)
- [ ] 각 모드 **최종 채택 버전**의 라이선스(버전에 따라 바뀔 수 있음)

## 4. 출처(검색 결과)

- TaCZ 포트: [CurseForge](https://www.curseforge.com/minecraft/mc-mods/tacz-1-21-1), [Mado Hosting](https://www.mado-hosting.com/en/minecraft-mods/tacz-1.21.1), [moddex](https://moddex.gg/mod/tacz-1-21-1)
- LR Tactical 포트: [CurseForge](https://www.curseforge.com/minecraft/mc-mods/lr-tactical-1-21-1), [Mado Hosting](https://www.mado-hosting.com/minecraft-mods/lr-tactical-1.21.1), [moddex](https://moddex.gg/mod/lr-tactical-1-21-1)
- Farmer's Delight: [Modrinth(1.21 빌드)](https://modrinth.com/mod/farmers-delight/version/5tKbefI6), [ecosyste.ms](https://awesome.ecosyste.ms/projects/github.com%2Fvectorwing%2FFarmersDelight)
- Kaleidoscope Cookery: [CurseForge](https://www.curseforge.com/minecraft/mc-mods/kaleidoscope-cookery/files/7057534), [Modrinth](https://modrinth.com/mod/kaleidoscope-cookery/version/1.1.2-neoforge+mc1.21.1)
- Kaledelights Compat: [CurseForge](https://www.curseforge.com/minecraft/mc-mods/kaledelights-compat), [ModpackIndex](https://www.modpackindex.com/mod/208776/kaledelights-compat)
- Aquaculture 2: [Modrinth](https://modrinth.com/project/UF9cVDTS), [moddex](https://moddex.gg/mod/aquaculture)
- Another Furniture: [Modrinth](https://modrinth.com/mod/another-furniture), [moddex](https://moddex.gg/mod/another-furniture)
- Handcrafted: [moddex](https://moddex.gg/mod/handcrafted), [Mado Hosting](https://www.mado-hosting.com/en/minecraft-mods/handcrafted)
- Refurbished: [GitHub 미러(README)](https://github.imc.re/MrCrayfish/MrCrayfishFurnitureMod-Refurbished/blob/1.21.1/README.md), [CurseForge](https://www.curseforge.com/minecraft/mc-mods/refurbished-furniture)
- Framework: [CurseForge](https://www.curseforge.com/minecraft/mc-mods/framework)
- Cataclysm: [GDLauncher 미러](https://gdlauncher.com/mods/modrinth/l_enders-cataclysm), [moddex](https://moddex.gg/mod/lendercataclysm)
- FTB Chunks: [FTB 문서](https://feedthebeast.notion.site/FTB-Mod-Documentation-da2e359bad2449459d58d787edda3168), [CurseForge](https://www.curseforge.com/minecraft/mc-mods/ftb-chunks-forge/files/5004644)
- Sprinkler: [Modrinth](https://modrinth.com/mod/sprinkler)
- Better Farming ++: [Mado Hosting](https://www.mado-hosting.com/minecraft-mods/better-farming-plus)
- Regions Unexplored: [Modrinth(1.21.1 NeoForge)](https://modrinth.com/project/Tkikq67H/version/jITSrhFt), [moddex](https://moddex.gg/mod/regions-unexplored)
