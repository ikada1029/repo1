package dev.economycore.command;

import com.mojang.brigadier.CommandDispatcher;
import dev.economycore.config.ConfigService;
import dev.economycore.guard.RecipeGuard;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.network.chat.Component;

/** S10: /economycore reload | status (관리자 전용). S7: 일반 유저 명령 차단은 별도 CommandEvent로 확인한다. */
public final class EconomyCommands {
    public static void register(CommandDispatcher<CommandSourceStack> d) {
        d.register(Commands.literal("economycore")
                .requires(s -> s.hasPermission(2))
                .then(Commands.literal("reload").executes(ctx -> {
                    String r = ConfigService.reload();
                    RecipeGuard.apply(ctx.getSource().getServer());
                    ctx.getSource().sendSuccess(() -> Component.literal("[economycore] reload: " + r), true);
                    return 1;
                }))
                .then(Commands.literal("status").executes(ctx -> {
                    ctx.getSource().sendSuccess(() -> Component.literal("[economycore] OK (C0 skeleton)"), false);
                    return 1;
                })));
    }

    private EconomyCommands() {}
}
