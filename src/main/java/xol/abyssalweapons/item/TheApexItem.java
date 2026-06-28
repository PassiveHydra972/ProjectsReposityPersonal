package xol.abyssalweapons.item;

import net.minecraft.network.chat.Component;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Tiers;

/**
 * The Apex — 60 true dmg.
 * On kill: instantly heal 15 HP, gain Strength IV (8 s) and Speed II (8 s).
 */
public class TheApexItem extends TrueDamageSword {

    public TheApexItem() {
        super(Tiers.NETHERITE, 60.0f, 1.2f, new Item.Properties().stacksTo(1));
    }

    @Override
    public void postTrueDamageHit(ItemStack stack, LivingEntity target, LivingEntity attacker) {
        if (target.isDeadOrDying() && attacker instanceof Player player) {
            player.heal(15.0f);
            player.addEffect(new MobEffectInstance(MobEffects.DAMAGE_BOOST,   160, 3)); // Strength IV, 8 s
            player.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SPEED, 160, 1)); // Speed II, 8 s
            player.displayClientMessage(Component.literal("\u00a76\u00bb Apex predator! \u00ab"), true);
        }
    }
}
