# 근접 무기 카탈로그 전체 목록 (자동 생성)

> `tools/weapon_catalog/gen.py`가 생성. 직접 수정하지 말 것. 수치는 [제안], 모든 항목은 `candidate`(후보)이다.
> 총 361종.

| def_id | 이름 | 아키타입 | 티어 | 등급 | 변형 | base_damage | 진화 부모 | 획득 | 귀속 |
|---|---|---|---|---|---|---|---|---|---|
| one_hand_sword_wood | 목제 검 | one_hand_sword | T0 | 시작 | balanced | 6.0 | - | 시작 무기 선택(최초 접속 1회, starter.json 후보 중 1개) | bind_on_acquire |
| one_hand_sword_iron | 철 검 | one_hand_sword | T1 | 일반 | balanced | 6.0 | one_hand_sword_wood | 상점(기본) 또는 목제에서 진화 | tradable |
| one_hand_sword_bronze | 청동 검 | one_hand_sword | T1 | 일반 | heavy | 7.09 | one_hand_sword_wood | 상점(기본) 또는 목제에서 진화 | tradable |
| one_hand_sword_steel | 강철 검 | one_hand_sword | T2 | 고급 | swift | 5.45 | one_hand_sword_iron | 상점(직업 레벨/도감 조건) 또는 철에서 진화 | tradable |
| one_hand_sword_silver | 은 검 | one_hand_sword | T2 | 고급 | swift | 5.45 | one_hand_sword_bronze | 상점(직업 레벨/도감 조건) 또는 청동에서 진화 | tradable |
| one_hand_sword_flame | 불꽃 검 | one_hand_sword | T3 | 희귀 | heavy | 7.09 | one_hand_sword_steel | 강철에서 진화(분기 A) | tradable |
| one_hand_sword_frost | 서리 검 | one_hand_sword | T3 | 희귀 | swift | 5.45 | one_hand_sword_steel | 강철에서 진화(분기 B) | tradable |
| one_hand_sword_thunder | 번개 검 | one_hand_sword | T3 | 희귀 | swift | 5.45 | one_hand_sword_silver | 은에서 진화(분기 A) | tradable |
| one_hand_sword_holy | 성광 검 | one_hand_sword | T3 | 희귀 | balanced | 6.0 | one_hand_sword_silver | 은에서 진화(분기 B) | tradable |
| one_hand_sword_venom | 맹독 검 | one_hand_sword | T3 | 희귀 | balanced | 6.0 | - | 보스 재료 교환(독 계열 보스) | tradable |
| one_hand_sword_shadow | 그림자 검 | one_hand_sword | T3 | 희귀 | swift | 5.45 | - | 보스 재료 교환(그림자 계열 보스) | tradable |
| one_hand_sword_lava | 용암 검 | one_hand_sword | T4 | 영웅 | balanced | 6.0 | one_hand_sword_flame | 불꽃에서 진화(보스 재료) | bind_on_acquire |
| one_hand_sword_glacier | 빙하 검 | one_hand_sword | T4 | 영웅 | balanced | 6.0 | one_hand_sword_frost | 서리에서 진화(보스 재료) | bind_on_acquire |
| one_hand_sword_storm | 폭풍 검 | one_hand_sword | T4 | 영웅 | heavy | 7.09 | one_hand_sword_thunder | 번개에서 진화(보스 재료) | bind_on_acquire |
| one_hand_sword_heaven | 천상 검 | one_hand_sword | T4 | 영웅 | swift | 5.45 | one_hand_sword_holy | 성광에서 진화(보스 재료) | bind_on_acquire |
| one_hand_sword_corrosion | 부식 검 | one_hand_sword | T4 | 영웅 | heavy | 7.09 | one_hand_sword_venom | 맹독에서 진화(보스 재료) | bind_on_acquire |
| one_hand_sword_dark | 암흑 검 | one_hand_sword | T4 | 영웅 | swift | 5.45 | one_hand_sword_shadow | 그림자에서 진화(보스 재료) | bind_on_acquire |
| one_hand_sword_dragon | 화룡 검 | one_hand_sword | T5 | 전설 | heavy | 7.09 | one_hand_sword_lava | 용암에서 진화(최상급 보스 재료) | bind_on_acquire |
| one_hand_sword_polar | 극한 검 | one_hand_sword | T5 | 전설 | balanced | 6.0 | one_hand_sword_glacier | 빙하에서 진화(최상급 보스 재료) | bind_on_acquire |
| one_hand_sword_skybolt | 천뢰 검 | one_hand_sword | T5 | 전설 | heavy | 7.09 | one_hand_sword_storm | 폭풍에서 진화(최상급 보스 재료) | bind_on_acquire |
| one_hand_sword_divine | 신성 검 | one_hand_sword | T5 | 전설 | balanced | 6.0 | one_hand_sword_heaven | 천상에서 진화(최상급 보스 재료) | bind_on_acquire |
| one_hand_sword_plague | 역병 검 | one_hand_sword | T5 | 전설 | heavy | 7.09 | one_hand_sword_corrosion | 부식에서 진화(최상급 보스 재료) | bind_on_acquire |
| one_hand_sword_abyss | 심연 검 | one_hand_sword | T5 | 전설 | swift | 5.45 | one_hand_sword_dark | 암흑에서 진화(최상급 보스 재료) | bind_on_acquire |
| dagger_wood | 목제 단검 | dagger | T0 | 시작 | balanced | 3.0 | - | 시작 무기 선택(최초 접속 1회, starter.json 후보 중 1개) | bind_on_acquire |
| dagger_iron | 철 단검 | dagger | T1 | 일반 | balanced | 3.0 | dagger_wood | 상점(기본) 또는 목제에서 진화 | tradable |
| dagger_bronze | 청동 단검 | dagger | T1 | 일반 | balanced | 3.0 | dagger_wood | 상점(기본) 또는 목제에서 진화 | tradable |
| dagger_steel | 강철 단검 | dagger | T2 | 고급 | balanced | 3.0 | dagger_iron | 상점(직업 레벨/도감 조건) 또는 철에서 진화 | tradable |
| dagger_silver | 은 단검 | dagger | T2 | 고급 | heavy | 3.45 | dagger_bronze | 상점(직업 레벨/도감 조건) 또는 청동에서 진화 | tradable |
| dagger_flame | 불꽃 단검 | dagger | T3 | 희귀 | heavy | 3.45 | dagger_steel | 강철에서 진화(분기 A) | tradable |
| dagger_frost | 서리 단검 | dagger | T3 | 희귀 | swift | 2.55 | dagger_steel | 강철에서 진화(분기 B) | tradable |
| dagger_thunder | 번개 단검 | dagger | T3 | 희귀 | swift | 2.55 | dagger_silver | 은에서 진화(분기 A) | tradable |
| dagger_holy | 성광 단검 | dagger | T3 | 희귀 | balanced | 3.0 | dagger_silver | 은에서 진화(분기 B) | tradable |
| dagger_venom | 맹독 단검 | dagger | T3 | 희귀 | balanced | 3.0 | - | 보스 재료 교환(독 계열 보스) | tradable |
| dagger_shadow | 그림자 단검 | dagger | T3 | 희귀 | swift | 2.55 | - | 보스 재료 교환(그림자 계열 보스) | tradable |
| dagger_lava | 용암 단검 | dagger | T4 | 영웅 | balanced | 3.0 | dagger_flame | 불꽃에서 진화(보스 재료) | bind_on_acquire |
| dagger_glacier | 빙하 단검 | dagger | T4 | 영웅 | balanced | 3.0 | dagger_frost | 서리에서 진화(보스 재료) | bind_on_acquire |
| dagger_storm | 폭풍 단검 | dagger | T4 | 영웅 | swift | 2.55 | dagger_thunder | 번개에서 진화(보스 재료) | bind_on_acquire |
| dagger_heaven | 천상 단검 | dagger | T4 | 영웅 | balanced | 3.0 | dagger_holy | 성광에서 진화(보스 재료) | bind_on_acquire |
| dagger_corrosion | 부식 단검 | dagger | T4 | 영웅 | heavy | 3.45 | dagger_venom | 맹독에서 진화(보스 재료) | bind_on_acquire |
| dagger_dark | 암흑 단검 | dagger | T4 | 영웅 | swift | 2.55 | dagger_shadow | 그림자에서 진화(보스 재료) | bind_on_acquire |
| dagger_dragon | 화룡 단검 | dagger | T5 | 전설 | heavy | 3.45 | dagger_lava | 용암에서 진화(최상급 보스 재료) | bind_on_acquire |
| dagger_polar | 극한 단검 | dagger | T5 | 전설 | balanced | 3.0 | dagger_glacier | 빙하에서 진화(최상급 보스 재료) | bind_on_acquire |
| dagger_skybolt | 천뢰 단검 | dagger | T5 | 전설 | swift | 2.55 | dagger_storm | 폭풍에서 진화(최상급 보스 재료) | bind_on_acquire |
| dagger_divine | 신성 단검 | dagger | T5 | 전설 | balanced | 3.0 | dagger_heaven | 천상에서 진화(최상급 보스 재료) | bind_on_acquire |
| dagger_plague | 역병 단검 | dagger | T5 | 전설 | heavy | 3.45 | dagger_corrosion | 부식에서 진화(최상급 보스 재료) | bind_on_acquire |
| dagger_abyss | 심연 단검 | dagger | T5 | 전설 | swift | 2.55 | dagger_dark | 암흑에서 진화(최상급 보스 재료) | bind_on_acquire |
| dual_blade_wood | 목제 쌍검 | dual_blade | T0 | 시작 | balanced | 4.0 | - | 시작 무기 선택(최초 접속 1회, starter.json 후보 중 1개) | bind_on_acquire |
| dual_blade_iron | 철 쌍검 | dual_blade | T1 | 일반 | balanced | 4.0 | dual_blade_wood | 상점(기본) 또는 목제에서 진화 | tradable |
| dual_blade_bronze | 청동 쌍검 | dual_blade | T1 | 일반 | heavy | 4.53 | dual_blade_wood | 상점(기본) 또는 목제에서 진화 | tradable |
| dual_blade_steel | 강철 쌍검 | dual_blade | T2 | 고급 | balanced | 4.0 | dual_blade_iron | 상점(직업 레벨/도감 조건) 또는 철에서 진화 | tradable |
| dual_blade_silver | 은 쌍검 | dual_blade | T2 | 고급 | swift | 3.47 | dual_blade_bronze | 상점(직업 레벨/도감 조건) 또는 청동에서 진화 | tradable |
| dual_blade_flame | 불꽃 쌍검 | dual_blade | T3 | 희귀 | heavy | 4.53 | dual_blade_steel | 강철에서 진화(분기 A) | tradable |
| dual_blade_frost | 서리 쌍검 | dual_blade | T3 | 희귀 | swift | 3.47 | dual_blade_steel | 강철에서 진화(분기 B) | tradable |
| dual_blade_thunder | 번개 쌍검 | dual_blade | T3 | 희귀 | heavy | 4.53 | dual_blade_silver | 은에서 진화(분기 A) | tradable |
| dual_blade_holy | 성광 쌍검 | dual_blade | T3 | 희귀 | balanced | 4.0 | dual_blade_silver | 은에서 진화(분기 B) | tradable |
| dual_blade_venom | 맹독 쌍검 | dual_blade | T3 | 희귀 | balanced | 4.0 | - | 보스 재료 교환(독 계열 보스) | tradable |
| dual_blade_shadow | 그림자 쌍검 | dual_blade | T3 | 희귀 | swift | 3.47 | - | 보스 재료 교환(그림자 계열 보스) | tradable |
| dual_blade_lava | 용암 쌍검 | dual_blade | T4 | 영웅 | heavy | 4.53 | dual_blade_flame | 불꽃에서 진화(보스 재료) | bind_on_acquire |
| dual_blade_glacier | 빙하 쌍검 | dual_blade | T4 | 영웅 | balanced | 4.0 | dual_blade_frost | 서리에서 진화(보스 재료) | bind_on_acquire |
| dual_blade_storm | 폭풍 쌍검 | dual_blade | T4 | 영웅 | swift | 3.47 | dual_blade_thunder | 번개에서 진화(보스 재료) | bind_on_acquire |
| dual_blade_heaven | 천상 쌍검 | dual_blade | T4 | 영웅 | balanced | 4.0 | dual_blade_holy | 성광에서 진화(보스 재료) | bind_on_acquire |
| dual_blade_corrosion | 부식 쌍검 | dual_blade | T4 | 영웅 | heavy | 4.53 | dual_blade_venom | 맹독에서 진화(보스 재료) | bind_on_acquire |
| dual_blade_dark | 암흑 쌍검 | dual_blade | T4 | 영웅 | swift | 3.47 | dual_blade_shadow | 그림자에서 진화(보스 재료) | bind_on_acquire |
| dual_blade_dragon | 화룡 쌍검 | dual_blade | T5 | 전설 | heavy | 4.53 | dual_blade_lava | 용암에서 진화(최상급 보스 재료) | bind_on_acquire |
| dual_blade_polar | 극한 쌍검 | dual_blade | T5 | 전설 | swift | 3.47 | dual_blade_glacier | 빙하에서 진화(최상급 보스 재료) | bind_on_acquire |
| dual_blade_skybolt | 천뢰 쌍검 | dual_blade | T5 | 전설 | swift | 3.47 | dual_blade_storm | 폭풍에서 진화(최상급 보스 재료) | bind_on_acquire |
| dual_blade_divine | 신성 쌍검 | dual_blade | T5 | 전설 | balanced | 4.0 | dual_blade_heaven | 천상에서 진화(최상급 보스 재료) | bind_on_acquire |
| dual_blade_plague | 역병 쌍검 | dual_blade | T5 | 전설 | heavy | 4.53 | dual_blade_corrosion | 부식에서 진화(최상급 보스 재료) | bind_on_acquire |
| dual_blade_abyss | 심연 쌍검 | dual_blade | T5 | 전설 | swift | 3.47 | dual_blade_dark | 암흑에서 진화(최상급 보스 재료) | bind_on_acquire |
| greatsword_wood | 목제 대검 | greatsword | T0 | 시작 | balanced | 10.0 | - | 시작 무기 선택(최초 접속 1회, starter.json 후보 중 1개) | bind_on_acquire |
| greatsword_iron | 철 대검 | greatsword | T1 | 일반 | balanced | 10.0 | greatsword_wood | 상점(기본) 또는 목제에서 진화 | tradable |
| greatsword_bronze | 청동 대검 | greatsword | T1 | 일반 | heavy | 11.4 | greatsword_wood | 상점(기본) 또는 목제에서 진화 | tradable |
| greatsword_steel | 강철 대검 | greatsword | T2 | 고급 | balanced | 10.0 | greatsword_iron | 상점(직업 레벨/도감 조건) 또는 철에서 진화 | tradable |
| greatsword_silver | 은 대검 | greatsword | T2 | 고급 | heavy | 11.4 | greatsword_bronze | 상점(직업 레벨/도감 조건) 또는 청동에서 진화 | tradable |
| greatsword_flame | 불꽃 대검 | greatsword | T3 | 희귀 | heavy | 11.4 | greatsword_steel | 강철에서 진화(분기 A) | tradable |
| greatsword_frost | 서리 대검 | greatsword | T3 | 희귀 | swift | 9.0 | greatsword_steel | 강철에서 진화(분기 B) | tradable |
| greatsword_thunder | 번개 대검 | greatsword | T3 | 희귀 | swift | 9.0 | greatsword_silver | 은에서 진화(분기 A) | tradable |
| greatsword_holy | 성광 대검 | greatsword | T3 | 희귀 | balanced | 10.0 | greatsword_silver | 은에서 진화(분기 B) | tradable |
| greatsword_venom | 맹독 대검 | greatsword | T3 | 희귀 | balanced | 10.0 | - | 보스 재료 교환(독 계열 보스) | tradable |
| greatsword_shadow | 그림자 대검 | greatsword | T3 | 희귀 | heavy | 11.4 | - | 보스 재료 교환(그림자 계열 보스) | tradable |
| greatsword_lava | 용암 대검 | greatsword | T4 | 영웅 | balanced | 10.0 | greatsword_flame | 불꽃에서 진화(보스 재료) | bind_on_acquire |
| greatsword_glacier | 빙하 대검 | greatsword | T4 | 영웅 | balanced | 10.0 | greatsword_frost | 서리에서 진화(보스 재료) | bind_on_acquire |
| greatsword_storm | 폭풍 대검 | greatsword | T4 | 영웅 | swift | 9.0 | greatsword_thunder | 번개에서 진화(보스 재료) | bind_on_acquire |
| greatsword_heaven | 천상 대검 | greatsword | T4 | 영웅 | balanced | 10.0 | greatsword_holy | 성광에서 진화(보스 재료) | bind_on_acquire |
| greatsword_corrosion | 부식 대검 | greatsword | T4 | 영웅 | balanced | 10.0 | greatsword_venom | 맹독에서 진화(보스 재료) | bind_on_acquire |
| greatsword_dark | 암흑 대검 | greatsword | T4 | 영웅 | swift | 9.0 | greatsword_shadow | 그림자에서 진화(보스 재료) | bind_on_acquire |
| greatsword_dragon | 화룡 대검 | greatsword | T5 | 전설 | heavy | 11.4 | greatsword_lava | 용암에서 진화(최상급 보스 재료) | bind_on_acquire |
| greatsword_polar | 극한 대검 | greatsword | T5 | 전설 | balanced | 10.0 | greatsword_glacier | 빙하에서 진화(최상급 보스 재료) | bind_on_acquire |
| greatsword_skybolt | 천뢰 대검 | greatsword | T5 | 전설 | swift | 9.0 | greatsword_storm | 폭풍에서 진화(최상급 보스 재료) | bind_on_acquire |
| greatsword_divine | 신성 대검 | greatsword | T5 | 전설 | balanced | 10.0 | greatsword_heaven | 천상에서 진화(최상급 보스 재료) | bind_on_acquire |
| greatsword_plague | 역병 대검 | greatsword | T5 | 전설 | balanced | 10.0 | greatsword_corrosion | 부식에서 진화(최상급 보스 재료) | bind_on_acquire |
| greatsword_abyss | 심연 대검 | greatsword | T5 | 전설 | heavy | 11.4 | greatsword_dark | 암흑에서 진화(최상급 보스 재료) | bind_on_acquire |
| spear_wood | 목제 창 | spear | T0 | 시작 | swift | 6.31 | - | 시작 무기 선택(최초 접속 1회, starter.json 후보 중 1개) | bind_on_acquire |
| spear_iron | 철 창 | spear | T1 | 일반 | balanced | 6.8 | spear_wood | 상점(기본) 또는 목제에서 진화 | tradable |
| spear_bronze | 청동 창 | spear | T1 | 일반 | heavy | 7.77 | spear_wood | 상점(기본) 또는 목제에서 진화 | tradable |
| spear_steel | 강철 창 | spear | T2 | 고급 | balanced | 6.8 | spear_iron | 상점(직업 레벨/도감 조건) 또는 철에서 진화 | tradable |
| spear_silver | 은 창 | spear | T2 | 고급 | swift | 6.31 | spear_bronze | 상점(직업 레벨/도감 조건) 또는 청동에서 진화 | tradable |
| spear_flame | 불꽃 창 | spear | T3 | 희귀 | heavy | 7.77 | spear_steel | 강철에서 진화(분기 A) | tradable |
| spear_frost | 서리 창 | spear | T3 | 희귀 | heavy | 7.77 | spear_steel | 강철에서 진화(분기 B) | tradable |
| spear_thunder | 번개 창 | spear | T3 | 희귀 | swift | 6.31 | spear_silver | 은에서 진화(분기 A) | tradable |
| spear_holy | 성광 창 | spear | T3 | 희귀 | balanced | 6.8 | spear_silver | 은에서 진화(분기 B) | tradable |
| spear_venom | 맹독 창 | spear | T3 | 희귀 | balanced | 6.8 | - | 보스 재료 교환(독 계열 보스) | tradable |
| spear_shadow | 그림자 창 | spear | T3 | 희귀 | swift | 6.31 | - | 보스 재료 교환(그림자 계열 보스) | tradable |
| spear_lava | 용암 창 | spear | T4 | 영웅 | balanced | 6.8 | spear_flame | 불꽃에서 진화(보스 재료) | bind_on_acquire |
| spear_glacier | 빙하 창 | spear | T4 | 영웅 | balanced | 6.8 | spear_frost | 서리에서 진화(보스 재료) | bind_on_acquire |
| spear_storm | 폭풍 창 | spear | T4 | 영웅 | swift | 6.31 | spear_thunder | 번개에서 진화(보스 재료) | bind_on_acquire |
| spear_heaven | 천상 창 | spear | T4 | 영웅 | balanced | 6.8 | spear_holy | 성광에서 진화(보스 재료) | bind_on_acquire |
| spear_corrosion | 부식 창 | spear | T4 | 영웅 | heavy | 7.77 | spear_venom | 맹독에서 진화(보스 재료) | bind_on_acquire |
| spear_dark | 암흑 창 | spear | T4 | 영웅 | swift | 6.31 | spear_shadow | 그림자에서 진화(보스 재료) | bind_on_acquire |
| spear_dragon | 화룡 창 | spear | T5 | 전설 | heavy | 7.77 | spear_lava | 용암에서 진화(최상급 보스 재료) | bind_on_acquire |
| spear_polar | 극한 창 | spear | T5 | 전설 | balanced | 6.8 | spear_glacier | 빙하에서 진화(최상급 보스 재료) | bind_on_acquire |
| spear_skybolt | 천뢰 창 | spear | T5 | 전설 | swift | 6.31 | spear_storm | 폭풍에서 진화(최상급 보스 재료) | bind_on_acquire |
| spear_divine | 신성 창 | spear | T5 | 전설 | balanced | 6.8 | spear_heaven | 천상에서 진화(최상급 보스 재료) | bind_on_acquire |
| spear_plague | 역병 창 | spear | T5 | 전설 | balanced | 6.8 | spear_corrosion | 부식에서 진화(최상급 보스 재료) | bind_on_acquire |
| spear_abyss | 심연 창 | spear | T5 | 전설 | swift | 6.31 | spear_dark | 암흑에서 진화(최상급 보스 재료) | bind_on_acquire |
| axe_wood | 목제 도끼 | axe | T0 | 시작 | swift | 7.87 | - | 시작 무기 선택(최초 접속 1회, starter.json 후보 중 1개) | bind_on_acquire |
| axe_iron | 철 도끼 | axe | T1 | 일반 | balanced | 8.8 | axe_wood | 상점(기본) 또는 목제에서 진화 | tradable |
| axe_bronze | 청동 도끼 | axe | T1 | 일반 | heavy | 10.19 | axe_wood | 상점(기본) 또는 목제에서 진화 | tradable |
| axe_steel | 강철 도끼 | axe | T2 | 고급 | swift | 7.87 | axe_iron | 상점(직업 레벨/도감 조건) 또는 철에서 진화 | tradable |
| axe_silver | 은 도끼 | axe | T2 | 고급 | swift | 7.87 | axe_bronze | 상점(직업 레벨/도감 조건) 또는 청동에서 진화 | tradable |
| axe_flame | 불꽃 도끼 | axe | T3 | 희귀 | heavy | 10.19 | axe_steel | 강철에서 진화(분기 A) | tradable |
| axe_frost | 서리 도끼 | axe | T3 | 희귀 | heavy | 10.19 | axe_steel | 강철에서 진화(분기 B) | tradable |
| axe_thunder | 번개 도끼 | axe | T3 | 희귀 | swift | 7.87 | axe_silver | 은에서 진화(분기 A) | tradable |
| axe_holy | 성광 도끼 | axe | T3 | 희귀 | balanced | 8.8 | axe_silver | 은에서 진화(분기 B) | tradable |
| axe_venom | 맹독 도끼 | axe | T3 | 희귀 | balanced | 8.8 | - | 보스 재료 교환(독 계열 보스) | tradable |
| axe_shadow | 그림자 도끼 | axe | T3 | 희귀 | swift | 7.87 | - | 보스 재료 교환(그림자 계열 보스) | tradable |
| axe_lava | 용암 도끼 | axe | T4 | 영웅 | heavy | 10.19 | axe_flame | 불꽃에서 진화(보스 재료) | bind_on_acquire |
| axe_glacier | 빙하 도끼 | axe | T4 | 영웅 | swift | 7.87 | axe_frost | 서리에서 진화(보스 재료) | bind_on_acquire |
| axe_storm | 폭풍 도끼 | axe | T4 | 영웅 | heavy | 10.19 | axe_thunder | 번개에서 진화(보스 재료) | bind_on_acquire |
| axe_heaven | 천상 도끼 | axe | T4 | 영웅 | balanced | 8.8 | axe_holy | 성광에서 진화(보스 재료) | bind_on_acquire |
| axe_corrosion | 부식 도끼 | axe | T4 | 영웅 | balanced | 8.8 | axe_venom | 맹독에서 진화(보스 재료) | bind_on_acquire |
| axe_dark | 암흑 도끼 | axe | T4 | 영웅 | swift | 7.87 | axe_shadow | 그림자에서 진화(보스 재료) | bind_on_acquire |
| axe_dragon | 화룡 도끼 | axe | T5 | 전설 | heavy | 10.19 | axe_lava | 용암에서 진화(최상급 보스 재료) | bind_on_acquire |
| axe_polar | 극한 도끼 | axe | T5 | 전설 | balanced | 8.8 | axe_glacier | 빙하에서 진화(최상급 보스 재료) | bind_on_acquire |
| axe_skybolt | 천뢰 도끼 | axe | T5 | 전설 | swift | 7.87 | axe_storm | 폭풍에서 진화(최상급 보스 재료) | bind_on_acquire |
| axe_divine | 신성 도끼 | axe | T5 | 전설 | balanced | 8.8 | axe_heaven | 천상에서 진화(최상급 보스 재료) | bind_on_acquire |
| axe_plague | 역병 도끼 | axe | T5 | 전설 | heavy | 10.19 | axe_corrosion | 부식에서 진화(최상급 보스 재료) | bind_on_acquire |
| axe_abyss | 심연 도끼 | axe | T5 | 전설 | swift | 7.87 | axe_dark | 암흑에서 진화(최상급 보스 재료) | bind_on_acquire |
| rapier_wood | 목제 레이피어 | rapier | T0 | 시작 | balanced | 3.99 | - | 시작 무기 선택(최초 접속 1회, starter.json 후보 중 1개) | bind_on_acquire |
| rapier_iron | 철 레이피어 | rapier | T1 | 일반 | balanced | 3.99 | rapier_wood | 상점(기본) 또는 목제에서 진화 | tradable |
| rapier_bronze | 청동 레이피어 | rapier | T1 | 일반 | heavy | 4.56 | rapier_wood | 상점(기본) 또는 목제에서 진화 | tradable |
| rapier_steel | 강철 레이피어 | rapier | T2 | 고급 | balanced | 3.99 | rapier_iron | 상점(직업 레벨/도감 조건) 또는 철에서 진화 | tradable |
| rapier_silver | 은 레이피어 | rapier | T2 | 고급 | swift | 3.56 | rapier_bronze | 상점(직업 레벨/도감 조건) 또는 청동에서 진화 | tradable |
| rapier_flame | 불꽃 레이피어 | rapier | T3 | 희귀 | balanced | 3.99 | rapier_steel | 강철에서 진화(분기 A) | tradable |
| rapier_frost | 서리 레이피어 | rapier | T3 | 희귀 | swift | 3.56 | rapier_steel | 강철에서 진화(분기 B) | tradable |
| rapier_thunder | 번개 레이피어 | rapier | T3 | 희귀 | swift | 3.56 | rapier_silver | 은에서 진화(분기 A) | tradable |
| rapier_holy | 성광 레이피어 | rapier | T3 | 희귀 | balanced | 3.99 | rapier_silver | 은에서 진화(분기 B) | tradable |
| rapier_venom | 맹독 레이피어 | rapier | T3 | 희귀 | balanced | 3.99 | - | 보스 재료 교환(독 계열 보스) | tradable |
| rapier_shadow | 그림자 레이피어 | rapier | T3 | 희귀 | heavy | 4.56 | - | 보스 재료 교환(그림자 계열 보스) | tradable |
| rapier_lava | 용암 레이피어 | rapier | T4 | 영웅 | balanced | 3.99 | rapier_flame | 불꽃에서 진화(보스 재료) | bind_on_acquire |
| rapier_glacier | 빙하 레이피어 | rapier | T4 | 영웅 | swift | 3.56 | rapier_frost | 서리에서 진화(보스 재료) | bind_on_acquire |
| rapier_storm | 폭풍 레이피어 | rapier | T4 | 영웅 | swift | 3.56 | rapier_thunder | 번개에서 진화(보스 재료) | bind_on_acquire |
| rapier_heaven | 천상 레이피어 | rapier | T4 | 영웅 | balanced | 3.99 | rapier_holy | 성광에서 진화(보스 재료) | bind_on_acquire |
| rapier_corrosion | 부식 레이피어 | rapier | T4 | 영웅 | heavy | 4.56 | rapier_venom | 맹독에서 진화(보스 재료) | bind_on_acquire |
| rapier_dark | 암흑 레이피어 | rapier | T4 | 영웅 | swift | 3.56 | rapier_shadow | 그림자에서 진화(보스 재료) | bind_on_acquire |
| rapier_dragon | 화룡 레이피어 | rapier | T5 | 전설 | heavy | 4.56 | rapier_lava | 용암에서 진화(최상급 보스 재료) | bind_on_acquire |
| rapier_polar | 극한 레이피어 | rapier | T5 | 전설 | balanced | 3.99 | rapier_glacier | 빙하에서 진화(최상급 보스 재료) | bind_on_acquire |
| rapier_skybolt | 천뢰 레이피어 | rapier | T5 | 전설 | heavy | 4.56 | rapier_storm | 폭풍에서 진화(최상급 보스 재료) | bind_on_acquire |
| rapier_divine | 신성 레이피어 | rapier | T5 | 전설 | balanced | 3.99 | rapier_heaven | 천상에서 진화(최상급 보스 재료) | bind_on_acquire |
| rapier_plague | 역병 레이피어 | rapier | T5 | 전설 | heavy | 4.56 | rapier_corrosion | 부식에서 진화(최상급 보스 재료) | bind_on_acquire |
| rapier_abyss | 심연 레이피어 | rapier | T5 | 전설 | swift | 3.56 | rapier_dark | 암흑에서 진화(최상급 보스 재료) | bind_on_acquire |
| saber_wood | 목제 곡도 | saber | T0 | 시작 | balanced | 5.01 | - | 시작 무기 선택(최초 접속 1회, starter.json 후보 중 1개) | bind_on_acquire |
| saber_iron | 철 곡도 | saber | T1 | 일반 | balanced | 5.01 | saber_wood | 상점(기본) 또는 목제에서 진화 | tradable |
| saber_bronze | 청동 곡도 | saber | T1 | 일반 | heavy | 5.64 | saber_wood | 상점(기본) 또는 목제에서 진화 | tradable |
| saber_steel | 강철 곡도 | saber | T2 | 고급 | balanced | 5.01 | saber_iron | 상점(직업 레벨/도감 조건) 또는 철에서 진화 | tradable |
| saber_silver | 은 곡도 | saber | T2 | 고급 | swift | 4.54 | saber_bronze | 상점(직업 레벨/도감 조건) 또는 청동에서 진화 | tradable |
| saber_flame | 불꽃 곡도 | saber | T3 | 희귀 | heavy | 5.64 | saber_steel | 강철에서 진화(분기 A) | tradable |
| saber_frost | 서리 곡도 | saber | T3 | 희귀 | swift | 4.54 | saber_steel | 강철에서 진화(분기 B) | tradable |
| saber_thunder | 번개 곡도 | saber | T3 | 희귀 | swift | 4.54 | saber_silver | 은에서 진화(분기 A) | tradable |
| saber_holy | 성광 곡도 | saber | T3 | 희귀 | balanced | 5.01 | saber_silver | 은에서 진화(분기 B) | tradable |
| saber_venom | 맹독 곡도 | saber | T3 | 희귀 | balanced | 5.01 | - | 보스 재료 교환(독 계열 보스) | tradable |
| saber_shadow | 그림자 곡도 | saber | T3 | 희귀 | swift | 4.54 | - | 보스 재료 교환(그림자 계열 보스) | tradable |
| saber_lava | 용암 곡도 | saber | T4 | 영웅 | heavy | 5.64 | saber_flame | 불꽃에서 진화(보스 재료) | bind_on_acquire |
| saber_glacier | 빙하 곡도 | saber | T4 | 영웅 | balanced | 5.01 | saber_frost | 서리에서 진화(보스 재료) | bind_on_acquire |
| saber_storm | 폭풍 곡도 | saber | T4 | 영웅 | swift | 4.54 | saber_thunder | 번개에서 진화(보스 재료) | bind_on_acquire |
| saber_heaven | 천상 곡도 | saber | T4 | 영웅 | balanced | 5.01 | saber_holy | 성광에서 진화(보스 재료) | bind_on_acquire |
| saber_corrosion | 부식 곡도 | saber | T4 | 영웅 | heavy | 5.64 | saber_venom | 맹독에서 진화(보스 재료) | bind_on_acquire |
| saber_dark | 암흑 곡도 | saber | T4 | 영웅 | swift | 4.54 | saber_shadow | 그림자에서 진화(보스 재료) | bind_on_acquire |
| saber_dragon | 화룡 곡도 | saber | T5 | 전설 | heavy | 5.64 | saber_lava | 용암에서 진화(최상급 보스 재료) | bind_on_acquire |
| saber_polar | 극한 곡도 | saber | T5 | 전설 | balanced | 5.01 | saber_glacier | 빙하에서 진화(최상급 보스 재료) | bind_on_acquire |
| saber_skybolt | 천뢰 곡도 | saber | T5 | 전설 | swift | 4.54 | saber_storm | 폭풍에서 진화(최상급 보스 재료) | bind_on_acquire |
| saber_divine | 신성 곡도 | saber | T5 | 전설 | swift | 4.54 | saber_heaven | 천상에서 진화(최상급 보스 재료) | bind_on_acquire |
| saber_plague | 역병 곡도 | saber | T5 | 전설 | balanced | 5.01 | saber_corrosion | 부식에서 진화(최상급 보스 재료) | bind_on_acquire |
| saber_abyss | 심연 곡도 | saber | T5 | 전설 | swift | 4.54 | saber_dark | 암흑에서 진화(최상급 보스 재료) | bind_on_acquire |
| katana_wood | 목제 카타나 | katana | T0 | 시작 | balanced | 5.27 | - | 시작 무기 선택(최초 접속 1회, starter.json 후보 중 1개) | bind_on_acquire |
| katana_iron | 철 카타나 | katana | T1 | 일반 | balanced | 5.27 | katana_wood | 상점(기본) 또는 목제에서 진화 | tradable |
| katana_bronze | 청동 카타나 | katana | T1 | 일반 | heavy | 6.1 | katana_wood | 상점(기본) 또는 목제에서 진화 | tradable |
| katana_steel | 강철 카타나 | katana | T2 | 고급 | balanced | 5.27 | katana_iron | 상점(직업 레벨/도감 조건) 또는 철에서 진화 | tradable |
| katana_silver | 은 카타나 | katana | T2 | 고급 | swift | 4.72 | katana_bronze | 상점(직업 레벨/도감 조건) 또는 청동에서 진화 | tradable |
| katana_flame | 불꽃 카타나 | katana | T3 | 희귀 | heavy | 6.1 | katana_steel | 강철에서 진화(분기 A) | tradable |
| katana_frost | 서리 카타나 | katana | T3 | 희귀 | swift | 4.72 | katana_steel | 강철에서 진화(분기 B) | tradable |
| katana_thunder | 번개 카타나 | katana | T3 | 희귀 | heavy | 6.1 | katana_silver | 은에서 진화(분기 A) | tradable |
| katana_holy | 성광 카타나 | katana | T3 | 희귀 | swift | 4.72 | katana_silver | 은에서 진화(분기 B) | tradable |
| katana_venom | 맹독 카타나 | katana | T3 | 희귀 | balanced | 5.27 | - | 보스 재료 교환(독 계열 보스) | tradable |
| katana_shadow | 그림자 카타나 | katana | T3 | 희귀 | swift | 4.72 | - | 보스 재료 교환(그림자 계열 보스) | tradable |
| katana_lava | 용암 카타나 | katana | T4 | 영웅 | heavy | 6.1 | katana_flame | 불꽃에서 진화(보스 재료) | bind_on_acquire |
| katana_glacier | 빙하 카타나 | katana | T4 | 영웅 | balanced | 5.27 | katana_frost | 서리에서 진화(보스 재료) | bind_on_acquire |
| katana_storm | 폭풍 카타나 | katana | T4 | 영웅 | heavy | 6.1 | katana_thunder | 번개에서 진화(보스 재료) | bind_on_acquire |
| katana_heaven | 천상 카타나 | katana | T4 | 영웅 | swift | 4.72 | katana_holy | 성광에서 진화(보스 재료) | bind_on_acquire |
| katana_corrosion | 부식 카타나 | katana | T4 | 영웅 | heavy | 6.1 | katana_venom | 맹독에서 진화(보스 재료) | bind_on_acquire |
| katana_dark | 암흑 카타나 | katana | T4 | 영웅 | heavy | 6.1 | katana_shadow | 그림자에서 진화(보스 재료) | bind_on_acquire |
| katana_dragon | 화룡 카타나 | katana | T5 | 전설 | heavy | 6.1 | katana_lava | 용암에서 진화(최상급 보스 재료) | bind_on_acquire |
| katana_polar | 극한 카타나 | katana | T5 | 전설 | swift | 4.72 | katana_glacier | 빙하에서 진화(최상급 보스 재료) | bind_on_acquire |
| katana_skybolt | 천뢰 카타나 | katana | T5 | 전설 | swift | 4.72 | katana_storm | 폭풍에서 진화(최상급 보스 재료) | bind_on_acquire |
| katana_divine | 신성 카타나 | katana | T5 | 전설 | balanced | 5.27 | katana_heaven | 천상에서 진화(최상급 보스 재료) | bind_on_acquire |
| katana_plague | 역병 카타나 | katana | T5 | 전설 | heavy | 6.1 | katana_corrosion | 부식에서 진화(최상급 보스 재료) | bind_on_acquire |
| katana_abyss | 심연 카타나 | katana | T5 | 전설 | swift | 4.72 | katana_dark | 암흑에서 진화(최상급 보스 재료) | bind_on_acquire |
| hammer_wood | 목제 해머 | hammer | T0 | 시작 | balanced | 11.35 | - | 시작 무기 선택(최초 접속 1회, starter.json 후보 중 1개) | bind_on_acquire |
| hammer_iron | 철 해머 | hammer | T1 | 일반 | swift | 10.21 | hammer_wood | 상점(기본) 또는 목제에서 진화 | tradable |
| hammer_bronze | 청동 해머 | hammer | T1 | 일반 | heavy | 13.05 | hammer_wood | 상점(기본) 또는 목제에서 진화 | tradable |
| hammer_steel | 강철 해머 | hammer | T2 | 고급 | swift | 10.21 | hammer_iron | 상점(직업 레벨/도감 조건) 또는 철에서 진화 | tradable |
| hammer_silver | 은 해머 | hammer | T2 | 고급 | swift | 10.21 | hammer_bronze | 상점(직업 레벨/도감 조건) 또는 청동에서 진화 | tradable |
| hammer_flame | 불꽃 해머 | hammer | T3 | 희귀 | balanced | 11.35 | hammer_steel | 강철에서 진화(분기 A) | tradable |
| hammer_frost | 서리 해머 | hammer | T3 | 희귀 | heavy | 13.05 | hammer_steel | 강철에서 진화(분기 B) | tradable |
| hammer_thunder | 번개 해머 | hammer | T3 | 희귀 | swift | 10.21 | hammer_silver | 은에서 진화(분기 A) | tradable |
| hammer_holy | 성광 해머 | hammer | T3 | 희귀 | balanced | 11.35 | hammer_silver | 은에서 진화(분기 B) | tradable |
| hammer_venom | 맹독 해머 | hammer | T3 | 희귀 | balanced | 11.35 | - | 보스 재료 교환(독 계열 보스) | tradable |
| hammer_shadow | 그림자 해머 | hammer | T3 | 희귀 | heavy | 13.05 | - | 보스 재료 교환(그림자 계열 보스) | tradable |
| hammer_lava | 용암 해머 | hammer | T4 | 영웅 | balanced | 11.35 | hammer_flame | 불꽃에서 진화(보스 재료) | bind_on_acquire |
| hammer_glacier | 빙하 해머 | hammer | T4 | 영웅 | balanced | 11.35 | hammer_frost | 서리에서 진화(보스 재료) | bind_on_acquire |
| hammer_storm | 폭풍 해머 | hammer | T4 | 영웅 | swift | 10.21 | hammer_thunder | 번개에서 진화(보스 재료) | bind_on_acquire |
| hammer_heaven | 천상 해머 | hammer | T4 | 영웅 | balanced | 11.35 | hammer_holy | 성광에서 진화(보스 재료) | bind_on_acquire |
| hammer_corrosion | 부식 해머 | hammer | T4 | 영웅 | heavy | 13.05 | hammer_venom | 맹독에서 진화(보스 재료) | bind_on_acquire |
| hammer_dark | 암흑 해머 | hammer | T4 | 영웅 | swift | 10.21 | hammer_shadow | 그림자에서 진화(보스 재료) | bind_on_acquire |
| hammer_dragon | 화룡 해머 | hammer | T5 | 전설 | heavy | 13.05 | hammer_lava | 용암에서 진화(최상급 보스 재료) | bind_on_acquire |
| hammer_polar | 극한 해머 | hammer | T5 | 전설 | balanced | 11.35 | hammer_glacier | 빙하에서 진화(최상급 보스 재료) | bind_on_acquire |
| hammer_skybolt | 천뢰 해머 | hammer | T5 | 전설 | swift | 10.21 | hammer_storm | 폭풍에서 진화(최상급 보스 재료) | bind_on_acquire |
| hammer_divine | 신성 해머 | hammer | T5 | 전설 | balanced | 11.35 | hammer_heaven | 천상에서 진화(최상급 보스 재료) | bind_on_acquire |
| hammer_plague | 역병 해머 | hammer | T5 | 전설 | heavy | 13.05 | hammer_corrosion | 부식에서 진화(최상급 보스 재료) | bind_on_acquire |
| hammer_abyss | 심연 해머 | hammer | T5 | 전설 | swift | 10.21 | hammer_dark | 암흑에서 진화(최상급 보스 재료) | bind_on_acquire |
| mace_wood | 목제 메이스 | mace | T0 | 시작 | balanced | 7.27 | - | 시작 무기 선택(최초 접속 1회, starter.json 후보 중 1개) | bind_on_acquire |
| mace_iron | 철 메이스 | mace | T1 | 일반 | balanced | 7.27 | mace_wood | 상점(기본) 또는 목제에서 진화 | tradable |
| mace_bronze | 청동 메이스 | mace | T1 | 일반 | balanced | 7.27 | mace_wood | 상점(기본) 또는 목제에서 진화 | tradable |
| mace_steel | 강철 메이스 | mace | T2 | 고급 | balanced | 7.27 | mace_iron | 상점(직업 레벨/도감 조건) 또는 철에서 진화 | tradable |
| mace_silver | 은 메이스 | mace | T2 | 고급 | swift | 6.66 | mace_bronze | 상점(직업 레벨/도감 조건) 또는 청동에서 진화 | tradable |
| mace_flame | 불꽃 메이스 | mace | T3 | 희귀 | heavy | 8.33 | mace_steel | 강철에서 진화(분기 A) | tradable |
| mace_frost | 서리 메이스 | mace | T3 | 희귀 | swift | 6.66 | mace_steel | 강철에서 진화(분기 B) | tradable |
| mace_thunder | 번개 메이스 | mace | T3 | 희귀 | swift | 6.66 | mace_silver | 은에서 진화(분기 A) | tradable |
| mace_holy | 성광 메이스 | mace | T3 | 희귀 | swift | 6.66 | mace_silver | 은에서 진화(분기 B) | tradable |
| mace_venom | 맹독 메이스 | mace | T3 | 희귀 | balanced | 7.27 | - | 보스 재료 교환(독 계열 보스) | tradable |
| mace_shadow | 그림자 메이스 | mace | T3 | 희귀 | heavy | 8.33 | - | 보스 재료 교환(그림자 계열 보스) | tradable |
| mace_lava | 용암 메이스 | mace | T4 | 영웅 | heavy | 8.33 | mace_flame | 불꽃에서 진화(보스 재료) | bind_on_acquire |
| mace_glacier | 빙하 메이스 | mace | T4 | 영웅 | balanced | 7.27 | mace_frost | 서리에서 진화(보스 재료) | bind_on_acquire |
| mace_storm | 폭풍 메이스 | mace | T4 | 영웅 | swift | 6.66 | mace_thunder | 번개에서 진화(보스 재료) | bind_on_acquire |
| mace_heaven | 천상 메이스 | mace | T4 | 영웅 | swift | 6.66 | mace_holy | 성광에서 진화(보스 재료) | bind_on_acquire |
| mace_corrosion | 부식 메이스 | mace | T4 | 영웅 | heavy | 8.33 | mace_venom | 맹독에서 진화(보스 재료) | bind_on_acquire |
| mace_dark | 암흑 메이스 | mace | T4 | 영웅 | swift | 6.66 | mace_shadow | 그림자에서 진화(보스 재료) | bind_on_acquire |
| mace_dragon | 화룡 메이스 | mace | T5 | 전설 | heavy | 8.33 | mace_lava | 용암에서 진화(최상급 보스 재료) | bind_on_acquire |
| mace_polar | 극한 메이스 | mace | T5 | 전설 | balanced | 7.27 | mace_glacier | 빙하에서 진화(최상급 보스 재료) | bind_on_acquire |
| mace_skybolt | 천뢰 메이스 | mace | T5 | 전설 | swift | 6.66 | mace_storm | 폭풍에서 진화(최상급 보스 재료) | bind_on_acquire |
| mace_divine | 신성 메이스 | mace | T5 | 전설 | balanced | 7.27 | mace_heaven | 천상에서 진화(최상급 보스 재료) | bind_on_acquire |
| mace_plague | 역병 메이스 | mace | T5 | 전설 | balanced | 7.27 | mace_corrosion | 부식에서 진화(최상급 보스 재료) | bind_on_acquire |
| mace_abyss | 심연 메이스 | mace | T5 | 전설 | swift | 6.66 | mace_dark | 암흑에서 진화(최상급 보스 재료) | bind_on_acquire |
| halberd_wood | 목제 할버드 | halberd | T0 | 시작 | balanced | 8.7 | - | 시작 무기 선택(최초 접속 1회, starter.json 후보 중 1개) | bind_on_acquire |
| halberd_iron | 철 할버드 | halberd | T1 | 일반 | balanced | 8.7 | halberd_wood | 상점(기본) 또는 목제에서 진화 | tradable |
| halberd_bronze | 청동 할버드 | halberd | T1 | 일반 | heavy | 10.0 | halberd_wood | 상점(기본) 또는 목제에서 진화 | tradable |
| halberd_steel | 강철 할버드 | halberd | T2 | 고급 | balanced | 8.7 | halberd_iron | 상점(직업 레벨/도감 조건) 또는 철에서 진화 | tradable |
| halberd_silver | 은 할버드 | halberd | T2 | 고급 | swift | 7.83 | halberd_bronze | 상점(직업 레벨/도감 조건) 또는 청동에서 진화 | tradable |
| halberd_flame | 불꽃 할버드 | halberd | T3 | 희귀 | balanced | 8.7 | halberd_steel | 강철에서 진화(분기 A) | tradable |
| halberd_frost | 서리 할버드 | halberd | T3 | 희귀 | swift | 7.83 | halberd_steel | 강철에서 진화(분기 B) | tradable |
| halberd_thunder | 번개 할버드 | halberd | T3 | 희귀 | swift | 7.83 | halberd_silver | 은에서 진화(분기 A) | tradable |
| halberd_holy | 성광 할버드 | halberd | T3 | 희귀 | balanced | 8.7 | halberd_silver | 은에서 진화(분기 B) | tradable |
| halberd_venom | 맹독 할버드 | halberd | T3 | 희귀 | balanced | 8.7 | - | 보스 재료 교환(독 계열 보스) | tradable |
| halberd_shadow | 그림자 할버드 | halberd | T3 | 희귀 | swift | 7.83 | - | 보스 재료 교환(그림자 계열 보스) | tradable |
| halberd_lava | 용암 할버드 | halberd | T4 | 영웅 | heavy | 10.0 | halberd_flame | 불꽃에서 진화(보스 재료) | bind_on_acquire |
| halberd_glacier | 빙하 할버드 | halberd | T4 | 영웅 | swift | 7.83 | halberd_frost | 서리에서 진화(보스 재료) | bind_on_acquire |
| halberd_storm | 폭풍 할버드 | halberd | T4 | 영웅 | swift | 7.83 | halberd_thunder | 번개에서 진화(보스 재료) | bind_on_acquire |
| halberd_heaven | 천상 할버드 | halberd | T4 | 영웅 | balanced | 8.7 | halberd_holy | 성광에서 진화(보스 재료) | bind_on_acquire |
| halberd_corrosion | 부식 할버드 | halberd | T4 | 영웅 | heavy | 10.0 | halberd_venom | 맹독에서 진화(보스 재료) | bind_on_acquire |
| halberd_dark | 암흑 할버드 | halberd | T4 | 영웅 | swift | 7.83 | halberd_shadow | 그림자에서 진화(보스 재료) | bind_on_acquire |
| halberd_dragon | 화룡 할버드 | halberd | T5 | 전설 | heavy | 10.0 | halberd_lava | 용암에서 진화(최상급 보스 재료) | bind_on_acquire |
| halberd_polar | 극한 할버드 | halberd | T5 | 전설 | balanced | 8.7 | halberd_glacier | 빙하에서 진화(최상급 보스 재료) | bind_on_acquire |
| halberd_skybolt | 천뢰 할버드 | halberd | T5 | 전설 | swift | 7.83 | halberd_storm | 폭풍에서 진화(최상급 보스 재료) | bind_on_acquire |
| halberd_divine | 신성 할버드 | halberd | T5 | 전설 | balanced | 8.7 | halberd_heaven | 천상에서 진화(최상급 보스 재료) | bind_on_acquire |
| halberd_plague | 역병 할버드 | halberd | T5 | 전설 | heavy | 10.0 | halberd_corrosion | 부식에서 진화(최상급 보스 재료) | bind_on_acquire |
| halberd_abyss | 심연 할버드 | halberd | T5 | 전설 | heavy | 10.0 | halberd_dark | 암흑에서 진화(최상급 보스 재료) | bind_on_acquire |
| dual_dagger_wood | 목제 쌍단검 | dual_dagger | T0 | 시작 | balanced | 3.37 | - | 시작 무기 선택(최초 접속 1회, starter.json 후보 중 1개) | bind_on_acquire |
| dual_dagger_iron | 철 쌍단검 | dual_dagger | T1 | 일반 | balanced | 3.37 | dual_dagger_wood | 상점(기본) 또는 목제에서 진화 | tradable |
| dual_dagger_bronze | 청동 쌍단검 | dual_dagger | T1 | 일반 | heavy | 4.0 | dual_dagger_wood | 상점(기본) 또는 목제에서 진화 | tradable |
| dual_dagger_steel | 강철 쌍단검 | dual_dagger | T2 | 고급 | swift | 2.84 | dual_dagger_iron | 상점(직업 레벨/도감 조건) 또는 철에서 진화 | tradable |
| dual_dagger_silver | 은 쌍단검 | dual_dagger | T2 | 고급 | heavy | 4.0 | dual_dagger_bronze | 상점(직업 레벨/도감 조건) 또는 청동에서 진화 | tradable |
| dual_dagger_flame | 불꽃 쌍단검 | dual_dagger | T3 | 희귀 | heavy | 4.0 | dual_dagger_steel | 강철에서 진화(분기 A) | tradable |
| dual_dagger_frost | 서리 쌍단검 | dual_dagger | T3 | 희귀 | swift | 2.84 | dual_dagger_steel | 강철에서 진화(분기 B) | tradable |
| dual_dagger_thunder | 번개 쌍단검 | dual_dagger | T3 | 희귀 | swift | 2.84 | dual_dagger_silver | 은에서 진화(분기 A) | tradable |
| dual_dagger_holy | 성광 쌍단검 | dual_dagger | T3 | 희귀 | balanced | 3.37 | dual_dagger_silver | 은에서 진화(분기 B) | tradable |
| dual_dagger_venom | 맹독 쌍단검 | dual_dagger | T3 | 희귀 | balanced | 3.37 | - | 보스 재료 교환(독 계열 보스) | tradable |
| dual_dagger_shadow | 그림자 쌍단검 | dual_dagger | T3 | 희귀 | swift | 2.84 | - | 보스 재료 교환(그림자 계열 보스) | tradable |
| dual_dagger_lava | 용암 쌍단검 | dual_dagger | T4 | 영웅 | heavy | 4.0 | dual_dagger_flame | 불꽃에서 진화(보스 재료) | bind_on_acquire |
| dual_dagger_glacier | 빙하 쌍단검 | dual_dagger | T4 | 영웅 | swift | 2.84 | dual_dagger_frost | 서리에서 진화(보스 재료) | bind_on_acquire |
| dual_dagger_storm | 폭풍 쌍단검 | dual_dagger | T4 | 영웅 | swift | 2.84 | dual_dagger_thunder | 번개에서 진화(보스 재료) | bind_on_acquire |
| dual_dagger_heaven | 천상 쌍단검 | dual_dagger | T4 | 영웅 | swift | 2.84 | dual_dagger_holy | 성광에서 진화(보스 재료) | bind_on_acquire |
| dual_dagger_corrosion | 부식 쌍단검 | dual_dagger | T4 | 영웅 | heavy | 4.0 | dual_dagger_venom | 맹독에서 진화(보스 재료) | bind_on_acquire |
| dual_dagger_dark | 암흑 쌍단검 | dual_dagger | T4 | 영웅 | swift | 2.84 | dual_dagger_shadow | 그림자에서 진화(보스 재료) | bind_on_acquire |
| dual_dagger_dragon | 화룡 쌍단검 | dual_dagger | T5 | 전설 | heavy | 4.0 | dual_dagger_lava | 용암에서 진화(최상급 보스 재료) | bind_on_acquire |
| dual_dagger_polar | 극한 쌍단검 | dual_dagger | T5 | 전설 | swift | 2.84 | dual_dagger_glacier | 빙하에서 진화(최상급 보스 재료) | bind_on_acquire |
| dual_dagger_skybolt | 천뢰 쌍단검 | dual_dagger | T5 | 전설 | swift | 2.84 | dual_dagger_storm | 폭풍에서 진화(최상급 보스 재료) | bind_on_acquire |
| dual_dagger_divine | 신성 쌍단검 | dual_dagger | T5 | 전설 | balanced | 3.37 | dual_dagger_heaven | 천상에서 진화(최상급 보스 재료) | bind_on_acquire |
| dual_dagger_plague | 역병 쌍단검 | dual_dagger | T5 | 전설 | heavy | 4.0 | dual_dagger_corrosion | 부식에서 진화(최상급 보스 재료) | bind_on_acquire |
| dual_dagger_abyss | 심연 쌍단검 | dual_dagger | T5 | 전설 | swift | 2.84 | dual_dagger_dark | 암흑에서 진화(최상급 보스 재료) | bind_on_acquire |
| dual_axe_wood | 목제 쌍도끼 | dual_axe | T0 | 시작 | swift | 7.06 | - | 시작 무기 선택(최초 접속 1회, starter.json 후보 중 1개) | bind_on_acquire |
| dual_axe_iron | 철 쌍도끼 | dual_axe | T1 | 일반 | balanced | 7.94 | dual_axe_wood | 상점(기본) 또는 목제에서 진화 | tradable |
| dual_axe_bronze | 청동 쌍도끼 | dual_axe | T1 | 일반 | heavy | 8.97 | dual_axe_wood | 상점(기본) 또는 목제에서 진화 | tradable |
| dual_axe_steel | 강철 쌍도끼 | dual_axe | T2 | 고급 | balanced | 7.94 | dual_axe_iron | 상점(직업 레벨/도감 조건) 또는 철에서 진화 | tradable |
| dual_axe_silver | 은 쌍도끼 | dual_axe | T2 | 고급 | swift | 7.06 | dual_axe_bronze | 상점(직업 레벨/도감 조건) 또는 청동에서 진화 | tradable |
| dual_axe_flame | 불꽃 쌍도끼 | dual_axe | T3 | 희귀 | heavy | 8.97 | dual_axe_steel | 강철에서 진화(분기 A) | tradable |
| dual_axe_frost | 서리 쌍도끼 | dual_axe | T3 | 희귀 | swift | 7.06 | dual_axe_steel | 강철에서 진화(분기 B) | tradable |
| dual_axe_thunder | 번개 쌍도끼 | dual_axe | T3 | 희귀 | swift | 7.06 | dual_axe_silver | 은에서 진화(분기 A) | tradable |
| dual_axe_holy | 성광 쌍도끼 | dual_axe | T3 | 희귀 | balanced | 7.94 | dual_axe_silver | 은에서 진화(분기 B) | tradable |
| dual_axe_venom | 맹독 쌍도끼 | dual_axe | T3 | 희귀 | balanced | 7.94 | - | 보스 재료 교환(독 계열 보스) | tradable |
| dual_axe_shadow | 그림자 쌍도끼 | dual_axe | T3 | 희귀 | swift | 7.06 | - | 보스 재료 교환(그림자 계열 보스) | tradable |
| dual_axe_lava | 용암 쌍도끼 | dual_axe | T4 | 영웅 | heavy | 8.97 | dual_axe_flame | 불꽃에서 진화(보스 재료) | bind_on_acquire |
| dual_axe_glacier | 빙하 쌍도끼 | dual_axe | T4 | 영웅 | balanced | 7.94 | dual_axe_frost | 서리에서 진화(보스 재료) | bind_on_acquire |
| dual_axe_storm | 폭풍 쌍도끼 | dual_axe | T4 | 영웅 | swift | 7.06 | dual_axe_thunder | 번개에서 진화(보스 재료) | bind_on_acquire |
| dual_axe_heaven | 천상 쌍도끼 | dual_axe | T4 | 영웅 | balanced | 7.94 | dual_axe_holy | 성광에서 진화(보스 재료) | bind_on_acquire |
| dual_axe_corrosion | 부식 쌍도끼 | dual_axe | T4 | 영웅 | heavy | 8.97 | dual_axe_venom | 맹독에서 진화(보스 재료) | bind_on_acquire |
| dual_axe_dark | 암흑 쌍도끼 | dual_axe | T4 | 영웅 | swift | 7.06 | dual_axe_shadow | 그림자에서 진화(보스 재료) | bind_on_acquire |
| dual_axe_dragon | 화룡 쌍도끼 | dual_axe | T5 | 전설 | heavy | 8.97 | dual_axe_lava | 용암에서 진화(최상급 보스 재료) | bind_on_acquire |
| dual_axe_polar | 극한 쌍도끼 | dual_axe | T5 | 전설 | balanced | 7.94 | dual_axe_glacier | 빙하에서 진화(최상급 보스 재료) | bind_on_acquire |
| dual_axe_skybolt | 천뢰 쌍도끼 | dual_axe | T5 | 전설 | heavy | 8.97 | dual_axe_storm | 폭풍에서 진화(최상급 보스 재료) | bind_on_acquire |
| dual_axe_divine | 신성 쌍도끼 | dual_axe | T5 | 전설 | balanced | 7.94 | dual_axe_heaven | 천상에서 진화(최상급 보스 재료) | bind_on_acquire |
| dual_axe_plague | 역병 쌍도끼 | dual_axe | T5 | 전설 | heavy | 8.97 | dual_axe_corrosion | 부식에서 진화(최상급 보스 재료) | bind_on_acquire |
| dual_axe_abyss | 심연 쌍도끼 | dual_axe | T5 | 전설 | swift | 7.06 | dual_axe_dark | 암흑에서 진화(최상급 보스 재료) | bind_on_acquire |
| war_scythe_wood | 목제 대낫 | war_scythe | T0 | 시작 | balanced | 8.2 | - | 시작 무기 선택(최초 접속 1회, starter.json 후보 중 1개) | bind_on_acquire |
| war_scythe_iron | 철 대낫 | war_scythe | T1 | 일반 | balanced | 8.2 | war_scythe_wood | 상점(기본) 또는 목제에서 진화 | tradable |
| war_scythe_bronze | 청동 대낫 | war_scythe | T1 | 일반 | heavy | 9.44 | war_scythe_wood | 상점(기본) 또는 목제에서 진화 | tradable |
| war_scythe_steel | 강철 대낫 | war_scythe | T2 | 고급 | swift | 7.33 | war_scythe_iron | 상점(직업 레벨/도감 조건) 또는 철에서 진화 | tradable |
| war_scythe_silver | 은 대낫 | war_scythe | T2 | 고급 | swift | 7.33 | war_scythe_bronze | 상점(직업 레벨/도감 조건) 또는 청동에서 진화 | tradable |
| war_scythe_flame | 불꽃 대낫 | war_scythe | T3 | 희귀 | heavy | 9.44 | war_scythe_steel | 강철에서 진화(분기 A) | tradable |
| war_scythe_frost | 서리 대낫 | war_scythe | T3 | 희귀 | heavy | 9.44 | war_scythe_steel | 강철에서 진화(분기 B) | tradable |
| war_scythe_thunder | 번개 대낫 | war_scythe | T3 | 희귀 | swift | 7.33 | war_scythe_silver | 은에서 진화(분기 A) | tradable |
| war_scythe_holy | 성광 대낫 | war_scythe | T3 | 희귀 | balanced | 8.2 | war_scythe_silver | 은에서 진화(분기 B) | tradable |
| war_scythe_venom | 맹독 대낫 | war_scythe | T3 | 희귀 | balanced | 8.2 | - | 보스 재료 교환(독 계열 보스) | tradable |
| war_scythe_shadow | 그림자 대낫 | war_scythe | T3 | 희귀 | swift | 7.33 | - | 보스 재료 교환(그림자 계열 보스) | tradable |
| war_scythe_lava | 용암 대낫 | war_scythe | T4 | 영웅 | heavy | 9.44 | war_scythe_flame | 불꽃에서 진화(보스 재료) | bind_on_acquire |
| war_scythe_glacier | 빙하 대낫 | war_scythe | T4 | 영웅 | balanced | 8.2 | war_scythe_frost | 서리에서 진화(보스 재료) | bind_on_acquire |
| war_scythe_storm | 폭풍 대낫 | war_scythe | T4 | 영웅 | swift | 7.33 | war_scythe_thunder | 번개에서 진화(보스 재료) | bind_on_acquire |
| war_scythe_heaven | 천상 대낫 | war_scythe | T4 | 영웅 | swift | 7.33 | war_scythe_holy | 성광에서 진화(보스 재료) | bind_on_acquire |
| war_scythe_corrosion | 부식 대낫 | war_scythe | T4 | 영웅 | heavy | 9.44 | war_scythe_venom | 맹독에서 진화(보스 재료) | bind_on_acquire |
| war_scythe_dark | 암흑 대낫 | war_scythe | T4 | 영웅 | swift | 7.33 | war_scythe_shadow | 그림자에서 진화(보스 재료) | bind_on_acquire |
| war_scythe_dragon | 화룡 대낫 | war_scythe | T5 | 전설 | heavy | 9.44 | war_scythe_lava | 용암에서 진화(최상급 보스 재료) | bind_on_acquire |
| war_scythe_polar | 극한 대낫 | war_scythe | T5 | 전설 | balanced | 8.2 | war_scythe_glacier | 빙하에서 진화(최상급 보스 재료) | bind_on_acquire |
| war_scythe_skybolt | 천뢰 대낫 | war_scythe | T5 | 전설 | swift | 7.33 | war_scythe_storm | 폭풍에서 진화(최상급 보스 재료) | bind_on_acquire |
| war_scythe_divine | 신성 대낫 | war_scythe | T5 | 전설 | balanced | 8.2 | war_scythe_heaven | 천상에서 진화(최상급 보스 재료) | bind_on_acquire |
| war_scythe_plague | 역병 대낫 | war_scythe | T5 | 전설 | balanced | 8.2 | war_scythe_corrosion | 부식에서 진화(최상급 보스 재료) | bind_on_acquire |
| war_scythe_abyss | 심연 대낫 | war_scythe | T5 | 전설 | swift | 7.33 | war_scythe_dark | 암흑에서 진화(최상급 보스 재료) | bind_on_acquire |
| one_hand_sword_unique_new_dawn | 새벽 | one_hand_sword | T4 | 영웅 | balanced | 6.0 | - | 보스 보상(성광 계열) | bind_on_acquire |
| one_hand_sword_unique_starlight | 별빛 | one_hand_sword | T5 | 전설 | swift | 5.45 | - | 도감 마일스톤(검 도감 완성) | bind_on_acquire |
| dagger_unique_fang_of_shadow | 그림자 송곳니 | dagger | T4 | 영웅 | swift | 2.55 | - | 보스 보상(그림자 계열) | bind_on_acquire |
| dual_blade_unique_yaksha | 야차 | dual_blade | T5 | 전설 | swift | 3.47 | - | 최상급 보스 보상 | bind_on_acquire |
| greatsword_unique_paecheon | 파천 | greatsword | T5 | 전설 | heavy | 11.4 | - | 최상급 보스 보상 | bind_on_acquire |
| halberd_unique_blue_dragon_glaive | 청룡언월 | halberd | T5 | 전설 | balanced | 8.7 | - | 시즌 보상 | bind_on_acquire |
| spear_unique_lightning_fall | 낙뢰 | spear | T4 | 영웅 | swift | 6.31 | - | 보스 보상(번개 계열) | bind_on_acquire |
| axe_unique_primal_axe | 태초의 도끼 | axe | T5 | 전설 | heavy | 10.19 | - | 최상급 보스 보상 | bind_on_acquire |
| rapier_unique_white_night | 백야 | rapier | T4 | 영웅 | swift | 3.56 | - | 보스 보상(서리 계열) | bind_on_acquire |
| saber_unique_crimson_blade | 적염 | saber | T4 | 영웅 | balanced | 5.01 | - | 보스 보상(화염 계열) | bind_on_acquire |
| katana_unique_sun_and_moon | 일월 | katana | T5 | 전설 | balanced | 5.27 | - | 시즌 이벤트 | bind_on_acquire |
| hammer_unique_thunder_hammer | 천둥 | hammer | T4 | 영웅 | heavy | 13.05 | - | 보스 보상(번개 계열) | bind_on_acquire |
| mace_unique_vajra | 금강 | mace | T4 | 영웅 | heavy | 8.33 | - | 보스 보상(성광 계열) | bind_on_acquire |
| dual_dagger_unique_twin_stars | 쌍성 | dual_dagger | T5 | 전설 | swift | 2.84 | - | 이벤트(수집) | bind_on_acquire |
| dual_axe_unique_goblin_twins | 도깨비 쌍부 | dual_axe | T5 | 전설 | heavy | 8.97 | - | 최상급 보스 보상 | bind_on_acquire |
| war_scythe_unique_blood_moon | 혈월 | war_scythe | T5 | 전설 | balanced | 8.2 | - | 최상급 보스 보상 | bind_on_acquire |
