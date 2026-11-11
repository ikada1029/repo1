package dev.economycore.item;

import net.minecraft.world.item.Item;

/**
 * 신규 근접 무기 아이템(S3·S4).
 * - SwordItem을 상속하지 않는다(바닐라 휩쓸기·기본 공격 속성 미적용).
 * - TODO(S4): 바닐라 공격/블록 파괴 차단(canAttackBlock 등)을 확인한다.
 * - TODO(S8): 내구도 개념 없음(damageable 아님) 확인.
 */
public class GearItem extends Item {
    public GearItem(Properties properties) {
        super(properties);
    }
}
