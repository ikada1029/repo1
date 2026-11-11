package dev.economycore.component;

import dev.economycore.EconomyCore;
import net.minecraft.core.component.DataComponentType;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

public final class ModComponents {
    public static final DeferredRegister.DataComponents COMPONENTS = DeferredRegister.createDataComponents(EconomyCore.MOD_ID);

    // S3: LR의 CUSTOM_DATA와 섞지 않고 자체 컴포넌트로 분리한다.
    public static final DeferredHolder<DataComponentType<?>, DataComponentType<GearData>> GEAR =
            COMPONENTS.registerComponentType("gear", b -> b.persistent(GearData.CODEC).networkSynchronized(GearData.STREAM_CODEC));

    private ModComponents() {}
}
