package xol.abyssalweapons.item;

import net.minecraft.network.chat.Component;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Tiers;
import net.minecraft.world.level.Level;

/**
 * Rapier of Revenge — 35 true dmg.
 * Passive: while held at ≤40% HP, the player receives Strength II (handled in AbyssalWeaponsEvents).
 * Right-click: heals 8 HP and grants Speed III for 10 s (60 s cooldown).
 */
public class RapierOfRevengeItem extends TrueDamageSword {

    public RapierOfRevengeItem() {
        super(Tiers.NETHERITE, 35.0f, 1.6f, new Item.Properties().stacksTo(1));
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        if (player.getCooldowns().isOnCooldown(this)) {
            return InteractionResultHolder.pass(player.getItemInHand(hand));
        }
        if (!level.isClientSide) {
            player.heal(8.0f);
            player.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SPEED, 200, 2)); // Speed III, 10 s
            player.getCooldowns().addCooldown(this, 1200); // 60 s
            player.displayClientMessage(Component.literal("\u00a7c\u00bb Vengeance ignites! \u00ab"), true);
        }
        return InteractionResultHolder.sidedSuccess(player.getItemInHand(hand), level.isClientSide);
    }
}
