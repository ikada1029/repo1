package dev.economycore;

import dev.economycore.command.EconomyCommands;
import dev.economycore.component.ModComponents;
import dev.economycore.config.ConfigService;
import dev.economycore.guard.RecipeGuard;
import dev.economycore.item.ModItems;
import dev.economycore.net.AttackIntentPayload;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.ModContainer;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.RegisterCommandsEvent;
import net.neoforged.neoforge.event.server.ServerStartedEvent;
import net.neoforged.neoforge.network.event.RegisterPayloadHandlersEvent;
import org.slf4j.Logger;
import com.mojang.logging.LogUtils;

/**
 * C0 스파이크 골격. NeoForge 21.1.x API 이름은 컴파일로 확인한다(미검증 초안).
 * 각 TODO 옆 S번호는 docs/c0-spike-plan.md의 스파이크 항목이다.
 */
@Mod(EconomyCore.MOD_ID)
public final class EconomyCore {
    public static final String MOD_ID = "economycore";
    public static final Logger LOGGER = LogUtils.getLogger();

    public EconomyCore(IEventBus modBus, ModContainer container) {
        ModItems.ITEMS.register(modBus);               // S3
        ModComponents.COMPONENTS.register(modBus);     // S3
        modBus.addListener(this::registerPayloads);    // S4

        NeoForge.EVENT_BUS.addListener(this::onServerStarted);
        NeoForge.EVENT_BUS.addListener(this::onRegisterCommands);

        ConfigService.init();                          // S10
        LOGGER.info("[economycore] loaded");
    }

    private void registerPayloads(RegisterPayloadHandlersEvent event) {
        var registrar = event.registrar("1");
        registrar.playToServer(AttackIntentPayload.TYPE, AttackIntentPayload.STREAM_CODEC, AttackIntentPayload::handle); // S4
    }

    private void onServerStarted(ServerStartedEvent event) {
        RecipeGuard.apply(event.getServer());          // S1 (reload 후 재적용은 S1에서 확인)
    }

    private void onRegisterCommands(RegisterCommandsEvent event) {
        EconomyCommands.register(event.getDispatcher()); // S10
    }
}
