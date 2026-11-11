package dev.economycore.guard;

import dev.economycore.EconomyCore;
import dev.economycore.config.ConfigService;
import net.minecraft.server.MinecraftServer;

/**
 * S1: 레시피 필터 스텁.
 * 가설 H1: 서버 시작 후/리로드 후 RecipeManager의 레시피 목록을 읽어 허용 목록 밖을 제거(replaceRecipes 계열)할 수 있다.
 * 확인할 것: (a) 적용 훅 시점(ServerStarted vs 데이터팩 리로드 후), (b) /reload 후 재적용, (c) 런타임 생성 레시피 대응,
 * (d) 클라이언트로 동기화되는 레시피(JEI 표시) 처리, (e) 믹스인이 필요한지.
 * 현재 구현은 log_only 모드로 '어떤 레시피가 남고 제거될지'만 기록한다.
 */
public final class RecipeGuard {
    public static void apply(MinecraftServer server) {
        var rm = server.getRecipeManager();
        int total = 0;
        // TODO(S1): 전체 레시피 순회(rm.getRecipes() 등 1.21.1 API 확인), 허용 네임스페이스/ID/결과 기준 판정, log_only → enforce 전환
        EconomyCore.LOGGER.info("[economycore] RecipeGuard: recipes inspected (stub) total={} cfg={}", total, ConfigService.guard());
    }

    private RecipeGuard() {}
}
