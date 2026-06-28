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

/** Greatsword of Etherial Selection — 55 true dmg / speed 1.2 / 50-50 buff-or-curse (3 min cooldown) */
public class SwordOfSelectionItem extends TrueDamageSword {

    public SwordOfSelectionItem() {
        super(Tiers.NETHERITE, 55.0f, 1.2f, new Item.Properties().stacksTo(1));
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        if (player.getCooldowns().isOnCooldown(this)) {
            return InteractionResultHolder.pass(player.getItemInHand(hand));
        }
        if (!level.isClientSide) {
            if (level.random.nextBoolean()) {
                // Lucky: Strength 50, Resistance 50, Speed 3, Regen 50 for 120 s
                int d = 120 * 20;
                player.addEffect(new MobEffectInstance(MobEffects.DAMAGE_BOOST,      d, 49));
                player.addEffect(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE, d, 49));
                player.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SPEED,    d, 2));
                player.addEffect(new MobEffectInstance(MobEffects.REGENERATION,      d, 49));
                player.displayClientMessage(Component.literal("\u00a7a\u2605 The blade chooses you! \u2605"), true);
                player.getCooldowns().addCooldown(this, 3600); // Lucky: 3 min cooldown
            } else {
                // Unlucky: Weakness 3, Slowness 3, Hunger 3, Poison 3 for 30 s
                int d = 30 * 20;
                player.addEffect(new MobEffectInstance(MobEffects.WEAKNESS,          d, 2));
                player.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, d, 2));
                player.addEffect(new MobEffectInstance(MobEffects.HUNGER,            d, 2));
                player.addEffect(new MobEffectInstance(MobEffects.POISON,            d, 2));
                player.displayClientMessage(Component.literal("\u00a7c\u2620 The blade rejects you. \u2620"), true);
                player.getCooldowns().addCooldown(this, 1200); // Rejection: 60 s cooldown
            }
        }
        return InteractionResultHolder.sidedSuccess(player.getItemInHand(hand), level.isClientSide);
    }
}
