package dev.economycore.component;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;

/** economycore:gear 컴포넌트 값(표시·캐시용, 정본은 DB). S3에서 직렬화·동기화를 확인한다. */
public record GearData(String defId, int enhanceLevel, int tier) {
    public static final Codec<GearData> CODEC = RecordCodecBuilder.create(i -> i.group(
            Codec.STRING.fieldOf("def_id").forGetter(GearData::defId),
            Codec.INT.optionalFieldOf("enhance_level", 0).forGetter(GearData::enhanceLevel),
            Codec.INT.optionalFieldOf("tier", 0).forGetter(GearData::tier)
    ).apply(i, GearData::new));

    public static final StreamCodec<RegistryFriendlyByteBuf, GearData> STREAM_CODEC = StreamCodec.composite(
            ByteBufCodecs.STRING_UTF8, GearData::defId,
            ByteBufCodecs.VAR_INT, GearData::enhanceLevel,
            ByteBufCodecs.VAR_INT, GearData::tier,
            GearData::new);
}
