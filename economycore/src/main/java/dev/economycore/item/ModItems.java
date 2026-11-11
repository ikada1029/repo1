package dev.economycore.item;

import dev.economycore.EconomyCore;
import net.minecraft.world.item.Item;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

public final class ModItems {
    public static final DeferredRegister.Items ITEMS = DeferredRegister.createItems(EconomyCore.MOD_ID);

    // S3: 카테고리별 신규 아이템. 무기 종류는 def_id(데이터 컴포넌트)로 구분한다.
    public static final DeferredItem<GearItem> GEAR_SWORD =
            ITEMS.register("gear_sword", () -> new GearItem(new Item.Properties().stacksTo(1).fireResistant()));

    private ModItems() {}
}
