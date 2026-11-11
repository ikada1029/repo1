package dev.economycore.net;

import dev.economycore.EconomyCore;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.ResourceLocation;
import net.neoforged.neoforge.network.handling.IPayloadContext;

/**
 * 공격 의도 패킷(S4): 클라이언트는 '의도'(좌/우, 순번)만 보내고 대상·위치·시선은 보내지 않는다.
 * 서버가 쿨다운·콤보·대상(S5)·피해를 계산한다.
 */
public record AttackIntentPayload(int action, int seq) implements CustomPacketPayload {
    public static final Type<AttackIntentPayload> TYPE =
            new Type<>(ResourceLocation.fromNamespaceAndPath(EconomyCore.MOD_ID, "attack_intent"));
    public static final StreamCodec<RegistryFriendlyByteBuf, AttackIntentPayload> STREAM_CODEC = StreamCodec.composite(
            ByteBufCodecs.VAR_INT, AttackIntentPayload::action,
            ByteBufCodecs.VAR_INT, AttackIntentPayload::seq,
            AttackIntentPayload::new);

    @Override
    public Type<? extends CustomPacketPayload> type() {
        return TYPE;
    }

    public static void handle(AttackIntentPayload payload, IPayloadContext ctx) {
        ctx.enqueueWork(() -> {
            // TODO(S4): seq 단조 증가·레이트 제한 검증, 메인핸드가 GearItem인지 확인
            // TODO(S5): 서버 값(눈 위치·시선)으로 cone 판정 후 피해 적용, delay 틱 스케줄
            EconomyCore.LOGGER.debug("[economycore] attack intent action={} seq={}", payload.action(), payload.seq());
        });
    }
}
