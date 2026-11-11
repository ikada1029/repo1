package dev.economycore.client;

import dev.economycore.EconomyCore;
import dev.economycore.item.GearItem;
import dev.economycore.net.AttackIntentPayload;
import net.minecraft.client.Minecraft;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.client.event.InputEvent;
import net.neoforged.neoforge.network.PacketDistributor;

/** S4: GearItem을 든 상태의 좌/우 클릭을 바닐라 동작 대신 의도 패킷으로 바꾼다. 클라이언트 전용 클래스. */
@EventBusSubscriber(modid = EconomyCore.MOD_ID, value = Dist.CLIENT)
public final class ClientInput {
    private static int seq = 0;

    @SubscribeEvent
    public static void onInteraction(InputEvent.InteractionKeyMappingTriggered event) {
        var player = Minecraft.getInstance().player;
        if (player == null || !(player.getMainHandItem().getItem() instanceof GearItem)) {
            return;
        }
        if (event.isAttack() || event.isUseItem()) {
            event.setCanceled(true);          // 바닐라 공격/사용 취소 (스윙 연출 여부는 S4에서 결정)
            event.setSwingHand(false);
            PacketDistributor.sendToServer(new AttackIntentPayload(event.isAttack() ? 0 : 1, ++seq));
        }
    }

    private ClientInput() {}
}
