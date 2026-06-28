package xol.abyssalweapons.item;

import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Tiers;

/** Greatsword of Eternal Death And Corruption — 65 true dmg / speed 0.4 / Wither V (7.5 s) on hit */
public class BladeOfDeadItem extends TrueDamageSword {

    /** 7.5 seconds = 150 ticks */
    private static final int WITHER_DURATION = 150;

    public BladeOfDeadItem() {
        super(Tiers.NETHERITE, 65.0f, 0.4f, new Item.Properties().stacksTo(1));
    }

    @Override
    public void postTrueDamageHit(ItemStack stack, LivingEntity target, LivingEntity attacker) {
        // Wither V = amplifier 4
        target.addEffect(new MobEffectInstance(MobEffects.WITHER, WITHER_DURATION, 4));
    }
}
