package dev.economycore.config;

import com.google.gson.Gson;
import com.google.gson.JsonObject;
import dev.economycore.EconomyCore;
import net.neoforged.fml.loading.FMLPaths;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

/** S10: config/economycore/*.json 로더. 핫리로드는 /economycore reload. 기본 파일이 없으면 만들지 않고 비활성 상태로 둔다(스텁). */
public final class ConfigService {
    private static final Gson GSON = new Gson();
    private static volatile JsonObject guard = new JsonObject();

    public static Path dir() {
        return FMLPaths.CONFIGDIR.get().resolve("economycore");
    }

    public static void init() {
        reload();
    }

    public static String reload() {
        try {
            Path f = dir().resolve("economycore-guard.json");
            if (Files.exists(f)) {
                guard = GSON.fromJson(Files.readString(f), JsonObject.class);
                return "guard loaded";
            }
            return "guard file missing (" + f + ")";
        } catch (IOException | RuntimeException e) {
            EconomyCore.LOGGER.error("[economycore] config reload failed", e);
            return "error: " + e.getMessage();
        }
    }

    public static JsonObject guard() {
        return guard;
    }

    private ConfigService() {}
}
