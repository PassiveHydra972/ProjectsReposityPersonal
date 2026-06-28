package xol.abyssalweapons.item;

import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.SwordItem;
import net.minecraft.world.item.Tiers;

/**
 * Saber Claw — 28 dmg. Each attack delivers a rapid second slash for half the damage.
 */
public class SaberClawItem extends SwordItem {

    public SaberClawItem() {
        super(Tiers.NETHERITE,
                new Item.Properties()
                        .stacksTo(1)
                        .attributes(SwordItem.createAttributes(Tiers.NETHERITE, 23, -2.4f))); // 28 dmg
    }

    @Override
    public boolean hurtEnemy(ItemStack stack, LivingEntity target, LivingEntity attacker) {
        boolean result = super.hurtEnemy(stack, target, attacker);
        if (result && !target.level().isClientSide) {
            // Second rapid slash: 14 damage (magic damage so it always lands)
            target.hurt(target.level().damageSources().magic(), 14.0f);
        }
        return result;
    }
}
